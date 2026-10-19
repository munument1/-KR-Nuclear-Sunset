"""Audit and narrowly normalize verified New Vegas place names in an NS catalog.

Run --check before --apply. Only plugin mapping `dest` fields may change.
Applying writes a full, checksum-verified backup in .local/place-name-backups.
The output is consumed by a subsequent build using --catalog <catalog directory>.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


PATCHER = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PATCHER / ".local/key-prompt/TranslationData/catalog.json"
BACKUP_ROOT = PATCHER / ".local/place-name-backups"

# The glossary's unambiguous place names, selected only after checking source
# English and target examples across VNV and NS. Context-sensitive names such
# as Zion / Silver Rush / The Strip are intentionally excluded.
RULES = (
    ("New Vegas", (("뉴베가스", "뉴 베가스"),)),
    ("Nipton", (("닙톤", "닙튼"), ("닙턴", "닙튼"))),
    ("Old Mormon Fort", (("올드 몰몬 요새", "구 몰몬 요새"),)),
    ("Camp Golf", (("골프 캠프", "캠프 골프"),)),
)
SOURCE_PATTERNS = tuple(
    re.compile(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", re.I)
    for name, _ in RULES
)
RECORD_KEY = ("owner", "id", "signature", "field", "path", "source")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_catalog(catalog: dict) -> list[dict]:
    """Edit only safe dest substrings with a matching English place in source."""
    if catalog.get("target_modlist") != "nuclear-sunset-ttw":
        raise ValueError("Not a Nuclear Sunset TTW catalog")
    if not isinstance(catalog.get("files"), list):
        raise ValueError("Missing catalog files")

    changes = []
    for entry in catalog["files"]:
        if entry.get("kind") != "plugin-records":
            continue
        for mapping in entry.get("mappings", []):
            source, dest = mapping.get("source"), mapping.get("dest")
            if not isinstance(source, str) or not isinstance(dest, str):
                continue
            updated = dest
            applied = []
            for (name, replacements), pattern in zip(RULES, SOURCE_PATTERNS):
                if not pattern.search(source):
                    continue
                for old, new in replacements:
                    if old in updated:
                        hits = updated.count(old)
                        updated = updated.replace(old, new)
                        applied.append((name, old, new, hits))
            if updated == dest:
                continue
            # A substring-only transformation cannot alter tokens, formatting,
            # record addresses, or punctuation outside the whitelisted names.
            if not applied or not all(old not in updated for _, old, _, _ in applied):
                raise ValueError("Unexpected place-name replacement")
            mapping["dest"] = updated
            changes.append({
                "plugin": entry["path"],
                **{key: mapping.get(key) for key in RECORD_KEY},
                "old_dest": dest,
                "new_dest": updated,
                "rules": applied,
            })
    return changes


def write_catalog(path: Path, catalog: dict) -> None:
    # Match the existing nskr.write_json serializer and Windows CRLF layout.
    with path.open("w", encoding="utf-8", newline="\r\n") as stream:
        json.dump(catalog, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def allocate_temp(target: Path) -> Path:
    fd, raw = tempfile.mkstemp(prefix=".place-name-", suffix=".tmp", dir=target.parent)
    os.close(fd)
    return Path(raw)


def apply(catalog_path: Path, backup_root: Path, expected_count: int | None = None) -> dict:
    catalog_path = catalog_path.resolve(strict=True)
    original_sha = sha256_file(catalog_path)
    data = load(catalog_path)
    changes = normalize_catalog(data)
    if expected_count is not None and len(changes) != expected_count:
        raise ValueError(f"Expected {expected_count} matching rows; found {len(changes)}")
    if not changes:
        return {"status": "already_normalized", "changes": 0, "sha256": original_sha}

    temp = allocate_temp(catalog_path)
    try:
        write_catalog(temp, data)
        if load(temp) != data:
            raise ValueError("Written catalog does not round-trip identically")
        patched_sha = sha256_file(temp)
        if patched_sha == original_sha:
            raise ValueError("No serialized changes after normalization")
        if sha256_file(catalog_path) != original_sha:
            raise ValueError("Catalog was changed concurrently; refusing to overwrite")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = backup_root / f"{stamp}-{original_sha[:12]}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        backup = backup_dir / "catalog.json"
        shutil.copy2(catalog_path, backup)
        if sha256_file(backup) != original_sha:
            raise ValueError("Backup checksum mismatch; catalog not modified")
        summary = {
            "catalog": str(catalog_path),
            "backup": str(backup),
            "sha256_before": original_sha,
            "sha256_after": patched_sha,
            "change_count": len(changes),
            "by_rule": dict(Counter(name for c in changes for name, _, _, _ in c["rules"])),
            "by_plugin": dict(Counter(c["plugin"] for c in changes)),
            "record_keys": [{key: c[key] for key in RECORD_KEY} | {"plugin": c["plugin"]}
                            for c in changes],
        }
        (backup_dir / "manifest.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if sha256_file(catalog_path) != original_sha:
            raise ValueError("Catalog changed during backup; refusing to overwrite")
        os.replace(temp, catalog_path)
        if sha256_file(catalog_path) != patched_sha:
            raise ValueError("Applied catalog checksum mismatch; restore backup immediately")
        return {"status": "applied", **summary}
    finally:
        temp.unlink(missing_ok=True)


def restore(catalog_path: Path, manifest_path: Path) -> dict:
    catalog_path = catalog_path.resolve(strict=True)
    summary = json.loads(manifest_path.read_text(encoding="utf-8"))
    backup = Path(summary["backup"]).resolve(strict=True)
    if catalog_path != Path(summary["catalog"]).resolve():
        raise ValueError("Manifest targets another catalog")
    if sha256_file(backup) != summary["sha256_before"]:
        raise ValueError("Backup corrupted; refusing restore")
    if sha256_file(catalog_path) != summary["sha256_after"]:
        raise ValueError("Current catalog differs from this patch; refusing restore")
    temp = allocate_temp(catalog_path)
    try:
        shutil.copyfile(backup, temp)
        if sha256_file(temp) != summary["sha256_before"]:
            raise ValueError("Temporary restore file corrupted")
        os.replace(temp, catalog_path)
        if sha256_file(catalog_path) != summary["sha256_before"]:
            raise ValueError("Restored checksum mismatch")
        return {"status": "restored", "catalog": str(catalog_path),
                "sha256": summary["sha256_before"]}
    finally:
        temp.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Read-only match count")
    group.add_argument("--apply", action="store_true", help="Backup, verify, normalize")
    group.add_argument("--restore", type=Path, metavar="MANIFEST", help="Undo exact patch")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--backup-root", type=Path, default=BACKUP_ROOT)
    parser.add_argument("--expect-edits", type=int)
    args = parser.parse_args()
    if args.check:
        changes = normalize_catalog(load(args.catalog))
        result = {"status": "check", "catalog": str(args.catalog),
                  "change_count": len(changes),
                  "by_rule": dict(Counter(n for c in changes for n, _, _, _ in c["rules"])),
                  "by_plugin": dict(Counter(c["plugin"] for c in changes))}
    elif args.apply:
        result = apply(args.catalog, args.backup_root, args.expect_edits)
    else:
        result = restore(args.catalog, args.restore)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
