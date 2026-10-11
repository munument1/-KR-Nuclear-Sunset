"""Resolve all existing translations to current native record paths, without installation."""
from collections import Counter, defaultdict
from copy import deepcopy
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import nskr
import nskr_xedit
from nskr_output import output_catalog, stable_context, original_installation
from tools.loose_translation import decode, json_values
from nskr_xedit_worker import row_key
import check_gemini_json_results as gemini_qa
from tools.tes4_text_scan import masters, plugin_records
from tools.translation_field_policy import skip_reason

HANGUL = re.compile("[가-힣]")


def canonical_text(text):
    return text.replace("\r\n", "\n")


def identity(row):
    return (row["owner"].casefold(), row["id"].casefold(), row["signature"])


def slot(row):
    return (*identity(row), row["field"], row["path"])


def source_key(row):
    return (*identity(row), row["field"], canonical_text(row["source"]))


def inspect(installation, fields, keys, work, name, worker, overrides=None, targets=None,
            reuse=False):
    job = work / name
    data = job / "Game/Data"
    overrides = {key.casefold(): value for key, value in (overrides or {}).items()}
    plugins = list(installation.active)
    existing = {x.casefold() for x in plugins}
    plugins.extend(path.name for key, path in overrides.items() if key not in existing)
    if reuse:
        previous = nskr.read_json(job / "inspect.request.json")
        if (previous["plugins"] != plugins or previous["fields"] != fields
                or previous["inspectRecordKeys"] != sorted(keys)
                or previous["targets"] != (targets or plugins)):
            raise ValueError("Cached inspection request differs")
        for plugin in plugins:
            source = overrides.get(plugin.casefold()) or installation.source(plugin)
            if nskr.sha256(source) != nskr.sha256(data / plugin):
                raise ValueError(f"Cached inspection source changed: {plugin}")
        return nskr.read_json(job / "inspect.json")
    data.mkdir(parents=True)
    before = {}
    for plugin in plugins:
        source = overrides.get(plugin.casefold()) or installation.source(plugin)
        before[source] = nskr.sha256(source)
        shutil.copyfile(source, data / plugin)
    request = {"game": str(job / "Game"), "plugins": plugins,
               "targets": targets or plugins, "fields": fields,
               "inspectRecordKeys": sorted(keys), "mode": "inspect",
               "output": str(job / "inspect.json")}
    print(f"{name}: {len(request['targets'])}개 플러그인의 현재 필드 경로 확인", flush=True)
    result = nskr_xedit.run_worker(request, job, "inspect", worker)
    if any(nskr.sha256(path) != digest for path, digest in before.items()):
        raise ValueError("Inspection changed a source plugin")
    return result


def pick(candidates):
    """Only equal-priority, unambiguous translations may win."""
    if not candidates:
        return None
    priority = min(x[0] for x in candidates)
    best = [x[1] for x in candidates if x[0] == priority]
    if len({x["dest"] for x in best}) != 1:
        return None
    return best[0]


def gemini_matches(candidate, item):
    return (candidate["field"] == item["field"]
            and canonical_text(candidate["source"]) == canonical_text(item["source"])
            and candidate["occurrence"] == item["field_occurrence"])


def prepare(args):
    if args.output.exists():
        raise FileExistsError(args.output)
    installation = original_installation(
        nskr.Installation(args.mo2, args.profile), args.exclude_provider)
    sst = nskr.read_json(args.sst / "catalog.json")
    ui = nskr.read_json(args.review / "catalog.json")
    validation = nskr.read_json(args.review / "validation.json")
    if (sst.get("translation_ready") is not False or validation["errors"]
            or validation["missing"] or len(ui["files"]) != 37):
        raise ValueError("Expected unreleased SST and validated 37-file UI catalog")
    runtime = nskr.read_json(args.runtime / "catalog.json")
    if runtime.get("translation_ready") is not False:
        raise ValueError("Runtime must remain an unreleased candidate")
    gemini_qa.BASE = args.gemini
    manifest = nskr.read_json(args.gemini / "00_manifest.json")
    stats = Counter()
    fields = {key: set(value) for key, value in sst["plugin_fields"].items()}
    direct = defaultdict(lambda: defaultdict(list))
    keys = set()
    tracked = {}
    inputs = {}

    def add(plugin, row, origin, token):
        if skip_reason(row["signature"], row["field"], row["source"]):
            stats[f"{origin}_non_display_excluded"] += 1
            return
        if not row["source"] or not row["dest"] or row["source"] == row["dest"]:
            stats[f"{origin}_unchanged_excluded"] += 1
            return
        probe = {**row, "path": row.get("path", ""), "origin": origin}
        try:
            nskr_xedit.validate_mapping(probe)
        except ValueError:
            stats[f"{origin}_protected_or_invalid_excluded"] += 1
            return
        probe["_token"] = token
        inputs[token] = probe
        fields.setdefault(row["signature"], set()).add(row["field"])
        direct[plugin.casefold()][source_key(row)].append(probe)
        keys.add(row_key(row))
        stats[f"{origin}_input_rows"] += 1

    for entry in sst["files"]:
        if entry["kind"] != "plugin-records":
            continue
        for index, row in enumerate(entry["mappings"]):
            if row.get("origin") != "sst_direct":
                continue
            add(entry["path"], row, "sst_direct", f"sst:{entry['path']}:{index}")
    corrections = nskr.read_json(args.gemini / (
        "04_결과_검수_001/09_QA_PRIORITY_TRIAGE_20261010/"
        "06_P0_확인된오류_교정후보.json"))["proposals"]
    corrected = {(r["source_file"], r["key"]): r for r in corrections}
    gemini_rows = {}
    for job in manifest["files"]:
        state, rows, _ = gemini_qa.validate_batch(job)
        if state != "verified_structure":
            raise ValueError(f"Invalid Gemini batch: {job['source_file']}: {state}")
        stats["gemini_batches_validated"] += 1
        for raw in rows:
            gemini_rows[(raw["source_file"], raw["key"])] = raw
            stats["gemini_values_checked"] += 1
            if raw["qa_status"] == "SKIP_NON_DISPLAY":
                stats["gemini_non_display_excluded"] += 1
                continue
            dest = raw["korean_candidate"]
            correction = corrected.get((raw["source_file"], raw["key"]))
            if (correction and raw["english_source"] == correction["expected_english_source"]
                    and dest == correction["expected_previous_korean"]):
                dest = correction["proposed_corrected_korean"]
                stats["verified_corrections_used"] += 1
            row = {"owner": raw["origin_master"].casefold(),
                   "id": f"{int(raw['formid'], 16) & 0xffffff:06x}",
                   "signature": raw["signature"], "field": raw["field"],
                   "source": raw["english_source"], "dest": dest,
                   "occurrence": int(raw["occurrence"])}
            add(raw["plugin"], row, "gemini_candidate",
                f"gemini:{raw['source_file']}:{raw['key']}")
    keep_file = args.gemini / (
        "04_결과_검수_001/08_UNRELEASED_GEMINI_QA_CATALOG_20261010/"
        "03_keep_original_radio_cues.jsonl")
    keep = set()
    for line in keep_file.read_text(encoding="utf-8-sig").splitlines():
        raw = json.loads(line)
        metadata = gemini_rows[(raw["source_file"], raw["key"])]
        if raw["original"] != metadata["english_source"] or raw["action"] != "SKIP":
            raise ValueError("Radio cue preservation source mismatch")
        keep.add((metadata["plugin"].casefold(), metadata["origin_master"].casefold(),
                  f"{int(metadata['formid'], 16) & 0xffffff:06x}", metadata["signature"],
                  metadata["field"], canonical_text(metadata["english_source"])))

    donors = [args.donors / name for name in
              ("FO3 KR.esm", "TaleOfTwoWastelands.esm", "YUPTTW.esm")]
    for path in donors:
        names = [name.casefold() for name in masters(path)] + [path.name.casefold()]
        for fid, signature, values in plugin_records(path):
            owner = fid >> 24
            if owner >= len(names):
                raise ValueError(f"Invalid donor record owner: {path.name}:{fid:08X}")
            if names[owner] == "fo3 kr.esm":
                continue
            if any(field in fields.get(signature, set()) for field, _ in values):
                keys.add(f"{names[owner]}|{fid & 0xffffff:06x}|{signature}")
    tracked.update({path: nskr.sha256(path) for path in donors})
    tracked.update({installation.source(name): nskr.sha256(installation.source(name))
                    for name in installation.active})
    tracked.update({path: nskr.sha256(path) for path in installation.profile_dir.rglob("*")
                    if path.is_file()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    work = (args.inspection_work if args.inspection_work else
            Path(tempfile.mkdtemp(prefix="full-native-", dir=args.output.parent)))
    field_list = {key: sorted(value) for key, value in fields.items()}
    current = inspect(installation, field_list, keys, work, "current", args.worker,
                      reuse=args.inspection_work is not None)
    donor = inspect(installation, field_list, keys, work, "donors", args.worker,
                    overrides={p.name: p for p in donors}, targets=[p.name for p in donors],
                    reuse=args.inspection_work is not None)
    base = {}
    for file in current["files"]:
        for item in file["rows"]:
            if file["plugin"].casefold() == item["owner"].casefold():
                base[slot(item)] = item
    donor_bank = defaultdict(list)
    for file in donor["files"]:
        for item in file["rows"]:
            original = base.get(slot(item))
            if (not original or not original["source"]
                    or item["owner"].casefold() == "fo3 kr.esm"
                    or item["edid"] != original["edid"] or not HANGUL.search(item["source"])
                    or skip_reason(item["signature"], item["field"], original["source"])):
                continue
            row = {key: original[key] for key in
                   ("owner", "id", "signature", "field", "path", "source")}
            row.update(dest=item["source"], origin="ttw_donor",
                       donor_plugin=file["plugin"])
            try:
                nskr_xedit.validate_mapping(row)
            except ValueError:
                stats["donor_protected_or_invalid_excluded"] += 1
                continue
            donor_bank[slot(item)].append(row)

    resolved = {}
    native_rows = {}
    seen = set()
    allowed = ("owner", "id", "signature", "field", "path", "source", "dest", "origin")
    for file in current["files"]:
        plugin = file["plugin"]
        result = []
        native_rows[plugin] = file["rows"]
        for item in file["rows"]:
            if (plugin.casefold(), *identity(item), item["field"],
                    canonical_text(item["source"])) in keep:
                stats["radio_identifiers_preserved"] += 1
                continue
            if skip_reason(item["signature"], item["field"], item["source"]):
                continue
            candidates = []
            for row in direct[plugin.casefold()].get(source_key(item), []):
                if row["origin"] == "gemini_candidate":
                    matched = gemini_matches(row, item)
                else:
                    matched = not row["path"] or row["path"] == item["path"]
                if matched:
                    seen.add(row["_token"])
                    candidates.append((0 if row["origin"] == "sst_direct" else 1, row))
            for row in donor_bank.get(slot(item), []):
                if canonical_text(row["source"]) == canonical_text(item["source"]):
                    priority = 2 if row["donor_plugin"].casefold() == plugin.casefold() else 3
                    candidates.append((priority, row))
            chosen = pick(candidates)
            if chosen and chosen["dest"] != item["source"]:
                mapping = {key: item[key] for key in
                           ("owner", "id", "signature", "field", "path", "source",
                            "field_occurrence")}
                mapping.update(dest=chosen["dest"], origin=chosen["origin"])
                nskr_xedit.validate_mapping(mapping)
                result.append(mapping)
            elif candidates and chosen is None:
                stats["conflicting_current_slots_held"] += 1
        resolved[plugin] = result
    inheritance = {}
    for plugin, rows in resolved.items():
        for row in rows:
            if plugin.casefold() == row["owner"].casefold():
                inheritance[slot(row)] = row
    for plugin, items in native_rows.items():
        existing = {slot(row) for row in resolved[plugin]}
        for item in items:
            row = inheritance.get(slot(item))
            if (slot(item) in existing or not row
                    or canonical_text(row["source"]) != canonical_text(item["source"])
                    or row["dest"] == item["source"]):
                continue
            if (plugin.casefold(), *identity(item), item["field"],
                    canonical_text(item["source"])) in keep:
                continue
            mapping = {key: item[key] for key in
                       ("owner", "id", "signature", "field", "path", "source",
                        "field_occurrence")}
            mapping.update(dest=row["dest"], origin="base_translation_inherited")
            resolved[plugin].append(mapping)
            existing.add(slot(item))

    args.output.mkdir()
    files = []
    for entry in ui["files"]:
        source = installation.source(entry["path"])
        current_hash = nskr.sha256(source)
        if installation.providers[entry["path"].casefold()][-1]["provider"] != entry["provider"]:
            raise ValueError(f"UI provider changed: {entry['path']}")
        prepared = {**entry, "review_status": "ui_reviewed"}
        if current_hash != entry["baseline_sha256"]:
            if entry["kind"] != "json":
                raise ValueError(f"Reviewed INI changed: {entry['path']}")
            text, _ = decode(source)
            obj = json.loads(text)
            current_slots = {(stable_context(obj, list(pointer)), value)
                             for pointer, value in json_values(obj)}
            prepared["mappings"] = [row for row in entry["mappings"]
                                    if (row["context"], row["source"]) in current_slots]
            prepared["baseline_sha256"] = current_hash
            prepared["updated_source_exact_matches_only"] = True
            stats["ui_updated_source_candidates_held"] += (
                len(entry["mappings"]) - len(prepared["mappings"]))
            stats["ui_updated_sources_rebound"] += 1
        tracked[source] = current_hash
        files.append(prepared)
    for plugin, mappings in resolved.items():
        if not mappings:
            continue
        source = installation.source(plugin)
        files.append({"path": plugin, "kind": "plugin-records",
                      "baseline_sha256": nskr.sha256(source),
                      "review_status": "source_matched_candidate", "mappings": mappings})
        stats["plugins_with_resolved_translations"] += 1
        stats.update({f"resolved_{origin}": count for origin, count in
                      Counter(row["origin"] for row in mappings).items()})
    stats["active_plugins_checked"] = len(current["files"])
    stats["candidate_input_rows_not_matched"] = len(set(inputs) - seen)
    font = deepcopy(sst["font_bundle"])
    payloads = [(font["ini"], "NVSE/plugins/tnvse.ini"),
                (font["xml"], "NVSE/plugins/tnvse_fonts.xml")]
    payloads.extend((entry, entry["path"]) for entry in font["assets"])
    for entry, relative in payloads:
        source = args.font_mod / relative
        target = nskr.contained(args.output, entry["payload"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        entry["payload_sha256"] = nskr.sha256(target)
        if entry["payload_sha256"] != nskr.sha256(source):
            raise ValueError("Font candidate copy mismatch")
    for spec in runtime["runtime_mods"]:
        if not {x.casefold() for x in spec["required_masters"]}.issubset(installation.active_keys):
            raise ValueError("UI plugin master is not active")
        for entry in spec["files"]:
            source = nskr.contained(args.runtime, entry["payload"])
            if nskr.sha256(source) != entry["payload_sha256"]:
                raise ValueError("Runtime payload mismatch")
            target = nskr.contained(args.output, entry["payload"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    catalog = {"schema_version": 1, "target_modlist": "nuclear-sunset-ttw",
               "channel": "development", "translation_ready": False,
               "full_translation_catalog": True, "strict_plugin_paths": True,
               "excluded_test_providers": args.exclude_provider,
               "gemini_candidates_included": True, "human_review_complete": False,
               "automatic_inheritance": False, "game_validation": "pending",
               "tested_profile": installation.profile, "candidate_summary": dict(stats),
               "ui_review_counts": validation["counts"], "files": files,
               "plugin_fields": field_list, "font_bundle": font,
               "runtime_mods": runtime["runtime_mods"]}
    output_catalog(catalog, True, {"ui", "fonts", "plugins"})
    if any(nskr.sha256(path) != digest for path, digest in tracked.items()):
        raise ValueError("An original file/profile changed during preparation")
    nskr.write_json(args.output / "catalog.json", catalog)
    nskr.write_json(args.output / "unmatched-inputs.json", [
        {"input": token, **{key: value for key, value in row.items() if key != "_token"}}
        for token, row in inputs.items() if token not in seen])
    return {"catalog": str(args.output), "native_work": str(work),
            "counts": dict(stats), "translation_ready": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("sst", "review", "gemini", "donors", "runtime", "font-mod",
                 "mo2", "worker", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--exclude-provider", action="append", default=[])
    parser.add_argument("--inspection-work", type=Path)
    print(json.dumps(prepare(parser.parse_args()), ensure_ascii=False), flush=True)
