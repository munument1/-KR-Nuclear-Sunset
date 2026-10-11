"""Build and verify a small correction Output, preserving original mod paths."""
from collections import defaultdict
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from nskr_output import (
    original_installation, translation_companion, destination, merge_loose, ini_rows)
from nskr_plugin_text import write_plugin, verify_plugin
from tools.loose_translation import decode
from tools.tes4_text_scan import masters


def identity(row):
    return (row['plugin'], row['owner'], row['id'], row['signature'],
            row['field'], row['field_occurrence'], row['source'])


def main():
    candidates = Path(sys.argv[1])
    native = Path(sys.argv[2])
    catalog = nskr.read_json(ROOT / 'dist/NuclearSunset-Dev-0_1189_j/TranslationData/catalog.json')
    installed = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    original = original_installation(installed, catalog['excluded_test_providers'])
    approved = {
        identity(row) for row in map(json.loads, (
            candidates / 'plugin_candidates.jsonl').read_text(encoding='utf-8').splitlines())
        if row['existing_translation']}
    updates = [row for row in nskr.read_json(native / 'resolved.json')
               if identity(row) in approved]
    if len(updates) != len(approved):
        raise ValueError('Native validation does not cover every selected existing translation')
    work = Path(tempfile.mkdtemp(prefix='remaining-corrections-', dir=ROOT / '.local'))
    output = work / 'Output'
    files = []
    protected = {}
    grouped = defaultdict(list)
    for row in updates:
        grouped[row['plugin']].append(row)
    for plugin, rows in grouped.items():
        source = installed.source(plugin)
        baseline = original.source(plugin)
        protected[baseline] = nskr.sha256(baseline)
        relative = destination(original, baseline, plugin)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        before = nskr.sha256(source)
        names = masters(source)
        write_plugin(source, target, rows, names)
        verified = verify_plugin(source, target, rows, names)
        if nskr.sha256(source) != before:
            raise RuntimeError('Current test source changed while building')
        files.append({'path': plugin, 'output_path': relative,
                      'source_sha256': before, 'output_sha256': nskr.sha256(target),
                      'translated': len(rows), 'records_verified': len(verified)})
    mappings = nskr.read_json(ROOT / 'data/remaining_ui_direct_mappings.json')
    for virtual, pairs in mappings.items():
        source = original.source(virtual)
        protected[source] = nskr.sha256(source)
        text, encoding = decode(source)
        rows = [{**row, 'dest': pairs[row['source']]}
                for row in ini_rows(text) if row['source'] in pairs]
        if {r['source'] for r in rows} != pairs.keys():
            raise ValueError('An authored UI translation has no exact installed source')
        data, statistics = merge_loose(source, {'kind': 'ini', 'mappings': rows})
        if statistics['translated'] != len(rows):
            raise ValueError('Not every authored UI translation was applied')
        original_lines = text.splitlines(keepends=True)
        translated_lines = data.decode(encoding).splitlines(keepends=True)
        changed_lines = {row['line'] for row in rows}
        if len(original_lines) != len(translated_lines):
            raise ValueError('UI line count changed')
        if any(a != b for index, (a, b) in enumerate(zip(original_lines, translated_lines))
               if index not in changed_lines):
            raise ValueError('Unapproved UI data changed')
        translated_rows = list(ini_rows(data.decode(encoding)))
        if [(r['section'], r['key']) for r in ini_rows(text)] != [
                (r['section'], r['key']) for r in translated_rows]:
            raise ValueError('UI sections or keys changed')
        relative = destination(original, source, virtual)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({'path': virtual, 'output_path': relative,
                      'source_sha256': nskr.sha256(source), 'output_sha256': nskr.sha256(target),
                      'translated': len(rows)})
    restored = 0
    for key, chain in original.providers.items():
        virtual = chain[-1]['path']
        if not translation_companion(original, virtual):
            continue
        source = original.source(virtual)
        protected[source] = nskr.sha256(source)
        relative = destination(original, source, virtual)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if nskr.sha256(target) != protected[source]:
            raise RuntimeError('Paired JSON was not preserved exactly')
        files.append({'path': virtual, 'output_path': relative,
                      'source_sha256': protected[source], 'output_sha256': protected[source],
                      'translated': 0, 'status': 'original_json_preserved_translation_companion'})
        restored += 1
    if any(nskr.sha256(p) != before for p, before in protected.items()):
        raise RuntimeError('Original installed source changed')
    nskr.write_json(work / 'corrections.json', {
        'files': files, 'translation_ready': False, 'game_validation': 'not_run',
        'plugin_updates': updates, 'paired_json_preserved': restored})
    print('OUTPUT', output, 'PLUGIN_TRANSLATIONS', len(updates),
          'PLUGIN_FILES', len(grouped), 'UI_TRANSLATIONS',
          sum(f['translated'] for f in files) - len(updates),
          'PAIRED_JSON_PRESERVED', restored, flush=True)
    running = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "Get-Process | Where-Object { $_.ProcessName -eq 'FalloutNV' } | Select-Object -ExpandProperty Id"],
        capture_output=True, text=True, check=True)
    if running.stdout.strip():
        print('INSTALLATION_PENDING_GAME_EXIT', running.stdout.strip(), flush=True)
        return
    overlay = installed.mods / 'NSKR Test - 1cxljp5s'
    for row in files:
        source = output / row['output_path']
        target = overlay / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if nskr.sha256(target) != row['output_sha256']:
            raise RuntimeError('Test overlay copy verification failed')
    if any(nskr.sha256(p) != before for p, before in protected.items()):
        raise RuntimeError('Original installed source changed during overlay installation')
    print('TEST_OVERLAY_APPLIED_AND_VERIFIED', len(files),
          'ORIGINAL_FILES_UNCHANGED', len(protected), flush=True)


if __name__ == '__main__':
    main()
