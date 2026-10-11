"""Synchronize version-neutral Nuclear Sunset core from VNV canonical sources.

Pure base code: SST, XEditLib shim, xEdit bridge, xEdit worker.
Game profiles, font output, MCM/catalog logic stay target-specific.

Default --check makes no changes. --apply uses an exact-match guard:
if NS has independent modifications, it refuses to replace those modules.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path

DEST_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VNV_ROOT = Path(r"D:\Codex_Trans\비바 뉴 베가스")
CORE_MODULES = ("sst", "xelib", "xedit", "xedit_worker")


def canonical_source(text: str, module: str) -> str:
    """Resolve only known package/binary namespace differences.

    Avoid blanket "VNV" -> "TTW": it would silently change user-facing
    instructions and game assumptions. All other differences must be reviewed.
    """
    if module not in CORE_MODULES:
        raise ValueError(f"Unknown shared module: {module}")
    if module == "xedit":
        text = text.replace(
            "Native XEditLib translation backend for Viva New Vegas.",
            "Native XEditLib translation backend for Nuclear Sunset.",
        )
    if module in ("xedit", "xedit_worker"):
        text = text.replace("vnvkr", "nskr").replace("VNVKR", "NSKR")
    return text


def fingerprints(source_root: Path, destination_root: Path):
    results = []
    for module in CORE_MODULES:
        source = source_root / f"vnvkr_{module}.py"
        dest = destination_root / f"nskr_{module}.py"
        if not source.is_file():
            raise FileNotFoundError(f"Canonical VNV module unavailable: {source}")
        source_text = source.read_text(encoding="utf-8-sig")
        expected = canonical_source(source_text, module)
        actual = dest.read_text(encoding="utf-8-sig") if dest.is_file() else None
        if "\x00" in expected or "import vnvkr" in expected or "VNVKR_XEDIT_RUNTIME" in expected:
            raise ValueError(f"Unexpected namespace leak in {module}")
        results.append((module, source, dest, expected, actual))
    return results


def run(vnv_root: Path, target_root: Path, apply: bool, backup_root: Path | None = None):
    pairs = fingerprints(vnv_root, target_root)
    changes = []
    for module, source, target, expected, actual in pairs:
        if actual is None:
            raise FileNotFoundError(f"Shared target module missing: {target}")
        if actual != expected:
            changes.append((module, source, target, expected, actual))
    if apply and changes:
        # Refuse automatic copy when a TTW/Nuclear-specific change could be
        # overwritten. Users can inspect the per-module diff first.
        for module, source, target, expected, actual in changes:
            diff = list(difflib.unified_diff(
                actual.splitlines(), expected.splitlines(),
                fromfile=f"nskr_{module}.py", tofile=f"vnvkr_{module}.py synced", n=2))
            if backup_root is None:
                raise RuntimeError(
                    f"{module} diverged; --apply requires --backup-root to preserve local changes.\n"
                    + "\n".join(diff[:36]))
        if backup_root.exists():
            raise FileExistsError(f"Backup folder already exists: {backup_root}")
        backup_root.mkdir(parents=True)
        # Stage backups before a single change.
        for module, source, target, expected, actual in changes:
            (backup_root / target.name).write_text(actual, encoding="utf-8")
        for module, source, target, expected, actual in changes:
            tmp = target.with_name(target.name + ".sync-tmp")
            tmp.write_text(expected, encoding="utf-8")
            tmp.replace(target)
    report = {
        "source_vnv":str(vnv_root),
        "target_nuclear":str(target_root),
        "shared_modules":len(CORE_MODULES),
        "identical":len(CORE_MODULES)-len(changes),
        "out_of_sync":[entry[0] for entry in changes],
        "mode":"APPLIED_WITH_BACKUP" if apply and changes else "CHECK_ONLY" if not apply else "ALREADY_IDENTICAL",
        "shared":[
            {"name":module,"matches_vnv":actual==expected,
             "canonical_sha256":hashlib.sha256(expected.encode("utf-8")).hexdigest()}
            for module, source, target, expected, actual in pairs
        ],
        "separate_target_modules":[
            "nskr.py (TTW/MO2 detection)","nskr_output.py (TTW sources/catalog)",
            "nskr_fonts.py (reversible separate tNVSE mod)",
            "nskr_gui.py (Nuclear Sunset profile/labels)"
        ]
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vnv-root",type=Path,default=DEFAULT_VNV_ROOT)
    parser.add_argument("--ns-root",type=Path,default=DEST_ROOT)
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--backup-root",type=Path,
                        help="Mandatory directory for --apply if sources have diverged.")
    args=parser.parse_args()
    report=run(args.vnv_root, args.ns_root,args.apply,args.backup_root)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not args.apply and report["out_of_sync"]:
        raise SystemExit(2)


if __name__=="__main__":main()
