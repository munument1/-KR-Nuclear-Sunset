"""Prepare an UNRELEASED Nuclear Sunset translation review catalog from Gemini QA.

Offline only: does not change a mod, the original JSON, an MO2 profile,
or a runtime patcher's catalog. No xEdit path/record mapping is guessed.
Usage:
  py -3 tools/prepare_gemini_review_catalog.py --qa-csv ...\\검수대기_후보.csv \\
      --decisions ...\\07_검수결정_원본보존_20261010.json --output NEW_DIR
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

RADIO_ID = re.compile(r"^\\{Song\\s+\\d+\\s+[^{}]+\\}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_decisions(path: Path) -> dict[tuple[str, str], dict]:
    doc = json.loads(path.read_text(encoding="utf-8-sig"))
    if doc.get("schema_version") != 1 or not isinstance(doc.get("decisions"), list):
        raise ValueError("Unsupported review decision document")
    decisions = {}
    for entry in doc["decisions"]:
        if entry.get("action") != "SKIP_TRANSLATION_KEEP_ORIGINAL":
            raise ValueError("Unknown decision: " + str(entry.get("action")))
        original = entry["expected_english"]
        if not RADIO_ID.fullmatch(original):
            raise ValueError("Only verified radio song identifiers can be auto-skipped")
        key = (entry["source_file"], entry["key"])
        if key in decisions:
            raise ValueError("Duplicate decision for " + str(key))
        decisions[key] = entry
    return decisions


def prepare(qa_csv: Path, decisions_path: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Output directory already exists; refusing to overwrite: " + str(output))
    decisions = load_decisions(decisions_path)
    seen = set()
    used = set()
    counters = Counter()
    entries = []
    unresolved = []
    radio = []
    with qa_csv.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        needed = {"source_file", "key", "plugin", "formid", "origin_master",
                  "signature", "field", "occurrence", "english_source",
                  "korean_candidate", "qa_status", "qa_notes"}
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError("QA CSV missing columns " + str(needed-set(reader.fieldnames or [])))
        for row in reader:
            identity = (row["source_file"], row["key"])
            if identity in seen:
                raise ValueError("Duplicate source identity: " + str(identity))
            seen.add(identity)
            counters["total"] += 1
            status = row["qa_status"]
            if identity in decisions:
                decision = decisions[identity]
                if (status != "REVIEW_REQUIRED"
                    or row["english_source"] != decision["expected_english"]
                    or not RADIO_ID.fullmatch(row["english_source"])):
                    raise ValueError("Radio cue decision/input mismatch " + str(identity))
                radio.append({"source_file": identity[0], "key": identity[1],
                              "original": row["english_source"], "action": "SKIP"})
                used.add(identity)
                counters["radio_kept_original"] += 1
                continue
            if status == "SKIP_NON_DISPLAY":
                counters["non_display"] += 1
                continue
            data = {field: row[field] for field in
                    ("source_file", "key", "plugin", "formid", "origin_master",
                     "signature", "field", "occurrence", "english_source", "korean_candidate")}
            data["source_sha256"] = hashlib.sha256(row["english_source"].encode("utf-8")).hexdigest()
            if status == "READY_FOR_HUMAN_QA":
                if not data["korean_candidate"] or data["korean_candidate"] == data["english_source"]:
                    raise ValueError("Invalid passing candidate " + str(identity))
                data["review_status"] = "AUTO_QA_PASS_NOT_HUMAN_APPROVED"
                entries.append(data)
                counters["auto_qa_pass"] += 1
            elif status == "REVIEW_REQUIRED":
                data["qa_notes"] = row["qa_notes"]
                data["review_status"] = "MANUAL_REVIEW_REQUIRED"
                unresolved.append(data)
                counters["manual_review"] += 1
            else:
                raise ValueError("Unexpected QA status: " + str(status))

    if set(decisions) != used:
        raise ValueError("Unused radio decisions: " + str(len(set(decisions)-used)))
    expected = {"total": 42021, "non_display": 4526,
                "auto_qa_pass": 34479, "manual_review": 2998,
                "radio_kept_original": 18}
    if any(counters[key] != num for key, num in expected.items()):
        raise ValueError("QA counts changed; no output created: " + str(dict(counters)))

    output.mkdir(parents=True)
    def write_jsonl(filename: str, records: list[dict]) -> None:
        with (output / filename).open("w", encoding="utf-8", newline="\n") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    write_jsonl("01_auto_qa_candidate_rows.jsonl", entries)
    write_jsonl("02_manual_review_required.jsonl", unresolved)
    write_jsonl("03_keep_original_radio_cues.jsonl", radio)
    report = {
        "schema_version": 1,
        "translation_ready": False,
        "runtime_build_eligible": False,
        "release_eligible": False,
        "record_paths_verified": False,
        "type": "provisional_translation_review_catalog",
        "source_qa_sha256": sha256(qa_csv),
        "source_decisions_sha256": sha256(decisions_path),
        "counts": dict(counters),
        "limitations": [
            "Rows passing machine QA are NOT human-approved.",
            "Plugin FormIDs from modlist scans may be load-order-relative.",
            "xEdit record paths are missing; this is NOT a patcher runtime SST catalog.",
            "The base-game, TTW, FO3 and active plugin identity must be matched at build time.",
            "No game plugins, fonts, API keys or mod assets are included."
        ]
    }
    (output / "00_UNRELEASED_REVIEW_STATUS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qa-csv", type=Path, required=True)
    ap.add_argument("--decisions", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(prepare(args.qa_csv, args.decisions, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
