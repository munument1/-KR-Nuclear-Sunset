"""Build the v1.0.10 full onedir patcher from official v1.0.9 release bytes.

Never mutates the original archive, MO2, installs or savegames.
Python patcher and tNVSE DLL are rebuilt from pinned sources;
XEditLib and all other runtime payloads remain byte-for-byte unchanged.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from tools.apply_issue27_native_save_title import apply as apply_native_overlay
from tools.build_v1_0_5_folder_release import (
    checked_zip, checked_path, unpack, compile_program, check_binary,
    validate_payloads, package_zip,
)

VERSION = '1.0.10'
BASE_NAME = 'NuclearSunset-Korean-Patcher-v1.0.9.zip'


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_checksum(archive: Path, sums: Path):
    expected = []
    for line in sums.read_text(encoding='utf-8-sig').splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].lstrip('*') == archive.name:
            expected.append(parts[0].lower())
    if expected != [sha(archive)]:
        raise ValueError('Official v1.0.9 baseline SHA256 missing or mismatched')


def build(base: Path, sums: Path, work: Path, dll: Path):
    if nskr.VERSION != VERSION:
        raise ValueError('nskr.VERSION must be 1.0.10')
    if sys.platform != 'win32':
        raise EnvironmentError('The onedir patcher must be built on Windows')
    base, sums, work, dll = (Path(x).resolve() for x in (base, sums, work, dll))
    if base.name != BASE_NAME:
        raise ValueError('Unexpected baseline archive name')
    verify_release_checksum(base, sums)
    if work.exists():
        raise FileExistsError(work)
    package = work / 'package'
    package.mkdir(parents=True)
    with zipfile.ZipFile(base) as z:
        original_paths = checked_zip(z)
        unpack(z, package)
        reference_hashes = {
            name: sha(package / name) for name in original_paths
        }
    catalog_path = package / 'TranslationData/catalog.json'
    prior_catalog = nskr.read_json(catalog_path)
    if (prior_catalog.get('version'), prior_catalog.get('target_modlist')) != (
            '1.0.9', 'nuclear-sunset-ttw'):
        raise ValueError('Unrecognized v1.0.9 release catalog')
    catalog = prior_catalog
    if not dll.is_file() or dll.stat().st_size < 100000:
        raise ValueError('Missing native DLL')
    dll_sha = sha(dll)
    with dll.open('rb') as handle:
        if handle.read(2) != b'MZ':
            raise ValueError('Not PE DLL')
        handle.seek(0x3c)
        off = int.from_bytes(handle.read(4),'little')
        if not 0x40 <= off <= 4096:
            raise ValueError('Invalid PE offset')
        handle.seek(off)
        if handle.read(4) != bytes([80, 69, 0, 0]) or int.from_bytes(handle.read(2),'little') != 0x14c:
            raise ValueError('Not PE Win32 x86')
    native_changed = []
    for asset in catalog['font_bundle']['assets'] + [
            entry for mod in catalog['runtime_mods'] for entry in mod['files']]:
        if asset['path'].casefold().replace(chr(92), '/').endswith('/tnvse.dll'):
            rel = 'TranslationData/' + asset['payload']
            dest = package / rel
            if not dest.is_file():
                raise FileNotFoundError(dest)
            shutil.copy2(dll, dest)
            asset['payload_sha256'] = sha(dest)
            native_changed.append(rel)
    if len(native_changed) != 1:
        raise ValueError('Expected one tNVSE payload, got ' + repr(native_changed))
    native_source_rel = (
        'Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE/'
        'tnvse/Src/font/font_text_geometry.cpp')
    native_source = package / native_source_rel
    if not native_source.is_file():
        raise FileNotFoundError(native_source)
    native_source.write_bytes(apply_native_overlay(native_source.read_bytes()))
    native_source_sha = sha(native_source)
    catalog['version'] = VERSION
    catalog['channel'] = 'release'
    catalog['translation_ready'] = True
    catalog['game_validation'] = 'not_run_v1.0.10_same_save'
    nskr.write_json(catalog_path, catalog)
    asset_count = validate_payloads(package, catalog)

    # Preserve reviewed XEditLib and unrelated native binaries.
    for relative in ('NuclearSunsetKoreanPatcher.exe', 'NSKRXEditWorker.exe'):
        (package / relative).unlink()
    for relative in ('_internal', 'worker-runtime'):
        shutil.rmtree(package / relative)

    snap = package / 'Licenses-and-Source/NuclearSunset-Patcher-v1.0.10'
    if snap.exists():
        raise FileExistsError(snap)
    sources = sorted(ROOT.glob('nskr*.py')) + [ROOT / 'ns_inventory.py']
    sources += sorted((ROOT / 'tools').glob('*.py'))
    hashes = {}
    for source in sources:
        name = source.relative_to(ROOT).as_posix()
        target = snap / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[name] = sha(source)
    shutil.copytree(ROOT / 'tests', snap / 'tests',
                    ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT / 'native', snap / 'native',
                    ignore=shutil.ignore_patterns('__pycache__','*.exe','*.obj','*.bin','*.cmd','*.log'))
    (snap / 'SOURCE-SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n',
                                            encoding='utf-8')
    for source, name in (
        (ROOT / 'README.md', 'README.md'),
        (ROOT / 'docs/releases/v1.0.10.md', 'RELEASE-NOTES.md'),
        (ROOT.parent / 'translations/docs/main/korean-patch.md', 'INSTALL.md'),
    ):
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, package / name)

    compile_program(work, package, 'NSKRXEditWorker', 'nskr_xedit_worker.py',
                    'worker-runtime', windowed=False)
    compile_program(work, package, 'NuclearSunsetKoreanPatcher', 'nskr_gui.py',
                    '_internal', windowed=True)
    for src in sources:
        name = src.relative_to(ROOT).as_posix()
        if sha(src) != hashes[name] or sha(snap / name) != hashes[name]:
            raise RuntimeError('Source changed during compilation: ' + name)
    binary_status = check_binary(package)
    permitted = {
        'TranslationData/catalog.json', 'README.md', 'RELEASE-NOTES.md',
        'INSTALL.md',
        'NuclearSunsetKoreanPatcher.exe', 'NSKRXEditWorker.exe',
        native_source_rel, *native_changed,
    }
    for name, original_sha in reference_hashes.items():
        if name in permitted or name.startswith(('_internal/', 'worker-runtime/')):
            continue
        if sha(package / name) != original_sha:
            raise ValueError('Unexpected modification of baseline payload: ' + name)
    output = work / 'output'
    output.mkdir()
    full = output / f'NuclearSunset-Korean-Patcher-v{VERSION}.zip'
    data = output / f'NuclearSunset-TranslationData-v{VERSION}.zip'
    package_zip(package, full, ('',))
    package_zip(package, data, ('TranslationData', 'Licenses-and-Source'))
    with zipfile.ZipFile(full) as z, zipfile.ZipFile(data) as dz:
        if z.testzip() or dz.testzip():
            raise ValueError('Release ZIP CRC failure')
        for name in checked_zip(dz):
            if dz.read(name) != z.read(name):
                raise ValueError('Standalone/full release mismatch: ' + name)
        extracted = work / 'unpacked'
        extracted.mkdir()
        unpack(z, extracted)
    extracted_status = check_binary(extracted)
    artifacts = [
        {'file': a.name, 'bytes': a.stat().st_size, 'sha256': sha(a)}
        for a in (full, data)
    ]
    (output / 'SHA256SUMS.txt').write_text(
        ''.join(f"{a['sha256']}  {a['file']}\n" for a in artifacts),
        encoding='ascii')
    report = {
        'version': VERSION,
        'reference_sha256': sha(base),
        'original_untouched_payloads_checked': len(reference_hashes),
        'catalog_record_edits': 0,
        'native_binary_replaced': True,
        'native_sha256': dll_sha,
        'native_source_sha256': native_source_sha,
        'native_payloads': native_changed,
        'verified_runtime_assets': asset_count,
        'binary_selfcheck': binary_status,
        'extracted_binary_selfcheck': extracted_status,
        'source_sha256_count': len(hashes),
        'source_commit': subprocess.check_output(
            ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'game_validation': 'not_run',
        'artifacts': artifacts,
    }
    (output / 'build-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))  # Windows CI console may be cp1252


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('--base', required=True, type=Path)
    arg.add_argument('--checksums', required=True, type=Path)
    arg.add_argument('--work', required=True, type=Path)
    arg.add_argument('--dll', required=True, type=Path)
    a = arg.parse_args()
    build(a.base, a.checksums, a.work, a.dll)
