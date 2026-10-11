"""Package a tested executable without rebuilding it or including game Output."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve()
    data = build / "TranslationData"
    catalog = json.loads((data / "catalog.json").read_text(encoding="utf-8-sig"))
    report = json.loads(args.report.read_text(encoding="utf-8-sig"))
    assert catalog["translation_ready"] is False
    assert report["translation_ready"] is False
    assert not report["warnings"] and not report["skipped"]
    assert sum(row.get("unmatched", 0) for row in report["files"]) == 0
    exe = build / "NuclearSunsetKoreanPatcher.exe"
    root = Path(__file__).resolve().parents[1]
    for row in report["files"]:
        output = args.report.parent / args.report.name.removesuffix(".report.json")
        assert digest(output / row["output_path"]) == row["output_sha256"]
    args.destination.mkdir(parents=True, exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix="NSKR-v1.0.0-", dir=args.destination))
    name = "NuclearSunset-Korean-Patcher-v1.0.0.zip"
    with zipfile.ZipFile(target / name, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(exe, exe.name)
        archive.write(root / "README.md", "README.md")
        archive.write(root.parent / "translations/docs/main/korean-patch.md", "INSTALL.md")
        for folder in (data / "nskr-tNVSE-korean-fonts", data / "runtime/Nuclear Sunset - Radio Captions"):
            for source in folder.rglob("*"):
                if source.is_file() and (source.suffix.lower() in {".txt", ".html", ".md", ".zip"}
                                         or source.name == "LICENSE"):
                    archive.write(source, "Licenses-and-Source/" + source.relative_to(data).as_posix())
    data_name = "NuclearSunset-TranslationData-v1.0.0.zip"
    with zipfile.ZipFile(target / data_name, "w", zipfile.ZIP_DEFLATED) as archive:
        for source in data.rglob("*"):
            if source.is_file():
                archive.write(source, "TranslationData/" + source.relative_to(data).as_posix())
    for path in target.glob("*.zip"):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            assert not any("/Output/" in name or name.lower().endswith(".esm")
                           for name in archive.namelist())
    with zipfile.ZipFile(target / name) as archive:
        assert hashlib.sha256(archive.read(exe.name)).hexdigest() == digest(exe)
    hashes = "".join(f"{digest(path)}  {path.name}\n" for path in sorted(target.glob("*.zip")))
    (target / "SHA256SUMS.txt").write_text(hashes, encoding="ascii")
    print(json.dumps({"release_directory": str(target), "executable_sha256": digest(exe),
                      "assets": [{"name": p.name, "bytes": p.stat().st_size}
                                 for p in sorted(target.iterdir())]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
