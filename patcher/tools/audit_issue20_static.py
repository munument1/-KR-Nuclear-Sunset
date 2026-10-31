"""Read-only Nuclear Sunset #20 triage from a patcher report and release catalog.

This is *not* an encoding fix or a game-validation tool. It never rewrites mods,
Output, TranslationData, savegames or the supplied report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import zipfile

REVIEW_FIELDS = (
    "composition_review_notes",
    "dynamic_encoding_review_notes",
    "notification_review_notes",
    "runtime_text_review_notes",
    "override_review_notes",
    "unmatched_entries",
)
DISPLAY_FIELDS = ("dest", "translation")
SOURCE_FIELDS = ("source", "original")


def canonical_display(value):
    """Grouping hint only: NEVER use to rewrite actual translations."""
    return re.sub(r"[.。]+$", "", value.strip().strip("[]").strip()).strip()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def catalog_documents(path):
    """Yield only known translation JSON schemas (directory or ZIP)."""
    if path.is_dir():
        candidates = (path / "catalog.json",
                      path / "runtime_ui" / "NSKR_UI_Translations.json")
        for candidate in candidates:
            if candidate.is_file():
                yield candidate.relative_to(path).as_posix(), read_json(candidate)
    elif path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for name in (
                "TranslationData/catalog.json",
                "TranslationData/runtime_ui/NSKR_UI_Translations.json",
            ):
                if name in archive.namelist():
                    with archive.open(name) as stream:
                        yield name, json.loads(stream.read().decode("utf-8-sig"))
    else:
        raise ValueError("TranslationData must be a directory or ZIP")


def iter_translations(node, location="$"):
    """Capture paired, context-rich mappings without assuming a catalog size."""
    if isinstance(node, dict):
        display_key = next((k for k in DISPLAY_FIELDS if isinstance(node.get(k), str)), None)
        source_key = next((k for k in SOURCE_FIELDS if isinstance(node.get(k), str)), None)
        if display_key is not None:
            context = {k: node[k] for k in (
                "owner", "id", "signature", "field", "path", "section", "key",
            ) if isinstance(node.get(k), (str, int))}
            yield {"json_path": location,
                   "source": node[source_key] if source_key is not None else None,
                   "display": node[display_key],
                   "context": context}
        for key, child in node.items():
            yield from iter_translations(child, location + "." + str(key))
    elif isinstance(node, list):
        for index, child in enumerate(node):
            yield from iter_translations(child, f"{location}[{index}]")


def collect_report(report):
    if not isinstance(report, dict) or not isinstance(report.get("files"), list):
        raise ValueError("Expected a patcher .report.json with a files list")
    findings = []
    for file in report["files"]:
        path = file.get("output_path") or file.get("path") or "<unknown>"
        for key in REVIEW_FIELDS:
            notes = file.get(key, [])
            if notes is None:
                continue
            if not isinstance(notes, list):
                raise ValueError(f"Invalid {key} in report file: {path}")
            for note in notes:
                findings.append({"layer": key, "output_path": path, "evidence": note})
        unmatched = file.get("unmatched", 0)
        if isinstance(unmatched, int) and unmatched > 0 and not file.get("unmatched_entries"):
            findings.append({"layer": "unmatched_without_details",
                             "output_path": path, "evidence": {"count": unmatched}})
    for skipped in report.get("skipped", []):
        findings.append({"layer": "skipped", "output_path": skipped.get("path", "<unknown>"),
                         "evidence": skipped})
    return findings


def audit(report, docs=(), terms=("탄피", "탄피.")):
    findings = collect_report(report)
    requested = {canonical_display(term) for term in terms if term.strip()}
    variants = {}
    for docname, content in docs:
        for entry in iter_translations(content):
            base = canonical_display(entry["display"])
            if base in requested:
                variants.setdefault(base, []).append({"document": docname, **entry})
    conflicting = {}
    for base, entries in variants.items():
        forms = sorted(set(item["display"] for item in entries))
        if len(forms) > 1:
            conflicting[base] = {"forms": forms, "entries": entries}
    return {
        "schema": "nskr-issue20-static-triage-v1",
        "game_validation": "not_run",
        "scope": "patcher report and known translation JSON; no binary ESP/ESM parsing",
        "report_review_count": len(findings),
        "report_findings": findings,
        "requested_terms": list(terms),
        "translation_hits": variants,
        "variant_candidates": conflicting,
        "limitations": [
            "Different contexts can legitimately use different punctuation.",
            "An Output report cannot prove which MO2 provider won in game.",
            "No screenshot text, live DLL, logs or game save was inspected.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--data", type=Path, help="TranslationData directory or release ZIP")
    parser.add_argument("--term", action="append", dest="terms")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = read_json(args.report)
    docs = list(catalog_documents(args.data)) if args.data else []
    result = audit(report, docs, tuple(args.terms or ("탄피", "탄피.")))
    # Never overwrite a prior audit or modify any input file.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as dest:
        json.dump(result, dest, ensure_ascii=False, indent=2)
        dest.write("\n")
    print(f"Issue #20 static audit: {len(result['report_findings'])} report notes; "
          f"{sum(map(len, result['translation_hits'].values()))} term mappings; "
          f"{len(result['variant_candidates'])} punctuation candidate(s). "
          "No game outcome inferred.")


if __name__ == "__main__":
    main()
