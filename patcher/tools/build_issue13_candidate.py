"""Build a local issue #13 candidate using unchanged official v1.0.6 resources.

No publishing, installation, source overwrites or game execution. Rebuilds both
programs; preserves the complete latest TranslationData and vendor resources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_v1_0_5_folder_release import (
    checked_zip, checked_path, compile_program, check_binary, package_zip,
    validate_payloads,
)
from nskr_issue13 import name_entries
import nskr

BASE_SHA256 = '496cc462eb4ad82caa11f0e169fb68a1653b2d295fa88afb80416c943f8fe36a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(base, work):
    base, work = Path(base).resolve(), Path(work).resolve()
    if sha(base) != BASE_SHA256:
        raise ValueError('Expected the exact official v1.0.6 full patcher ZIP')
    if work.exists():
        raise FileExistsError(work)
    if work.is_relative_to(Path(r'C:\Modlists').resolve()):
        raise ValueError('Candidate work must be outside game installations')
    package = work / 'package'
    package.mkdir(parents=True)
    with zipfile.ZipFile(base) as archive:
        entries = checked_zip(archive)
        original_data = {n: hashlib.sha256(archive.read(n)).hexdigest()
                         for n in entries if n.startswith('TranslationData/')}
        for name in entries:
            if name.startswith(('_internal/', 'worker-runtime/')) or name in {
                    'NuclearSunsetKoreanPatcher.exe', 'NSKRXEditWorker.exe'}:
                continue
            target = checked_path(package, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(archive.read(name))
    # The candidate adds runtime behavior in Python, not changes to dictionaries,
    # UI ESPs, tNVSE DLLs, fonts, or settings. The sOr v1.0.6 repair is retained.
    if any(sha(package / name) != expected for name, expected in original_data.items()):
        raise ValueError('Official v1.0.6 TranslationData changed')
    catalog = json.loads((package / 'TranslationData/catalog.json').read_text(encoding='utf-8'))
    validate_payloads(package, catalog)
    sources = sorted(ROOT.glob('nskr*.py')) + [ROOT / 'ns_inventory.py']
    sources += [ROOT / 'tools' / name for name in (
        'loose_translation.py', 'audit_issue11_compiled_scripts.py',
        'tes4_text_scan.py', 'build_issue13_candidate.py', 'audit_issue13_sources.py',
        'build_v1_0_5_folder_release.py')]
    snapshot = package / 'Licenses-and-Source' / ('NuclearSunset-Patcher-v' + nskr.VERSION)
    manifest = {}
    for source in sources:
        relative = source.relative_to(ROOT).as_posix()
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest[relative] = sha(source)
    (snapshot / 'SOURCE-SHA256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    shutil.copy2(ROOT / 'docs/issue13-findings-20261023.md', package / 'ISSUE13-READ-ME.md')
    compile_program(work, package, 'NSKRXEditWorker', 'nskr_xedit_worker.py',
                    'worker-runtime', windowed=False)
    compile_program(work, package, 'NuclearSunsetKoreanPatcher', 'nskr_gui.py',
                    '_internal', windowed=True)
    binary_check = check_binary(package)
    for source in sources:
        if sha(source) != manifest[source.relative_to(ROOT).as_posix()]:
            raise ValueError('Source changed during candidate build')
    if any(sha(package / name) != expected for name, expected in original_data.items()):
        raise ValueError('Resources changed during candidate build')
    output = work / 'output'
    output.mkdir()
    destination = output / ('NuclearSunset-Korean-Patcher-v' + nskr.VERSION + '.zip')
    package_zip(package, destination, ('',))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError('Candidate archive CRC verification failed')
    report = {'candidate': nskr.VERSION, 'base': 'v1.0.6',
              'base_sha256': BASE_SHA256, 'zip': destination.name,
              'sha256': sha(destination), 'bytes': destination.stat().st_size,
              'translation_data_files_unchanged': len(original_data),
              'source_snapshot': manifest, 'package_check': binary_check,
              'name_operand_mappings': sum(len(e['mappings']) for e in name_entries()),
              'in_game_validation': 'not_run', 'published': False}
    (output / 'build-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (output / 'SHA256SUMS.txt').write_text(report['sha256'] + '  ' + destination.name + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.base, args.work), ensure_ascii=False, indent=2))
