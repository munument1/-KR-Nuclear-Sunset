"""Build the v1.0.9 full onedir patcher from official v1.0.8 release bytes.

Never mutates the original archive, MO2, installs or savegames.
Python patcher is recompiled from this exact commit; tNVSE/XEdit binaries
are retained byte-for-byte from the verified baseline.
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
from nskr_issue20_casings import align_spare_casings
from tools.build_v1_0_5_folder_release import (
    checked_zip, checked_path, unpack, compile_program, check_binary,
    validate_payloads, package_zip,
)

VERSION = '1.0.9'
BASE_NAME = 'NuclearSunset-Korean-Patcher-v1.0.8.zip'


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_checksum(archive: Path, sums: Path):
    expected = []
    for line in sums.read_text(encoding='utf-8-sig').splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].lstrip('*') == archive.name:
            expected.append(parts[0].lower())
    if expected != [sha(archive)]:
        raise ValueError('Official v1.0.8 baseline SHA256 missing or mismatched')


def build(base: Path, sums: Path, work: Path):
    if nskr.VERSION != VERSION:
        raise ValueError('nskr.VERSION must be 1.0.9')
    if sys.platform != 'win32':
        raise EnvironmentError('The onedir patcher must be built on Windows')
    base, sums, work = (Path(x).resolve() for x in (base, sums, work))
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
            '1.0.8', 'nuclear-sunset-ttw'):
        raise ValueError('Unrecognized v1.0.8 release catalog')
    catalog, edits = align_spare_casings(prior_catalog)
    if len(edits) != 7 or align_spare_casings(catalog)[1]:
        raise ValueError('Expected seven reviewed #20 casing translations')
    catalog['version'] = VERSION
    catalog['channel'] = 'release'
    catalog['translation_ready'] = True
    catalog['game_validation'] = 'not_run_v1.0.9_same_save'
    nskr.write_json(catalog_path, catalog)
    asset_count = validate_payloads(package, catalog)

    # Keep reviewed tNVSE DLL and XEditLib backend from v1.0.8 untouched.
    for relative in ('NuclearSunsetKoreanPatcher.exe', 'NSKRXEditWorker.exe'):
        (package / relative).unlink()
    for relative in ('_internal', 'worker-runtime'):
        shutil.rmtree(package / relative)

    snap = package / 'Licenses-and-Source/NuclearSunset-Patcher-v1.0.9'
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
        (ROOT / 'docs/releases/v1.0.9.md', 'RELEASE-NOTES.md'),
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
        'catalog_record_edits': edits,
        'unchanged_native_binary_retained': True,
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
    a = arg.parse_args()
    build(a.base,a.checksums,a.work)
