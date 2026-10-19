"""Produce a verified v1.0.5 *candidate* onedir package from v1.0.4.

The official v1.0.4 onedir ZIPs provide complete, self-contained binary and
licensed asset inputs. Current Python sources are separately recompiled;
patched translations and optional runtime overlay files are added afterwards.

Typical commands (from patcher/):

  python tools/build_v1_0_5_folder_release.py --preflight
  python tools/build_v1_0_5_folder_release.py --build
  python tools/build_v1_0_5_folder_release.py --package-check --candidate .local/v1.0.5-folder-candidate/output/NuclearSunset-Korean-Patcher-v1.0.5-candidate.zip

Never ships a onefile binary, modifies a baseline release, or publishes assets.
The build deliberately refuses branches that do not contain origin/main.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

PATCHER = Path(__file__).resolve().parents[1]
REPO = PATCHER.parent
sys.path.insert(0, str(PATCHER))
DEFAULT_BASE = PATCHER / ".local/place-name-release-reference-v1.0.4"
DEFAULT_CATALOG = PATCHER / ".local/key-prompt/TranslationData/catalog.json"
DEFAULT_WORK = PATCHER / ".local/v1.0.5-folder-candidate"
PATCHER_ZIP = "NuclearSunset-Korean-Patcher-v1.0.4.zip"
DATA_ZIP = "NuclearSunset-TranslationData-v1.0.4.zip"
PATCHER_SHA256 = "9f3768491cb7abf9de911f23a68273cb187136c106e672995f5e607a78645345"
DATA_SHA256 = "ffa78eec3126a886efe216bcc89e0f8af6f326fa9189397e79ca8f1f9cc5bcbc"
VERSION = "1.0.5"
IDENTITY = ("owner", "id", "signature", "field", "path", "source", "rec_id",
            "rec_id_max", "field_occurrence", "string_id")
PROTECTED_BASE = ("TranslationData/", "Backend/", "Licenses-and-Source/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def checked_path(root: Path, member: str) -> Path:
    if not member or "\\" in member or member.startswith("/") or ":" in member:
        raise ValueError(f"Unsafe ZIP/overlay member: {member!r}")
    parts = PurePosixPath(member).parts
    if any(p in ("", ".", "..") or p.rstrip(" .") != p for p in parts):
        raise ValueError(f"Unsafe ZIP/overlay member: {member!r}")
    target = (root / member).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes package: {member!r}")
    return target


def checked_zip(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    seen = set()
    files = {}
    for item in archive.infolist():
        path = item.filename
        checked_path(Path("."), path.rstrip("/"))
        normalized = path.rstrip("/").casefold()
        if normalized in seen:
            raise ValueError(f"Duplicate ZIP entry (case insensitive): {path}")
        seen.add(normalized)
        unix_type = (item.external_attr >> 16) & 0o170000
        if unix_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError(f"Unexpected non-regular ZIP member: {path}")
        if not item.is_dir():
            files[path] = item
    return files


def unpack(archive: zipfile.ZipFile, destination: Path) -> None:
    files = checked_zip(archive)
    for name in files:
        output = checked_path(destination, name)
        output.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(name) as source, output.open("xb") as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)


def verify_baselines(base: Path) -> tuple[Path, Path, dict]:
    patcher_zip, data_zip = base / PATCHER_ZIP, base / DATA_ZIP
    for path, wanted in ((patcher_zip, PATCHER_SHA256), (data_zip, DATA_SHA256)):
        if not path.is_file() or sha256(path) != wanted:
            raise ValueError(f"Missing/mismatched official v1.0.4 ZIP: {path}")
    with zipfile.ZipFile(patcher_zip) as full, zipfile.ZipFile(data_zip) as data:
        pfiles, dfiles = checked_zip(full), checked_zip(data)
        for name in ("NuclearSunsetKoreanPatcher.exe", "NSKRXEditWorker.exe",
                     "_internal/_bz2.pyd", "worker-runtime/_bz2.pyd",
                     "TranslationData/catalog.json", "Backend/XEditLib.dll"):
            if name not in pfiles:
                raise ValueError(f"Official onedir package missing {name}")
        if "TranslationData/catalog.json" not in dfiles:
            raise ValueError("Official TranslationData archive missing its catalog")
        if not all(name.startswith(("TranslationData/", "Licenses-and-Source/"))
                   for name in dfiles):
            raise ValueError("TranslationData ZIP contains unexpected top-level files")
        # The standalone TranslationData is an exact mirror of the release assets.
        if not dfiles.keys() <= pfiles.keys():
            raise ValueError("Standalone TranslationData has unexpected paths")
        for name, info in dfiles.items():
            other = pfiles[name]
            if info.file_size != other.file_size or data.read(name) != full.read(name):
                raise ValueError(f"Two official ZIPs disagree: {name}")
        catalog = json.loads(full.read("TranslationData/catalog.json"))
    if (catalog.get("packaging"), catalog.get("version")) != ("folder", "1.0.4"):
        raise ValueError("The supplied official catalog is not v1.0.4 folder")
    return patcher_zip, data_zip, catalog


def row_identity(mapping: dict) -> tuple:
    return tuple(mapping.get(key) for key in IDENTITY)


def entry_identity(entry: dict) -> tuple:
    return (entry["path"].casefold(), entry["kind"],
            (entry.get("provider") or "").casefold())


def attach_previous_destinations(reference: dict, merged: dict) -> dict:
    """Carry v1.0.4 Korean destinations for *exact* same record/provider.

    The deployed v1.0.4 may already have replaced English source values. New
    translations require previous_dests to allow precise Korean->Korean
    upgrades. Never match only source text or FormID independently.
    """
    from nskr_xedit import validate_mapping
    previous_entries = {entry_identity(e): e for e in reference["files"]
                        if e["kind"] == "plugin-records"}
    added_rows = 0
    aliases_added = 0
    for entry in merged["files"]:
        if entry["kind"] != "plugin-records":
            continue
        old_entry = previous_entries.get(entry_identity(entry))
        if old_entry is None:
            continue
        by_record = defaultdict(set)
        for old_row in old_entry.get("mappings", []):
            by_record[row_identity(old_row)].add(old_row["dest"])
        for row in entry.get("mappings", []):
            historic = by_record.get(row_identity(row), set()) - {row["dest"], row["source"]}
            if not historic:
                continue
            prior = row.get("previous_dests") or []
            if not isinstance(prior, list):
                raise ValueError("Malformed previous_dests in local catalog")
            newly_added = historic - set(prior)
            if not newly_added:
                continue
            row["previous_dests"] = sorted(set(prior) | newly_added)
            validate_mapping(row)  # format tokens from historical KO must be safe
            added_rows += 1
            aliases_added += len(newly_added)
    return {"historical_alias_rows_added": added_rows,
            "historical_aliases_added": aliases_added}


def verify_previous_destinations(reference: dict, merged: dict) -> dict:
    """Check every changed v1.0.4 destination survives as an upgrade alias."""
    merged_entries = {entry_identity(e): e for e in merged["files"]
                      if e["kind"] == "plugin-records"}
    changed = 0
    covered = 0
    for old_entry in reference["files"]:
        if old_entry["kind"] != "plugin-records":
            continue
        new_entry = merged_entries[entry_identity(old_entry)]
        by_record = defaultdict(list)
        for row in new_entry["mappings"]:
            by_record[row_identity(row)].append(row)
        for old_row in old_entry.get("mappings", []):
            current_rows = by_record.get(row_identity(old_row), [])
            if any(row["dest"] == old_row["dest"] for row in current_rows):
                continue
            changed += 1
            if not current_rows or not all(old_row["dest"] in row.get("previous_dests", [])
                                           for row in current_rows):
                raise ValueError(f"Missing v1.0.4 previous_dests alias for "
                                 f"{old_entry['path']}: {old_row['id']} "
                                 f"{old_row['field']}")
            covered += 1
    return {"v1_0_4_changed_destinations": changed,
            "covered_by_previous_dests": covered}


def keep_identity(reference: dict, updated: dict) -> dict:
    """Overlay current mappings while retaining every released English record.

    New mappings, revised destinations and future previous_dests aliases may be
    included; there is deliberately no global exact-55-delta requirement.
    """
    if (updated.get("schema_version") != reference.get("schema_version")
            or updated.get("target_modlist") != reference.get("target_modlist")):
        raise ValueError("Catalog target/schema differs from v1.0.4")
    available = defaultdict(list)
    for entry in updated.get("files", []):
        available[entry_identity(entry)].append(entry)
    for old_entry in reference["files"]:
        key = entry_identity(old_entry)
        choices = available.get(key, [])
        if len(choices) != 1:
            raise ValueError(f"Missing/ambiguous released entry: {key}")
        new_entry = choices[0]
        # A provider replacement must be requested explicitly by a future
        # migration rather than silently applying records to another mod.
        if old_entry.get("provider") != new_entry.get("provider"):
            raise ValueError(f"Provider changed in {old_entry['path']}")
        if old_entry["kind"] == "plugin-records":
            old = Counter(row_identity(m) for m in old_entry.get("mappings", []))
            new = Counter(row_identity(m) for m in new_entry.get("mappings", []))
            if old - new:
                raise ValueError(f"Original English record identity removed: {key}")
        else:
            old = Counter((m.get("source"), m.get("context"), tuple(m.get("pointer", ())),
                           m.get("section"), m.get("key")) for m in old_entry.get("mappings", []))
            new = Counter((m.get("source"), m.get("context"), tuple(m.get("pointer", ())),
                           m.get("section"), m.get("key")) for m in new_entry.get("mappings", []))
            if old - new:
                raise ValueError(f"Original UI mapping identity removed: {key}")
    result = copy.deepcopy(reference)
    for key, value in updated.items():
        if key not in ("version", "packaging", "font_bundle"):
            result[key] = copy.deepcopy(value)
    result["version"], result["packaging"] = VERSION, "folder"
    # v1.0.4 extracted the tNVSE corresponding source to regular files and
    # removed its ZIP from the font bundle. Keep the release's verified policy.
    result["font_bundle"] = copy.deepcopy(reference["font_bundle"])
    if result.get("target_modlist") != "nuclear-sunset-ttw":
        raise ValueError("Wrong modlist in output catalog")
    if sum(len(e.get("mappings", [])) for e in result["files"]) < sum(
            len(e.get("mappings", [])) for e in reference["files"]):
        raise ValueError("Catalog unexpectedly lost translations")
    attach_previous_destinations(reference, result)
    verify_previous_destinations(reference, result)
    return result


def validate_place_corrections(reference: dict, current: dict) -> dict:
    # Import the isolated audit helper only for the exact reference checks.
    from tools.normalize_place_names import normalize_catalog
    old = copy.deepcopy(reference)
    known = normalize_catalog(old)
    if len(known) != 55:
        raise ValueError(f"Unexpected v1.0.4 place-name baseline: {len(known)} != 55")
    pending = normalize_catalog(copy.deepcopy(current))
    if pending:
        raise ValueError(f"Active catalog still has {len(pending)} known name errors")
    return {"v1_0_4_place_corrections": len(known),
            "remaining_known_place_errors": len(pending)}


def overlay_tree(package: Path, overlay: Path | None) -> list[str]:
    if overlay is None:
        return []
    if not overlay.is_dir():
        raise ValueError(f"Overlay folder missing: {overlay}")
    names = []
    for source in sorted(overlay.rglob("*")):
        if not source.is_file():
            continue
        if source.is_symlink() or not source.resolve().is_relative_to(overlay.resolve()):
            raise ValueError(f"Overlay source escapes input folder: {source}")
        relative = source.relative_to(overlay).as_posix()
        if not relative.startswith(PROTECTED_BASE):
            raise ValueError(f"Overlay must live under TranslationData/Backend/Licenses: {relative}")
        if relative == "TranslationData/catalog.json":
            raise ValueError("Use --catalog to update catalog metadata and mappings")
        destination = checked_path(package, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        names.append(relative)
    return names


def embed_python_sources(package: Path) -> dict[str, str]:
    """Ship an exact snapshot of the Python source used for this candidate."""
    source_paths = sorted(PATCHER.glob("nskr*.py"))
    source_paths += [PATCHER / "ns_inventory.py"]
    source_paths += [PATCHER / "tools" / name for name in (
        "loose_translation.py", "merge_previous_catalogs.py",
        "normalize_place_names.py", "build_v1_0_5_folder_release.py",
        "audit_issue11_compiled_scripts.py", "tes4_text_scan.py")]
    destination = package / "Licenses-and-Source/NuclearSunset-Patcher-v1.0.5"
    checksums = {}
    for source in source_paths:
        if not source.is_file():
            raise FileNotFoundError(f"Required source snapshot missing: {source}")
        relative = source.relative_to(PATCHER).as_posix()
        target = checked_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        checksums[relative] = sha256(source)
        if sha256(target) != checksums[relative]:
            raise RuntimeError(f"Python source snapshot checksum mismatch: {relative}")
    (destination / "SOURCE-SHA256.json").write_text(
        json.dumps(checksums, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return checksums


def verify_embedded_sources(package: Path) -> int:
    root = package / "Licenses-and-Source/NuclearSunset-Patcher-v1.0.5"
    manifest = root / "SOURCE-SHA256.json"
    if not manifest.is_file():
        raise ValueError("Missing self-contained v1.0.5 Python source snapshot")
    digests = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(digests, dict) or not digests:
        raise ValueError("Empty Python source snapshot")
    for relative, expected in digests.items():
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"Malformed Python source hash: {relative}")
        candidate = checked_path(root, relative)
        if not candidate.is_file() or sha256(candidate) != expected:
            raise ValueError(f"Python source snapshot mismatch: {relative}")
    return len(digests)


def validate_payloads(package: Path, catalog: dict) -> int:
    data = package / "TranslationData"
    assets = catalog_payloads(catalog)
    verified = 0
    for asset in assets:
        path = checked_path(data, asset["payload"])
        if not path.is_file() or sha256(path) != asset["payload_sha256"]:
            raise ValueError(f"Missing/hash mismatch catalog payload: {asset['payload']}")
        verified += 1
    return verified


def catalog_payloads(catalog: dict) -> list[dict]:
    assets = list(catalog["font_bundle"].get("assets", ()))
    for entry in catalog.get("runtime_mods", []):
        assets.extend(entry.get("files", ()))
    return assets


def sync_local_payloads(package: Path, stage: Path, catalog: dict) -> list[str]:
    """Add changed, checksum-declared runtime/NVSE files from local TranslationData.

    Retain v1.0.4 assets unless the current manifest explicitly changes the
    payload digest; unrelated staging files (including old font-source ZIPs)
    are never copied automatically.
    """
    if not stage.is_dir():
        raise ValueError(f"Current TranslationData directory not found: {stage}")
    copied = []
    for asset in catalog_payloads(catalog):
        relative = asset["payload"]
        expected = asset["payload_sha256"]
        target = checked_path(package / "TranslationData", relative)
        if target.is_file() and sha256(target) == expected:
            continue
        source = checked_path(stage, relative)
        if not source.is_file() or source.is_symlink() or sha256(source) != expected:
            raise ValueError(f"Updated runtime asset missing/incorrect in local data "
                             f"or explicit overlay: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append("TranslationData/" + relative)
    return copied


def write_catalog(package: Path, catalog: dict) -> None:
    file = package / "TranslationData/catalog.json"
    file.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def git_provenance() -> dict:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()
    head = git("rev-parse", "HEAD")
    main = git("rev-parse", "origin/main")
    joined = subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"],
                            cwd=REPO, capture_output=True)
    provenance = "ancestor"
    if joined.returncode != 0:
        # Integrating the onedir tool via a cherry-pick generates a distinct
        # commit SHA. Accept that history only when the tracked release builder
        # has the exact same blob as origin/main, i.e. the critical v1.0.4
        # packaging change was actually imported and committed.
        path = "patcher/tools/build_folder_release.py"
        source_blob = subprocess.run(["git", "rev-parse", f"HEAD:{path}"],
                                    cwd=REPO, text=True, capture_output=True)
        main_blob = git("rev-parse", f"origin/main:{path}")
        if source_blob.returncode or source_blob.stdout.strip() != main_blob:
            raise ValueError("Current HEAD does not contain origin/main's v1.0.4 "
                             "onedir builder; merge or cherry-pick that code before "
                             "making a v1.0.5 candidate")
        provenance = "cherry-picked-exact-onedir-builder"
    return {"head": head, "origin_main": main,
            "branch": git("branch", "--show-current"), "main_integration": provenance}


def assert_sources() -> dict:
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("_nskr_version_check", PATCHER / "nskr.py")
    # No execution of nskr functions here, only import to read the version.
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.VERSION != VERSION:
        raise ValueError(f"Source version must be {VERSION}, got {module.VERSION}")
    required = [PATCHER / "nskr_gui.py", PATCHER / "nskr_xedit_worker.py",
                PATCHER / "tools/xedit_worker_utf8.manifest"]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    return git_provenance()


def expand_standard_library(folder: Path) -> None:
    for zipped in list(folder.rglob("base_library.zip")):
        with zipfile.ZipFile(zipped) as contents:
            unpack(contents, zipped.parent)
        zipped.unlink()


def compile_program(work: Path, package: Path, executable: str,
                    source: str, runtime_folder: str, *, windowed: bool) -> None:
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm",
            "--onedir", "--noupx", "--name", executable,
            "--contents-directory", runtime_folder,
            "--distpath", str(work / "compiled"),
            "--workpath", str(work / "build" / executable),
            "--specpath", str(work / "spec"),
            "--windowed" if windowed else "--console"]
    if executable == "NSKRXEditWorker":
        args += ["--manifest", str(PATCHER / "tools/xedit_worker_utf8.manifest")]
    subprocess.run(args + [str(PATCHER / source)], cwd=PATCHER, check=True)
    compiled = work / "compiled" / executable
    expand_standard_library(compiled)
    for candidate in (compiled / (executable + ".exe"), compiled / runtime_folder):
        if not candidate.exists():
            raise FileNotFoundError(candidate)
    shutil.copytree(compiled, package, dirs_exist_ok=True)


def check_binary(folder: Path) -> str:
    executable = folder / "NuclearSunsetKoreanPatcher.exe"
    worker = folder / "NSKRXEditWorker.exe"
    for file in (executable, worker):
        if not file.is_file() or file.stat().st_size < 100_000:
            raise ValueError(f"Missing/invalid onedir executable: {file}")
    for name in ("_internal", "worker-runtime"):
        directory = folder / name
        if not directory.is_dir() or not any(directory.iterdir()):
            raise ValueError(f"Missing onedir runtime: {directory}")
        if (directory / "base_library.zip").exists():
            raise ValueError(f"Found nested base_library.zip: {directory}")
    run = subprocess.run([str(executable.resolve()), "--package-check"],
                         cwd=folder, capture_output=True, text=True, timeout=180,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if run.returncode:
        raise RuntimeError(f"Executable --package-check failed: "
                           f"{run.returncode}: {run.stdout[-1500:]} {run.stderr[-1500:]}")
    return run.stdout.strip()


def verify_release_assets(package: Path, catalog: dict) -> dict:
    if (catalog.get("version"), catalog.get("packaging")) != (VERSION, "folder"):
        raise ValueError("Candidate catalog version/packaging mismatch")
    payloads = validate_payloads(package, catalog)
    sources = verify_embedded_sources(package)
    for path in ("Backend/XEditLib.dll", "Backend/FalloutNV.Hardcoded.dat",
                 "Backend/icudtl.dat", "Backend/LICENSE"):
        if not (package / path).is_file():
            raise ValueError(f"Missing backend asset: {path}")
    return {"payloads_sha_verified": payloads, "python_sources_sha_verified": sources,
            "translation_records": sum(len(e.get("mappings", []))
                                       for e in catalog.get("files", [])),
            "file_entries": len(catalog.get("files", []))}


def package_zip(source: Path, target: Path, folders: tuple[str, ...]) -> None:
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED, compresslevel=6,
                         allowZip64=True) as output:
        for sub in folders:
            folder = source / sub if sub else source
            if not folder.is_dir():
                raise FileNotFoundError(folder)
            for file in sorted(folder.rglob("*")):
                if file.is_file():
                    relative = file.relative_to(source).as_posix()
                    checked_path(source, relative)
                    output.write(file, relative)


def build(*, base: Path, catalog_path: Path, work: Path,
          overlay: Path | None, notes: Path | None, skip_main_guard: bool = False) -> dict:
    patcher_zip, _, baseline = verify_baselines(base)
    current = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    valid = validate_place_corrections(baseline, current)
    final_catalog = keep_identity(baseline, current)
    upgrade = verify_previous_destinations(baseline, final_catalog)
    if upgrade["v1_0_4_changed_destinations"] < 55:
        raise ValueError("At least 55 verified place destinations must have upgrade aliases")
    if not skip_main_guard:
        git_info = assert_sources()
    else:
        git_info = {"testing_only": True}
    if work.exists():
        raise FileExistsError(f"Refusing to overwrite candidate work folder: {work}")
    work.mkdir(parents=True)
    package = work / "package"
    package.mkdir()
    with zipfile.ZipFile(patcher_zip) as contents:
        unpack(contents, package)
    overlaid = overlay_tree(package, overlay)
    synced = sync_local_payloads(package, catalog_path.parent, final_catalog)
    sources = embed_python_sources(package)
    write_catalog(package, final_catalog)
    metadata = verify_release_assets(package, final_catalog)
    # Recompile both programs, replacing only previous onedir Python runtimes.
    for rel in ("_internal", "worker-runtime"):
        shutil.rmtree(package / rel)
    for rel in ("NuclearSunsetKoreanPatcher.exe", "NSKRXEditWorker.exe"):
        (package / rel).unlink()
    compile_program(work, package, "NSKRXEditWorker", "nskr_xedit_worker.py",
                    "worker-runtime", windowed=False)
    compile_program(work, package, "NuclearSunsetKoreanPatcher", "nskr_gui.py",
                    "_internal", windowed=True)
    for relative, expected in sources.items():
        if sha256(PATCHER / relative) != expected:
            raise RuntimeError(f"Source changed during PyInstaller build: {relative}")
    shutil.copy2(PATCHER / "README.md", package / "README.md")
    install_doc = REPO / "translations/docs/main/korean-patch.md"
    if install_doc.is_file():
        shutil.copy2(install_doc, package / "INSTALL.md")
    if notes is not None:
        shutil.copy2(notes, package / "RELEASE-NOTES.md")
    elif (PATCHER / "docs/releases/v1.0.5.md").is_file():
        shutil.copy2(PATCHER / "docs/releases/v1.0.5.md", package / "RELEASE-NOTES.md")
    binary_result = check_binary(package)
    output = work / "output"
    output.mkdir()
    program_zip = output / "NuclearSunset-Korean-Patcher-v1.0.5-candidate.zip"
    data_zip = output / "NuclearSunset-TranslationData-v1.0.5-candidate.zip"
    package_zip(package, program_zip, ("",))
    package_zip(package, data_zip, ("TranslationData", "Licenses-and-Source"))
    extracted = work / "zip-test"
    extracted.mkdir()
    with zipfile.ZipFile(program_zip) as contents:
        unpack(contents, extracted)
    extracted_catalog = json.loads(
        (extracted / "TranslationData/catalog.json").read_text(encoding="utf-8"))
    if extracted_catalog != final_catalog:
        raise ValueError("ZIP extraction changed catalog data")
    zip_metadata = verify_release_assets(extracted, extracted_catalog)
    zip_check = check_binary(extracted)
    with zipfile.ZipFile(data_zip) as only_data:
        with zipfile.ZipFile(program_zip) as all_data:
            if any(only_data.read(name) != all_data.read(name)
                   for name in checked_zip(only_data)):
                raise ValueError("Standalone TranslationData differs from full package")
    outputs = [{"file": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
               for p in (program_zip, data_zip)]
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{item['sha256']}  {item['file']}\n" for item in outputs),
        encoding="ascii")
    report = {
        "release": "v1.0.5-candidate", "source_release": "v1.0.4",
        "source_sha256": {PATCHER_ZIP: PATCHER_SHA256, DATA_ZIP: DATA_SHA256},
        "working_catalog_sha256": sha256(catalog_path),
        "git": git_info, "validation": {**valid, **upgrade},
        "catalog": metadata, "zip_catalog": zip_metadata,
        "python_source_sha256": sources,
        "runtime_overlay_files": overlaid,
        "auto_synced_catalog_payloads": synced,
        "package_check": binary_result, "zip_package_check": zip_check,
        "artifacts": outputs
    }
    (output / "build-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def inspect_candidate(candidate: Path) -> dict:
    if candidate.is_dir():
        folder = candidate
        result = check_binary(folder)
        catalog = json.loads((folder / "TranslationData/catalog.json").read_text("utf-8"))
        info = verify_release_assets(folder, catalog)
    elif candidate.is_file() and candidate.suffix.casefold() == ".zip":
        with tempfile.TemporaryDirectory(prefix="nskr-folder-check-") as temp:
            folder = Path(temp)
            with zipfile.ZipFile(candidate) as contents:
                unpack(contents, folder)
            result = check_binary(folder)
            catalog = json.loads((folder / "TranslationData/catalog.json").read_text("utf-8"))
            info = verify_release_assets(folder, catalog)
    else:
        raise ValueError(f"Expected package folder or ZIP: {candidate}")
    return {"status": "package-check OK", "candidate": str(candidate),
            "execution": result, **info}


def preflight(base: Path, catalog_path: Path, overlay: Path | None) -> dict:
    _, _, original = verify_baselines(base)
    current = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    names = validate_place_corrections(original, current)
    merged = keep_identity(original, current)
    upgrade = verify_previous_destinations(original, merged)
    if upgrade["v1_0_4_changed_destinations"] < 55:
        raise ValueError("v1.0.4 place upgrade alias coverage incomplete")
    if overlay is not None and not overlay.is_dir():
        raise ValueError(f"Overlay directory not found: {overlay}")
    git = None
    try:
        git = assert_sources()
    except (ValueError, subprocess.CalledProcessError) as exc:
        git = {"build_blocked": str(exc)}
    return {"status": "preflight OK", "official_archive_hashes_verified": True,
            "program_layout": "onedir", "catalog_sha256": sha256(catalog_path),
            **names, **upgrade, "candidate_file_entries": len(merged["files"]),
            "candidate_mappings": sum(len(e.get("mappings", []))
                                      for e in merged["files"]),
            "main_integration": git}


def check_baseline_executable(base: Path) -> dict:
    patcher_zip, _, reference = verify_baselines(base)
    with tempfile.TemporaryDirectory(prefix="nskr-v1.0.4-onedir-check-") as folder:
        extracted = Path(folder)
        with zipfile.ZipFile(patcher_zip) as contents:
            unpack(contents, extracted)
        if json.loads((extracted / "TranslationData/catalog.json").read_text(
                encoding="utf-8")) != reference:
            raise ValueError("Official archive catalog mismatch after unpack")
        check = check_binary(extracted)
    return {"status": "official v1.0.4 onedir --package-check OK",
            "archive_sha256": PATCHER_SHA256, "execution": check}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    task = parser.add_mutually_exclusive_group(required=True)
    task.add_argument("--preflight", action="store_true")
    task.add_argument("--build", action="store_true")
    task.add_argument("--package-check", action="store_true")
    task.add_argument("--baseline-check", action="store_true",
                      help="Execute --package-check on official v1.0.4 onedir ZIP")
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--work", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--overlay-dir", type=Path)
    parser.add_argument("--release-notes", type=Path)
    parser.add_argument("--candidate", type=Path)
    options = parser.parse_args()
    if options.package_check:
        if options.candidate is None:
            parser.error("--package-check requires --candidate ZIP_OR_FOLDER")
        result = inspect_candidate(options.candidate)
    elif options.baseline_check:
        result = check_baseline_executable(options.base)
    elif options.preflight:
        result = preflight(options.base, options.catalog, options.overlay_dir)
    else:
        result = build(base=options.base, catalog_path=options.catalog,
                       work=options.work, overlay=options.overlay_dir,
                       notes=options.release_notes)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
