"""Build the v1.1.0 full onedir patcher from official v1.0.10 release bytes.

Never mutates the original archive, MO2, installs or savegames.
Requires renderer in-game evidence and medical bag static verification.
Changes to other assets require an exact checksum-declared medical overlay.
"""
from __future__ import annotations
import argparse
import difflib
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
from tools.build_v1_0_5_folder_release import (
    checked_zip, checked_path, unpack, compile_program, check_binary,
    validate_payloads, package_zip,
)

VERSION = '1.1.0'
BASE_NAME = 'NuclearSunset-Korean-Patcher-v1.0.10.zip'
BASE_SHA256 = '89cf725b1d2cdf4f980d27f05b820fb07c16ad92a79364fc883917d283679f11'
RENDERER_DLL_SHA256 = 'bab7c5ae2cd9e2b3e8fe208d902cf3b02c229f75a1514605ead7b98818c35384'
# This hash records the official checkout used to create the isolated staging copy.
SOURCE_COMMIT = 'c0286836b1230c08ce8c0aa10b9ac7b42af30c7e'
NATIVE_REL = 'Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE/tnvse/Src/game/'
BASE_GAME_HOOKS_SHA256 = '33df7fa20e883c387aeed1974b5029ad44489544853f534fe574a77b29b02271'


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_checksum(archive: Path, sums: Path):
    expected = []
    for line in sums.read_text(encoding='utf-8-sig').splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].lstrip('*') == archive.name:
            expected.append(parts[0].lower())
    if expected != [BASE_SHA256] or sha(archive) != BASE_SHA256:
        raise ValueError('Official v1.0.10 baseline SHA256 missing or mismatched')


def load_proof(path: Path, baseline: Path, dll: Path):
    """Manual gate: does not claim that static checks equal in-game proof."""
    if not path.is_file():
        raise FileNotFoundError(f'Validation evidence missing: {path}')
    proof = json.loads(path.read_text(encoding='utf-8-sig'))
    expected = {
        'version': VERSION,
        'baseline_sha256': BASE_SHA256,
        'renderer_dll_sha256': sha(dll),
        'renderer_game_verified': True,
        'medical_static_verified': True,
    }
    for key, value in expected.items():
        if proof.get(key) != value:
            raise ValueError(f'Release evidence does not approve {key}')
    for field in ('renderer_evidence', 'medical_static_evidence'):
        if not isinstance(proof.get(field), str) or len(proof[field].strip()) < 12:
            raise ValueError(f'Missing reviewable verification reference: {field}')
    if not isinstance(proof.get('medical_game_verified'), bool):
        raise ValueError('Declare medical_game_verified explicitly, even if false')
    for key in ('source_changes', 'package_changes'):
        if not isinstance(proof.get(key), list):
            raise ValueError(f'Missing explicit {key} list')
    if not proof['source_changes'] and not proof['package_changes']:
        raise ValueError('Medical bag fix must name and verify changed source or payload')
    return proof


def apply_medical_changes(package: Path, overlay: Path, proof: dict):
    """Apply only review-approved, before/after SHA-pinned file replacements."""
    permitted = set()
    seen_sources = set()
    for item in proof['source_changes']:
        relative = item['path']
        if relative in seen_sources:
            raise ValueError(f'Duplicate medical source declaration: {relative}')
        seen_sources.add(relative)
        if not (relative.startswith(('nskr_', 'tools/', 'tests/'))
                and relative.endswith('.py')):
            raise ValueError(f'Medical source path outside patcher modules: {relative}')
        checked_path(ROOT, relative)
        current = ROOT / relative
        previous = package / ('Licenses-and-Source/NuclearSunset-Patcher-v1.0.10/' + relative)
        baseline_sha = sha(previous) if previous.is_file() else None
        if (not current.is_file() or current.is_symlink()
                or sha(current) != item['after_sha256']
                or baseline_sha != item['before_sha256']
                or item['after_sha256'] == item['before_sha256']):
            raise ValueError(f'Unverified medical source change: {relative}')
    for item in proof['package_changes']:
        relative = item['path']
        if not relative.startswith('TranslationData/'):
            raise ValueError(f'Medical payload path must stay in TranslationData: {relative}')
        checked_path(package, relative)
        current = package / relative
        replacement = checked_path(overlay, relative)
        if (not current.is_file() or not replacement.is_file()
                or sha(current) != item['before_sha256']
                or sha(replacement) != item['after_sha256']
                or item['after_sha256'] == item['before_sha256']):
            raise ValueError(f'Unverified medical payload change: {relative}')
        shutil.copy2(replacement, current)
        permitted.add(relative)
    return permitted


def build(base: Path, sums: Path, work: Path, dll: Path,
          medical_proof: Path, medical_overlay: Path):
    if nskr.VERSION != VERSION:
        raise ValueError('nskr.VERSION must be 1.1.0')
    if sys.platform != 'win32':
        raise EnvironmentError('The onedir patcher must be built on Windows')
    base, sums, work, dll, medical_proof, medical_overlay = (
        Path(x).resolve() for x in
        (base, sums, work, dll, medical_proof, medical_overlay))
    if base.name != BASE_NAME:
        raise ValueError('Unexpected baseline archive name')
    verify_release_checksum(base, sums)
    if not dll.is_file() or sha(dll) != RENDERER_DLL_SHA256:
        raise ValueError('Exact test-verified renderer DLL hash mismatch')
    proof = load_proof(medical_proof, base, dll)
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
    medical_changed = apply_medical_changes(package, medical_overlay, proof)
    catalog_path = package / 'TranslationData/catalog.json'
    prior_catalog = nskr.read_json(catalog_path)
    if (prior_catalog.get('version'), prior_catalog.get('target_modlist')) != (
            '1.0.10', 'nuclear-sunset-ttw'):
        raise ValueError('Unrecognized v1.0.10 release catalog')
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
    base_hooks_path = package / NATIVE_REL / 'game_hooks.cpp'
    if not base_hooks_path.is_file() or sha(base_hooks_path) != BASE_GAME_HOOKS_SHA256:
        raise ValueError('Packaged v1.0.10 tNVSE game_hooks.cpp is not the expected baseline')
    original_hooks = base_hooks_path.read_text(encoding='utf-8-sig')
    native_sources = {}
    for name in ('game_hooks.cpp', 'save_level_tile_fix.h'):
        source = ROOT / 'native/tnvse/Src/game' / name
        target = package / NATIVE_REL / name
        if not source.is_file():
            raise FileNotFoundError(source)
        if name == 'game_hooks.cpp' and not target.is_file():
            raise FileNotFoundError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        native_sources[NATIVE_REL + name] = sha(target)
    changed_hooks = base_hooks_path.read_text(encoding='utf-8-sig')
    new_header = (package / NATIVE_REL / 'save_level_tile_fix.h').read_text(encoding='utf-8-sig')
    patch_lines = list(difflib.unified_diff(
        original_hooks.splitlines(keepends=True),
        changed_hooks.splitlines(keepends=True),
        fromfile='a/tnvse/Src/game/game_hooks.cpp',
        tofile='b/tnvse/Src/game/game_hooks.cpp'))
    patch_lines.extend(difflib.unified_diff(
        [], new_header.splitlines(keepends=True),
        fromfile='/dev/null', tofile='b/tnvse/Src/game/save_level_tile_fix.h'))
    renderer_patch_path = package / ('Licenses-and-Source/'
        'tNVSE-71-KR-UI-source/renderer-v1.1.0.patch')
    renderer_patch_path.write_text(''.join(patch_lines), encoding='utf-8')
    native_source_rel = NATIVE_REL + 'game_hooks.cpp'
    native_source_sha = native_sources[native_source_rel]
    catalog['version'] = VERSION
    catalog['channel'] = 'release'
    catalog['translation_ready'] = True
    catalog['game_validation'] = (
        'renderer_game_verified_medical_game_verified_v1.1.0' if proof['medical_game_verified']
        else 'renderer_game_verified_medical_static_verified_game_not_run_v1.1.0')
    nskr.write_json(catalog_path, catalog)
    asset_count = validate_payloads(package, catalog)

    # Preserve reviewed XEditLib and unrelated native binaries.
    for relative in ('NuclearSunsetKoreanPatcher.exe', 'NSKRXEditWorker.exe'):
        (package / relative).unlink()
    for relative in ('_internal', 'worker-runtime'):
        shutil.rmtree(package / relative)

    snap = package / 'Licenses-and-Source/NuclearSunset-Patcher-v1.1.0'
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
        (ROOT / 'docs/releases/v1.1.0.md', 'RELEASE-NOTES.md'),
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
        *native_sources, *native_changed, *medical_changed,
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
        'catalog_record_edits': None if 'TranslationData/catalog.json' in medical_changed else 0,
        'catalog_before_sha256': reference_hashes['TranslationData/catalog.json'],
        'catalog_after_sha256': sha(catalog_path),
        'native_binary_replaced': True,
        'native_sha256': dll_sha,
        'native_source_sha256': native_source_sha,
        'native_sources_sha256': native_sources,
        'native_source_patch_sha256': sha(renderer_patch_path),
        'medical_change_paths': sorted(medical_changed),
        'medical_source_changes': proof['source_changes'],
        'renderer_game_verified': proof['renderer_game_verified'],
        'medical_static_verified': proof['medical_static_verified'],
        'medical_game_verified': proof['medical_game_verified'],
        'native_payloads': native_changed,
        'verified_runtime_assets': asset_count,
        'binary_selfcheck': binary_status,
        'extracted_binary_selfcheck': extracted_status,
        'source_sha256_count': len(hashes),
        'source_base_commit': SOURCE_COMMIT,
        'source_stage_isolated': True,
        'game_validation': catalog['game_validation'],
        'artifacts': artifacts,
    }
    (output / 'build-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))  # Windows CI console may be cp1252


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('--base', required=True, type=Path)
    arg.add_argument('--checksums', required=True, type=Path)
    arg.add_argument('--work', type=Path)
    arg.add_argument('--dll', required=True, type=Path)
    arg.add_argument('--medical-proof', type=Path)
    arg.add_argument('--medical-overlay', type=Path)
    arg.add_argument('--preflight', action='store_true',
                     help='Verify pinned v1.0.10 and renderer inputs without building/publishing')
    a = arg.parse_args()
    if a.preflight:
        verify_release_checksum(a.base, a.checksums)
        if nskr.VERSION != VERSION:
            raise ValueError('Expected staged nskr.VERSION=1.1.0')
        if sha(a.dll) != RENDERER_DLL_SHA256:
            raise ValueError('Renderer test DLL mismatch')
        with zipfile.ZipFile(a.base) as original:
            checked_zip(original)
            if original.testzip():
                raise ValueError('Official baseline ZIP CRC failure')
            if 'TranslationData/catalog.json' not in original.namelist():
                raise ValueError('Baseline catalog missing')
            for name in ('game_hooks.cpp', 'save_level_tile_fix.h'):
                if not (ROOT / 'native/tnvse/Src/game' / name).is_file():
                    raise FileNotFoundError(f'Staged native source missing: {name}')
        print(json.dumps({
            'version': VERSION,
            'baseline_sha256': BASE_SHA256,
            'renderer_dll_sha256': RENDERER_DLL_SHA256,
            'native_sources_staged': True,
            'medical_validation': 'not_supplied',
            'ready_for_release': False,
        }, indent=2))
    else:
        if not a.work or not a.medical_proof or not a.medical_overlay:
            arg.error('--work, --medical-proof and --medical-overlay are required for --build')
        build(a.base, a.checksums, a.work, a.dll,
              a.medical_proof, a.medical_overlay)
