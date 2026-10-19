"""Read-only evidence for issue #11 compiled SCPT runtime description overwrites.

This tool intentionally cannot build or patch ESPs: SCTX source text and SCDA
compiled bytecode must be changed by a verified script compiler together.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.tes4_text_scan import masters, plugin_records


HERE = Path(__file__).resolve().parents[1]
DEFAULT_MODS = Path(r"C:\Modlists\NuclearSunset\mods")
DEFAULT_DLL = HERE / ".local" / "key-prompt" / "Backend" / "XEditLib.dll"

CASES = (
    {
        "name": "Headhunter",
        "relative_plugin": "[#] [INF] - Nuclear Sunset Master Patches/NS.esp",
        "filename": "NS.esp",
        "record_formid": 0x91082F79,
        "record_owner": "S6S Perks.esp",
        "editor_id": "SCPTPatchForJBT",
        "target": "sssPerkHeadhunter",
        "source_en": (
            "You take your time to ensure that your bullets will land right "
            "between your target's eyes. You gain +25%% chance to hit your target's "
            "head in Bullet Time, at cost of 50%% increased AP cost. The second "
            "rank increases your reload speed while prone by 25%%, and your crit. "
            "damage while attacking your target's head in Bullet Time by 15%%."
        ),
        "expected_sha256": "29c237bc18133751fb9de138cd05644e64f7bb9d80502cd69ceeb9f923d461ea",
    },
    {
        "name": "Fast Metabolism",
        "relative_plugin": "[FL] [OP] - Sweet Consumables/Sweet Consumables.esp",
        "filename": "Sweet Consumables.esp",
        "record_formid": 0x12001870,
        "record_owner": "Sweet Consumables.esp",
        "editor_id": "sssSCPTIngestiblesStartup",
        "target": "FastMetabolism",
        "source_en": "%z Alcohol will also reduce your radiation twice as quickly.",
        "expected_sha256": "fbb771d36b5cc4c37e269a67caf48202afaf3654e9a87aaeaba3cebf74063fa1",
    },
)


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect_record(path: Path, spec: dict) -> dict:
    found = list(plugin_records(path, selected_ids={spec["record_formid"]}))
    if len(found) != 1 or found[0][1] != "SCPT":
        raise ValueError(f"Expected exactly one matching SCPT in {path}")
    formid, signature, fields = found[0]
    master_names = masters(path)
    owner_index = formid >> 24
    owner = (master_names[owner_index]
             if owner_index < len(master_names) else path.name)
    if owner.casefold() != spec["record_owner"].casefold():
        raise ValueError(f"Record owner mismatch {owner!r}")
    def one(name: str) -> bytes:
        values = [payload for sig, payload in fields if sig == name]
        if len(values) != 1:
            raise ValueError(f"{spec['name']} must have exactly one {name}")
        return values[0]

    edid = one("EDID").rstrip(b"\0").decode("ascii")
    if edid != spec["editor_id"]:
        raise ValueError(f"EDID mismatch {edid!r}")
    schr, scda, sctx = one("SCHR"), one("SCDA"), one("SCTX")
    if len(schr) != 20:
        raise ValueError(f"Unexpected SCHR size {len(schr)}")
    header = struct.unpack("<5I", schr)
    if header[2] != len(scda):
        raise ValueError("SCHR compiled length differs from SCDA payload")

    source = spec["source_en"]
    literal = source.encode("ascii")
    occurrences = {
        "SCTX": sctx.count(literal),
        "SCDA": scda.count(literal),
    }
    if occurrences != {"SCTX": 1, "SCDA": 1}:
        raise ValueError(f"Literal not unique in source/compiled payload: {occurrences}")

    scda_offset = scda.find(literal)
    sctx_offset = sctx.find(literal)
    if scda_offset < 2:
        raise ValueError("Compiled literal missing preceding size field")
    length_prefix = struct.unpack_from("<H", scda, scda_offset - 2)[0]
    if length_prefix != len(literal):
        raise ValueError("Compiled string length prefix mismatch")
    # Confirm the SCTX literal occurs in a precisely matching command.
    decoded_source = sctx.decode("ascii")
    statement = re.search(
        rf'\bSetFormDescription\s+{re.escape(spec["target"])}\s+"'
        rf'{re.escape(source)}"',
        decoded_source,
    )
    if statement is None:
        raise ValueError(f"Expected SetFormDescription command absent in {edid}")
    return {
        "formid": f"{formid:08X}",
        "signature": signature,
        "record_owner_from_verified_master_list": owner,
        "record_owner_index": owner_index,
        "editor_id": edid,
        "source_en": source,
        "source_len_ascii_bytes": len(literal),
        "source_occurrences": occurrences,
        "source_offset_in_sctx": sctx_offset,
        "source_offset_in_scda": scda_offset,
        "preceding_scda_uint16": length_prefix,
        "schr_uint32_values": list(header),
        "schr_compiled_size_matches_scda": header[2] == len(scda),
        "sctx_size": len(sctx),
        "scda_size": len(scda),
        "scda_sha256": hashlib.sha256(scda).hexdigest(),
        "subrecord_order": [name for name, _ in fields],
        "compiler_verified": False,
    }


def xeditlib_metadata(path: Path) -> dict:
    if not path.is_file():
        return {"status": "missing", "path": str(path)}
    result = {
        "path": str(path),
        "sha256": sha256_file(path),
        "file_size": path.stat().st_size,
    }
    try:
        import pefile
    except ImportError:
        result["status"] = "pefile unavailable: export/version audit not executed"
        return result
    pe = pefile.PE(str(path), fast_load=False)
    try:
        exports = sorted(
            symbol.name.decode("ascii", "replace")
            for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name
        )
        result["export_count"] = len(exports)
        result["compile_or_script_exports"] = [
            name for name in exports
            if any(key in name.lower() for key in ("compile", "script", "sctx", "scda"))
        ]
        version = {}
        for segment in getattr(pe, "FileInfo", []):
            for info in segment:
                for table in getattr(info, "StringTable", []):
                    version.update({
                        key.decode("utf-8", "replace"): val.decode("utf-8", "replace")
                        for key, val in table.entries.items()
                        if b"Version" in key or b"ProductName" in key
                    })
        result["version_info"] = version
        result["status"] = "export inspection only; SetValue is not a proven SCDA compiler"
    finally:
        pe.close()
    return result


def audit(mods: Path, dll: Path) -> dict:
    cases = []
    for spec in CASES:
        path = mods.joinpath(*spec["relative_plugin"].split("/"))
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = sha256_file(path)
        if digest != spec["expected_sha256"]:
            raise ValueError(f"Installed version has changed; inspect manually: {path}: {digest}")
        observed = inspect_record(path, spec)
        cases.append({
            "name": spec["name"],
            "file": str(path),
            "source_sha256": digest,
            "baseline_matches": True,
            **observed,
        })
    return {
        "mode": "READ_ONLY_AUDIT",
        "mutated_plugins": False,
        "translation_applied": False,
        "compiled_script_build_proven": False,
        "cases": cases,
        "xeditlib": xeditlib_metadata(dll),
        "safe_options": [
            "Recompile SCTX/SCDA consistently through NVSE-aware GECK on an isolated source copy, inspect all changed records, reload and compare, then verify in game.",
            "Investigate a separate JIP Script Runner description overlay; test timing against both original startup scripts and Unicode before enabling it for users.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mods", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--xeditlib", type=Path, default=DEFAULT_DLL)
    parser.add_argument(
        "--json-output", type=Path,
        help="Optional audit JSON destination; source plugins are always read only",
    )
    args = parser.parse_args()
    result = audit(args.mods, args.xeditlib)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        target = args.json_output.resolve()
        if target.suffix.lower() != ".json" or target.exists():
            raise ValueError("JSON output must be a new .json file")
        if target.is_relative_to(args.mods.resolve()):
            raise ValueError("Output must not be inside the source MO2 mods directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"READ_ONLY_AUDIT JSON={target}")
    for case in result["cases"]:
        print(f"VERIFIED {case['name']}: {case['editor_id']} "
              f"SCDA={case['scda_size']} source_bytes={case['source_len_ascii_bytes']}, "
              f"compiler_verified=False")
    meta = result["xeditlib"]
    print(f"XEDITLIB {meta.get('version_info')} "
          f"compile_exports={meta.get('compile_or_script_exports')}")
    print("No ESP/ESM changes made.")


if __name__ == "__main__":
    main()
