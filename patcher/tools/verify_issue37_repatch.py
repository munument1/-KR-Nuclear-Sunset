"""Reproduce #37 with shipped executables in a detached one-plugin MO2 fixture."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
import nskr_medical_bag as medical
from nskr_compiled_scpt import _walk, _slots, _decode_record, _encode_record, _with_payload

REPORTER_SHA = '00f6027550251ee498063205c2ddd71c8162fdc421876c75b42690cb10327270'


def verify(baseline, candidate, mo2, work):
    baseline, candidate, mo2, work = (p.resolve() for p in (baseline, candidate, mo2, work))
    if work.exists():
        raise FileExistsError(work)
    installation = nskr.Installation(mo2, all_installed=True)
    source = installation.mods / medical.PROVIDER / medical.RELATIVE_PATH
    original = source.read_bytes()
    if nskr.sha256(source) != medical.ORIGINAL_SHA256:
        raise ValueError('Exact reviewed English Aid Addon required')
    fixture = work / 'MO2'
    plugin = fixture / 'mods' / medical.PROVIDER / medical.RELATIVE_PATH
    plugin.parent.mkdir(parents=True)
    plugin.write_bytes(original)
    (fixture / 'ModOrganizer.ini').write_text(
        '[General]\ngameName=TTW\ngamePath=' + str(installation.game) + '\n', encoding='utf-8')
    runs = []

    def run(package, label, failure=False):
        catalog = nskr.read_json(package / 'TranslationData/catalog.json')
        catalog['files'] = [e for e in catalog['files']
                            if e['path'].casefold() == medical.RELATIVE_PATH.casefold()]
        if len(catalog['files']) != 1:
            raise ValueError('Expected exactly one Aid Addon catalog entry')
        for key in ('font_bundle', 'asset_bundle', 'runtime_mods'):
            catalog.pop(key, None)
        catalog_dir = work / (label + '-catalog')
        catalog_dir.mkdir()
        nskr.write_json(catalog_dir / 'catalog.json', catalog)
        output = work / label
        result = subprocess.run(
            [str(package / 'NuclearSunsetKoreanPatcher.exe'), '--self-test', str(fixture),
             '--catalog', str(catalog_dir), '--output', str(output)],
            capture_output=True, text=True, timeout=180,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        row = dict(label=label, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
        runs.append(row)
        if failure:
            if result.returncode == 0 or output.exists() or output.with_name(label + '.report.json').exists():
                raise AssertionError('Unreviewed input must fail without publishing Output')
            error = (package / 'NuclearSunset-self-test.error.log').read_text(encoding='utf-8')
            if 'Script hash changed, refusing unsafe edit: SCPTUpdateDummyNamesCall' not in error:
                raise AssertionError(error)
            return None
        if result.returncode:
            raise AssertionError(str(row))
        target = output / 'mods' / medical.PROVIDER / medical.RELATIVE_PATH
        if nskr.sha256(target) != REPORTER_SHA:
            raise AssertionError('Output differs from reporter-provided SHA-256')
        report = nskr.read_json(output.with_name(label + '.report.json'))
        entry = next(e for e in report['files'] if e['path'] == medical.RELATIVE_PATH)
        row.update(output_sha256=nskr.sha256(target), medical_bag_dynamic=entry['medical_bag_dynamic'])
        return target

    prior = run(baseline, 'baseline-original')
    shutil.copy2(prior, plugin)
    run(baseline, 'baseline-repeat', failure=True)
    repeated = run(candidate, 'candidate-repeat')
    if {r['status'] for r in runs[-1]['medical_bag_dynamic'].values()} != {'already_translated'}:
        raise AssertionError('Expected verification of both previously translated scripts')
    shutil.copy2(repeated, plugin)
    run(candidate, 'candidate-second-repeat')
    plugin.write_bytes(original)
    run(candidate, 'candidate-original')
    if {r['status'] for r in runs[-1]['medical_bag_dynamic'].values()} != {'translated'}:
        raise AssertionError('Expected translation of both original scripts')

    def tamper(header, payload):
        if header[:4] != b'SCPT':
            return payload
        slots = list(_slots(_decode_record(header, payload)))
        if not any(k == b'EDID' and v.rstrip(b'\0') == b'SCPTUpdateDummyNamesCall' for k, _, v in slots):
            return payload
        return _encode_record(header, b''.join(
            _with_payload(h, v + b'\n; unknown edit\n' if k == b'SCTX' else v)
            for k, h, v in slots))

    plugin.write_bytes(_walk(prior.read_bytes(), tamper))
    unknown = plugin.read_bytes()
    run(candidate, 'candidate-unknown', failure=True)
    if plugin.read_bytes() != unknown or source.read_bytes() != original:
        raise AssertionError('Patcher changed an input file')
    report = dict(reporter_sha256=REPORTER_SHA, source_sha256=nskr.sha256(source),
                  original_installation_unchanged=True, gameplay_tested=False, runs=runs)
    nskr.write_json(work / 'verification-report.json', report)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'candidate', 'mo2', 'work'):
        parser.add_argument('--' + name, type=Path, required=True)
    options = parser.parse_args()
    verify(options.baseline, options.candidate, options.mo2, options.work)
