"""Build input/output resources for a font-only Nuclear Sunset v1.0.1 release.

Recover the published v1.0.0 resources, validate against its standalone
TranslationData mirror and SHA256SUMS, and only change the six affected tNVSE
font slots. The original modified tNVSE DLL stays binary-identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

from PyInstaller.archive.readers import CArchiveReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr

SLOTS = {"1", "2", "3", "6", "7", "42"}
OLD = "nanumsquareeb.ttf"
NEW = "pretendard-bold.ttf"
EXE = "NuclearSunsetKoreanPatcher.exe"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_zip(file: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(file) as z:
        invalid = z.testzip()
        if invalid:
            raise RuntimeError(f"Corrupt ZIP entry: {invalid}")
        names = z.namelist()
        if any(not name or name.startswith("/") or "\\" in name
               or ".." in Path(name).parts for name in names):
            raise RuntimeError("Unsafe zip member path")
        return {name: z.read(name) for name in names if not name.endswith("/")}


def verify_checksums(directory: Path) -> None:
    checksum_file = directory / "SHA256SUMS.txt"
    expected = {}
    for line in checksum_file.read_text(encoding="utf-8-sig").splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.strip().lstrip("*")] = digest.lower()
    for name in ("NuclearSunset-Korean-Patcher-v1.0.0.zip",
                 "NuclearSunset-TranslationData-v1.0.0.zip"):
        if nskr.sha256(directory / name) != expected.get(name):
            raise RuntimeError(f"Original release failed checksum verification: {name}")


def normalize_archive(exe: Path) -> dict[str, bytes]:
    reader = CArchiveReader(str(exe))
    return {key.replace(chr(92), "/"): reader.extract(key)
            for key in reader.toc
            if key.replace(chr(92), "/").startswith(("TranslationData/", "Backend/"))
            or key.replace(chr(92), "/") == "NSKRXEditWorker.exe"}


def prepare(release_dir: Path, work: Path) -> None:
    if work.exists():
        raise FileExistsError(work)
    verify_checksums(release_dir)
    patcher = read_zip(release_dir / "NuclearSunset-Korean-Patcher-v1.0.0.zip")
    data_zip = read_zip(release_dir / "NuclearSunset-TranslationData-v1.0.0.zip")
    if EXE not in patcher or len(patcher[EXE]) < 1000000:
        raise RuntimeError("Original release does not contain expected EXE")
    work.mkdir(parents=True)
    source_exe = work / EXE
    source_exe.write_bytes(patcher[EXE])
    originals = normalize_archive(source_exe)
    for name, contents in data_zip.items():
        if not name.startswith("TranslationData/"):
            raise RuntimeError(f"Unexpected original translation data entry: {name}")
        if originals.get(name) != contents:
            raise RuntimeError(f"Published translation archive differs from EXE: {name}")
    if "NSKRXEditWorker.exe" not in originals:
        raise RuntimeError("Missing packed XEdit worker binary")
    for name, contents in originals.items():
        dest = nskr.contained(work, name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(contents)

    data = work / "TranslationData"
    catalog_path = data / "catalog.json"
    catalog = nskr.read_json(catalog_path)
    bundle = catalog["font_bundle"]
    xml_entry = bundle["xml"]
    xml_path = nskr.contained(data, xml_entry["payload"])
    if nskr.sha256(xml_path) != xml_entry["payload_sha256"]:
        raise RuntimeError("Original font XML digest mismatch")
    paths = {i["path"].replace("\\", "/").casefold() for i in bundle["assets"]}
    if "nvse/plugins/fonts/pretendard-bold.ttf" not in paths:
        raise RuntimeError("Pretendard Bold was not included in published release")

    xml = ET.parse(xml_path, parser=ET.XMLParser(
        target=ET.TreeBuilder(insert_comments=True)))
    found = set()
    for font in xml.findall("./fonts/font"):
        slot = font.get("id")
        for face in font.iter("face"):
            old_name = face.get("path", "").replace("\\", "/").split("/")[-1].casefold()
            if old_name != OLD:
                continue
            if slot not in SLOTS or slot in found:
                raise RuntimeError(f"Unexpected NanumSquare font slot {slot}")
            original_path = face.get("path", "")
            face.set("path", original_path[:len(original_path)-len(OLD)] + "Pretendard-Bold.ttf")
            found.add(slot)
    if found != SLOTS:
        raise RuntimeError(f"Wrong font set: {sorted(found)}")
    xml.write(xml_path, encoding="utf-8", xml_declaration=True)
    xml_entry["payload_sha256"] = nskr.sha256(xml_path)
    nskr.write_json(catalog_path, catalog)
    for key, contents in originals.items():
        after = nskr.contained(work, key).read_bytes()
        if after != contents and key not in {"TranslationData/catalog.json",
                                            "TranslationData/" + xml_entry["payload"]}:
            raise RuntimeError(f"Unexpected resource change: {key}")
    print("Prepared NS font-only v1.0.1:", sorted(found))
    print("Original tnvse.dll and all non-font resources preserved")


def verify_built(release_dir: Path, work: Path, new_exe: Path) -> None:
    old = normalize_archive(work / EXE)
    new = normalize_archive(new_exe)
    if old.keys() != new.keys():
        raise RuntimeError(f"Resource key difference: {old.keys() ^ new.keys()}")
    cat = json.loads(new["TranslationData/catalog.json"].decode("utf-8-sig"))
    allowed = {"TranslationData/catalog.json",
               "TranslationData/" + cat["font_bundle"]["xml"]["payload"]}
    diffs = {key for key in old if old[key] != new[key]}
    if diffs != allowed:
        raise RuntimeError(f"Unexpected rebuilt resources: {diffs ^ allowed}")
    print("PASS: rebuilt EXE only modifies font XML and its catalog digest")


def package(release_dir: Path, work: Path, new_exe: Path, output: Path) -> None:
    verify_built(release_dir, work, new_exe)
    output.mkdir(parents=True, exist_ok=True)
    original_zip = read_zip(release_dir / "NuclearSunset-Korean-Patcher-v1.0.0.zip")
    patcher_zip = output / "NuclearSunset-Korean-Patcher-v1.0.1.zip"
    data_zip = output / "NuclearSunset-TranslationData-v1.0.1.zip"
    with zipfile.ZipFile(patcher_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, raw in original_zip.items():
            z.writestr(name, new_exe.read_bytes() if name == EXE else raw)
    with zipfile.ZipFile(data_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted((work/"TranslationData").rglob("*")):
            if path.is_file():
                z.write(path, "TranslationData/" + path.relative_to(work/"TranslationData").as_posix())
    for path in (patcher_zip, data_zip):
        with zipfile.ZipFile(path) as z:
            if z.testzip():
                raise RuntimeError(f"ZIP CRC failure: {path}")
    sums = "".join(f"{nskr.sha256(p)}  {p.name}\n" for p in (patcher_zip, data_zip))
    (output/"SHA256SUMS.txt").write_text(sums, encoding="ascii")
    print(sums)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("prepare", "package"):
        p = sub.add_parser(name)
        p.add_argument("--release", type=Path, required=True)
        p.add_argument("--work", type=Path, required=True)
        if name == "package":
            p.add_argument("--exe", type=Path, required=True)
            p.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.command == "prepare":
        prepare(args.release, args.work)
    else:
        package(args.release, args.work, args.exe, args.output)
