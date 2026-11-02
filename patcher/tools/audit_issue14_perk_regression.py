"""Read-only comparison of Nuclear Sunset PERK translation catalogs and patch reports.

This cannot prove what the game renders. It identifies candidate PERK records
and highlights missing source mappings, changed Korean text, and report failures.
It never reads or writes game/mod files.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

COLUMNS = (
    "plugin", "provider", "owner", "formid", "field", "path", "occurrence",
    "change", "previous_source", "current_source", "previous_dest",
    "current_dest", "report_status", "notes",
)


def read_json(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def identity(entry: dict, row: dict) -> tuple:
    """Do not merge different physical providers or repeated text fields."""
    return (
        entry["path"].casefold(),
        (entry.get("provider") or "").casefold(),
        row["owner"].casefold(),
        row["id"].casefold(),
        row["field"],
        row["path"],
        row.get("field_occurrence", 0),
    )


def index_perks(catalog: dict) -> dict[tuple, list[dict]]:
    if (catalog.get("target_modlist") != "nuclear-sunset-ttw"
            or catalog.get("schema_version") != 1):
        raise ValueError("Not a Nuclear Sunset schema-1 catalog")
    results: dict[tuple, list[dict]] = {}
    for entry in catalog.get("files", []):
        if entry.get("kind") != "plugin-records":
            continue
        for row in entry.get("mappings", []):
            if row.get("signature") != "PERK" or row.get("field") not in {"FULL", "DESC"}:
                continue
            key = identity(entry, row)
            results.setdefault(key, []).append(row)
    return results


def _report_state(report: dict | None, key: tuple) -> tuple[str, str]:
    if report is None:
        return "report_not_provided", ""
    plugin, provider, owner, formid, field, path, occurrence = key
    relevant = [
        r for r in report.get("files", [])
        if str(r.get("path", "")).casefold() == plugin
        and (not provider or str(r.get("provider", "")).casefold() == provider)
    ]
    for item in report.get("skipped", []):
        if str(item.get("path", "")).casefold() == plugin and (
                not provider or str(item.get("provider", "")).casefold() == provider):
            return "skipped", str(item.get("reason") or "unknown")
    for item in relevant:
        for unmatched in item.get("unmatched_entries", []):
            if (str(unmatched.get("owner", "")).casefold() == owner
                    and str(unmatched.get("id", "")).casefold() == formid
                    and unmatched.get("signature") == "PERK"
                    and unmatched.get("field") == field
                    and unmatched.get("path") == path
                    and unmatched.get("field_occurrence", 0) == occurrence):
                return "mapping_unmatched", str(unmatched.get("reason") or "unknown")
    if not relevant:
        return "not_found_in_report", ""
    if any(e.get("formid", "").casefold() == formid
           and str(e.get("plugin", "")).casefold() == plugin
           and e.get("field") == "PERK/DESC"
           for e in report.get("english_only_exceptions", [])):
        return "explicit_english_exception", "Concentrated Fire workaround"
    # Current output reports aggregate success counts, not PERK-by-PERK success.
    return "plugin_processed_field_unverified", ""


def compare(previous: dict, current: dict, report: dict | None = None) -> list[dict]:
    older, newer = index_perks(previous), index_perks(current)
    rows = []
    for key in sorted(set(older) | set(newer)):
        old, new = older.get(key, []), newer.get(key, [])
        prior = old[0] if len(old) == 1 else {}
        latest = new[0] if len(new) == 1 else {}
        notes = []
        if len(old) > 1 or len(new) > 1:
            change = "ambiguous_duplicate_mapping"
            notes.append(f"previous_rows={len(old)}, current_rows={len(new)}")
        elif not old:
            change = "new_mapping"
        elif not new:
            change = "removed_mapping"
        elif prior["source"] != latest["source"]:
            change = "source_changed"
        elif prior["dest"] != latest["dest"]:
            change = "translation_changed"
        elif set(prior.get("previous_dests", [])) != set(latest.get("previous_dests", [])):
            change = "history_changed"
        else:
            change = "unchanged"
        state, explanation = _report_state(report, key)
        if explanation:
            notes.append(explanation)
        plugin, provider, owner, formid, field, path, occurrence = key
        rows.append(dict(zip(COLUMNS, (
            plugin, provider, owner, formid, field, path, occurrence,
            change, prior.get("source", ""), latest.get("source", ""),
            prior.get("dest", ""), latest.get("dest", ""), state,
            "; ".join(notes),
        ))))
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True, help="v1.0.2 TranslationData/catalog.json")
    parser.add_argument("--current", type=Path, required=True, help="v1.0.5 TranslationData/catalog.json")
    parser.add_argument("--report", type=Path, help="Optional v1.0.5 Output.report.json")
    parser.add_argument("--output", type=Path, help="New CSV file (stdout if omitted)")
    args = parser.parse_args(argv)
    old, new = read_json(args.previous), read_json(args.current)
    report = read_json(args.report) if args.report else None
    result = compare(old, new, report)
    if args.output:
        if args.output.resolve() in {x.resolve() for x in
                                     (args.previous, args.current, args.report) if x}:
            parser.error("Output cannot overwrite an input")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive mode: never overwrite an earlier diagnostic or user file.
        with args.output.open("x", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(result)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
