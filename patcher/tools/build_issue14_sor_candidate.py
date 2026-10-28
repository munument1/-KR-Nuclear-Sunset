"""Issue #14: surgically restore v1.0.2 sOr bytes, without touching key prompts.

READ-ONLY inputs: the published v1.0.2 and v1.0.5 TranslationData ZIPs.
Output: a *candidate*, NEVER a published fix or in-game validation.

A known change in the key-prompt release converted sOr to CP949. That is
valid for its original UI path but may poison UTF-8 PERK detail composition.
Only a cloned-profile game test can confirm the causal link.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import struct
import zipfile
from pathlib import Path

from nskr_plugin_text import record_slots

TARGET_ID = 0x0D000BA9
TARGET_EDITOR = b"sOr\0"
OLD_BYTES = "또는".encode("cp949") + b"\0"
RESTORED_BYTES = "또는".encode("utf-8") + b"\0"
PROMPT_EDITOR = b"sPCControlsTextPrefix\0"
PROMPT_BYTES = "누르기".encode("cp949") + b"\0"
RELEASE_ITEM = "TranslationData/catalog.json"
MOD = "Nuclear Sunset - Korean UI Strings"
RECORD_HEAD = struct.Struct("<4sIIIIHH")
U32 = struct.Struct("<I")
U16 = struct.Struct("<H")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fields(body: bytes) -> list[tuple[bytes, bytes, bytes]]:
    return list(record_slots(body))


def _record_info(record: bytes) -> tuple[bytes, bytes] | None:
    if record[:4] != b"GMST":
        return None
    if U32.unpack_from(record, 8)[0] & 0x00040000:
        raise ValueError("Compressed GMST needs independent review")
    slots = fields(record[24:])
    return (
        next((payload for key, _, payload in slots if key == b"EDID"), b""),
        next((payload for key, _, payload in slots if key == b"DATA"), b""),
    )


def _iter_records(raw: bytes):
    """Flatten all records without treating GRUP bodies as record data."""
    def walk(data):
        pos = 0
        while pos < len(data):
            if len(data) - pos < 24:
                raise ValueError("Truncated record/group header")
            kind = data[pos:pos + 4]
            size = U32.unpack_from(data, pos + 4)[0]
            full_size = size if kind == b"GRUP" else 24 + size
            if full_size < 24 or pos + full_size > len(data):
                raise ValueError("Invalid plugin group/record size")
            block = data[pos:pos + full_size]
            if kind == b"GRUP":
                yield from walk(block[24:])
            else:
                yield block
            pos += full_size
        if pos != len(data):
            raise ValueError("Plugin record traversal ended incorrectly")
    return list(walk(raw))


def _key_prompt(raw: bytes) -> bytes:
    found = []
    for rec in _iter_records(raw):
        if rec[:4] != b"GMST":
            continue
        key, payload = _record_info(rec)
        if key == PROMPT_EDITOR:
            found.append(payload)
    if len(found) != 1:
        raise ValueError("Key-prompt GMST missing or duplicated")
    return found[0]


def _sor(raw: bytes) -> bytes:
    found = []
    for rec in _iter_records(raw):
        if rec[:4] == b"GMST":
            key, payload = _record_info(rec)
            if key == TARGET_EDITOR:
                if U32.unpack_from(rec, 12)[0] != TARGET_ID:
                    raise ValueError("Unexpected sOr FormID")
                found.append(payload)
    if len(found) != 1:
        raise ValueError("sOr GMST missing or duplicated")
    return found[0]


def repair(source: bytes, baseline: bytes) -> bytes:
    """Exactly one GMST/DATA rewrite, with structural size propagation."""
    if _sor(source) != OLD_BYTES:
        raise ValueError("Input is not the pinned v1.0.5 CP949 sOr")
    if _sor(baseline) != RESTORED_BYTES:
        raise ValueError("Reference v1.0.2 sOr was not UTF-8")
    if _key_prompt(source) != PROMPT_BYTES:
        raise ValueError("Unexpected current key-prompt bytes")
    if _key_prompt(baseline) != b"\0":
        raise ValueError("Reference release key-prompt state differs")

    hits = 0

    def walk(data: bytes) -> bytes:
        nonlocal hits
        result = bytearray()
        pos = 0
        while pos < len(data):
            if pos + 24 > len(data):
                raise ValueError("Truncated group/record")
            header = bytearray(data[pos:pos + 24])
            typ = header[:4]
            size = U32.unpack_from(header, 4)[0]
            full_size = size if typ == b"GRUP" else 24 + size
            if full_size < 24 or pos + full_size > len(data):
                raise ValueError("Invalid group/record size")
            body = data[pos + 24:pos + full_size]
            if typ == b"GRUP":
                new_body = walk(body)
                U32.pack_into(header, 4, 24 + len(new_body))
                result.extend(header + new_body)
            elif typ == b"GMST" and U32.unpack_from(header, 12)[0] == TARGET_ID:
                if U32.unpack_from(header, 8)[0] & 0x00040000:
                    raise ValueError("Unexpected compressed target")
                parts = fields(body)
                if [name for name, _, _ in parts] != [b"EDID", b"DATA"]:
                    raise ValueError("Unexpected sOr record structure")
                if parts[0][2] != TARGET_EDITOR or parts[1][2] != OLD_BYTES:
                    raise ValueError("Unexpected target identity/bytes")
                new_body = bytearray()
                for name, header_bytes, value in parts:
                    if name == b"DATA":
                        if len(header_bytes) != 6:
                            raise ValueError("Extended DATA needs independent review")
                        value = RESTORED_BYTES
                        header_bytes = name + U16.pack(len(value))
                    new_body.extend(header_bytes + value)
                U32.pack_into(header, 4, len(new_body))
                result.extend(header + new_body)
                hits += 1
            else:
                result.extend(data[pos:pos + full_size])
            pos += full_size
        if pos != len(data):
            raise ValueError("Traversal mismatch")
        return bytes(result)

    changed = walk(source)
    if hits != 1 or _sor(changed) != RESTORED_BYTES:
        raise ValueError("Expected exactly one repaired sOr")
    if _key_prompt(changed) != _key_prompt(source):
        raise ValueError("Key prompt changed")
    before, after = _iter_records(source), _iter_records(changed)
    if len(before) != len(after):
        raise ValueError("Plugin record count changed")
    differences = []
    for original, new in zip(before, after):
        if original != new:
            differences.append((original, new))
    if len(differences) != 1 or _record_info(differences[0][0]) != (TARGET_EDITOR, OLD_BYTES) \
            or _record_info(differences[0][1]) != (TARGET_EDITOR, RESTORED_BYTES):
        raise ValueError("Unrelated game records changed")
    return changed


def released_ui(archive: zipfile.ZipFile) -> tuple[dict, str, bytes]:
    catalog = json.loads(archive.read(RELEASE_ITEM))
    entries = [(mod, e) for mod in catalog["runtime_mods"] if mod["mod"] == MOD
               for e in mod["files"] if e["path"].casefold() == "nskr ui strings.esp"]
    if len(entries) != 1:
        raise ValueError("Not exactly one UI Strings payload")
    entry = entries[0][1]
    archive_path = "TranslationData/" + entry["payload"]
    original = archive.read(archive_path)
    if sha(original) != entry["payload_sha256"]:
        raise ValueError("Release catalog payload SHA mismatch")
    return catalog, archive_path, original


def build(previous_zip: Path, current_zip: Path, output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(output_dir)
    with zipfile.ZipFile(previous_zip) as old_zip, zipfile.ZipFile(current_zip) as current:
        old_catalog, old_path, baseline = released_ui(old_zip)
        catalog, target_path, source = released_ui(current)
        # Early TranslationData catalogs need not stamp the release tag in
        # metadata. The caller pins the official archive filenames, and repair
        # validates the exact source bytes + original game record identities.
        if (previous_zip.name != "NuclearSunset-TranslationData-v1.0.2.zip"
                or current_zip.name != "NuclearSunset-TranslationData-v1.0.5.zip"
                or old_catalog.get("target_modlist") != "nuclear-sunset-ttw"
                or catalog.get("target_modlist") != "nuclear-sunset-ttw"):
            raise ValueError("Unexpected target or official release filenames")
        if old_path != target_path:
            raise ValueError("Unexpected UI Strings catalog path change")
        changed = repair(source, baseline)
        before_hash, after_hash = sha(source), sha(changed)
        target_entry = next(e for mod in catalog["runtime_mods"] if mod["mod"] == MOD
                            for e in mod["files"] if e["path"].casefold() == "nskr ui strings.esp")
        target_entry["payload_sha256"] = after_hash
        result = {"status": "candidate_only_game_unverified", "input_version": "1.0.5",
                  "target": target_path,
                  "input_sha256": before_hash, "output_sha256": after_hash,
                  "changed_fields": ["GMST sOr DATA: CP949 -> original v1.0.2 UTF-8"],
                  "unchanged": ["GMST sPCControlsTextPrefix", "all other ESP records",
                                "all other TranslationData payloads"],
                  "key_prompt_regression_risk": "The 1.0.3 fix intentionally set sOr to CP949."}
        output_dir.mkdir(parents=True)
        with zipfile.ZipFile(output_dir / "issue14-sOr-UTF8-single-field-candidate.zip",
                             "x", zipfile.ZIP_DEFLATED) as single:
            single.writestr("NSKR UI Strings.esp", changed)
            single.writestr("DIAGNOSTIC-NOT-RELEASE.json",
                            json.dumps(result, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(output_dir / "NuclearSunset-TranslationData-v1.0.5-issue14-CANDIDATE.zip",
                             "x", zipfile.ZIP_DEFLATED) as patched:
            for member in current.infolist():
                name = member.filename
                data = (changed if name == target_path else
                        (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                        if name == RELEASE_ITEM else current.read(name))
                # writestr mutates ZipInfo.header_offset; never pass the live
                # source ZipInfo when the original archive is still in use.
                patched.writestr(copy.copy(member), data)
        with zipfile.ZipFile(output_dir / "NuclearSunset-TranslationData-v1.0.5-issue14-CANDIDATE.zip") as check:
            cat, path, data = released_ui(check)
            if path != target_path or data != changed:
                raise ValueError("Candidate TranslationData self-check failed")
            input_names, output_names = set(current.namelist()), set(check.namelist())
            if input_names != output_names:
                raise ValueError("Unexpected TranslationData member change")
            changed_members = {name for name in input_names
                               if current.read(name) != check.read(name)}
            if changed_members != {RELEASE_ITEM, target_path}:
                raise ValueError("TranslationData changed unrelated assets")
        (output_dir / "MANIFEST.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.previous, args.current, args.output_dir),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
