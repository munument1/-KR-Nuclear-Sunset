"""Build an unpublished #37 candidate while preserving v1.1.3 game assets."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from tools.build_v1_0_5_folder_release import (
    checked_zip, unpack, compile_program, check_binary, validate_payloads, package_zip,
)

BASE_SHA = '98a33551c77bbdab465f57df1cd814469c8fdc761bb81718b7b8d7a4641936fb'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def build(base, work):
    base, work = Path(base).resolve(), Path(work).resolve()
    if nskr.VERSION != '1.1.4' or sha(base) != BASE_SHA:
        raise ValueError('Pinned v1.1.3 release / v1.1.4 source required')
    if work.exists():
        raise FileExistsError(work)
    package = work / 'package'
    package.mkdir(parents=True)
    with zipfile.ZipFile(base) as archive:
        if archive.testzip():
            raise ValueError('Baseline ZIP CRC failure')
        unpack(archive, package)
        baseline = {name: sha(package / name) for name in checked_zip(archive)}
    previous = package / 'Licenses-and-Source/NuclearSunset-Patcher-v1.1.3'
    sources = sorted(ROOT.glob('nskr*.py')) + [ROOT / 'ns_inventory.py']
    changed = {p.name for p in sources if sha(p) != sha(previous / p.name)}
    if changed != {'nskr.py', 'nskr_medical_bag.py'}:
        raise ValueError(f'Unexpected application source changes: {changed}')
    if (previous / 'nskr.py').read_text(encoding='utf-8').replace(
            'VERSION = "1.1.3"', 'VERSION = "1.1.4"') != (ROOT / 'nskr.py').read_text(encoding='utf-8'):
        raise ValueError('nskr.py may only change the version')
    catalog_path = package / 'TranslationData/catalog.json'
    catalog = nskr.read_json(catalog_path)
    if (catalog['version'], catalog['channel']) != ('1.1.3', 'release'):
        raise ValueError('Unexpected baseline catalog')
    catalog['version'] = '1.1.4'
    nskr.write_json(catalog_path, catalog)
    payloads = validate_payloads(package, catalog)
    snapshot = package / 'Licenses-and-Source/NuclearSunset-Patcher-v1.1.4'
    snapshot.mkdir()
    hashes = {}
    for source in sources + sorted((ROOT / 'tools').glob('*.py')):
        relative = source.relative_to(ROOT)
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[relative.as_posix()] = sha(source)
    shutil.copytree(ROOT / 'tests', snapshot / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
    (snapshot / 'SOURCE-SHA256.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
    for source, name in (
        (ROOT / 'README.md', 'README.md'),
        (ROOT / 'docs/releases/v1.1.4.md', 'RELEASE-NOTES.md'),
        (ROOT.parent / 'translations/docs/main/korean-patch.md', 'INSTALL.md'),
    ):
        shutil.copy2(source, package / name)
    runtime = (package / '_internal').resolve()
    if not runtime.is_relative_to(work):
        raise ValueError('Runtime cleanup escaped build workspace')
    shutil.rmtree(runtime)
    (package / 'NuclearSunsetKoreanPatcher.exe').unlink()
    compile_program(work, package, 'NuclearSunsetKoreanPatcher', 'nskr_gui.py', '_internal', windowed=True)
    check = check_binary(package)
    for relative, digest in hashes.items():
        if sha(ROOT / relative) != digest or sha(snapshot / relative) != digest:
            raise ValueError('Source changed during build: ' + relative)
    allowed = {'TranslationData/catalog.json', 'README.md', 'RELEASE-NOTES.md',
               'INSTALL.md', 'NuclearSunsetKoreanPatcher.exe'}
    for name, digest in baseline.items():
        if name in allowed or name.startswith('_internal/'):
            continue
        if sha(package / name) != digest:
            raise ValueError('Unrelated baseline file changed: ' + name)
    output = work / 'output'
    output.mkdir()
    full = output / 'NuclearSunset-Korean-Patcher-v1.1.4-candidate.zip'
    package_zip(package, full, ('',))
    with zipfile.ZipFile(full) as archive:
        if archive.testzip():
            raise ValueError('Candidate ZIP CRC failure')
        extracted = work / 'unpacked'
        extracted.mkdir()
        unpack(archive, extracted)
    extracted_check = check_binary(extracted)
    artifact = dict(file=full.name, sha256=sha(full), bytes=full.stat().st_size)
    (output / 'SHA256SUMS.txt').write_text(artifact['sha256'] + '  ' + full.name + '\n', encoding='ascii')
    report = dict(version='1.1.4', channel='unpublished_candidate', base_sha256=BASE_SHA,
                  changed_application_sources=sorted(changed), payloads_verified=payloads,
                  baseline_files_checked=len(baseline), binary_selfcheck=check,
                  extracted_binary_selfcheck=extracted_check, gameplay_tested=False, artifact=artifact)
    nskr.write_json(output / 'build-report.json', report)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    options = parser.parse_args()
    build(options.base, options.work)
