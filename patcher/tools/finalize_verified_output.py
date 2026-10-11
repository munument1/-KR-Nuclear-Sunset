"""Compose the verified full Output and correct stale SST text-only mappings safely."""
from collections import Counter
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
import nskr_xedit
from nskr_output import original_installation, output_catalog, format_plugin_report
from nskr_plugin_text import write_plugin, verify_plugin
from tools.tes4_text_scan import plugin_records, masters, clean_text


def record_strings(path, signature, ident, field):
    for fid, sig, slots in plugin_records(path):
        if sig == signature and fid & 0xffffff == ident:
            return [clean_text(raw) or clean_text(raw, 'cp1252')
                    for name, raw in slots if name == field]
    raise ValueError('Required record missing from verified source')


def main():
    base = Path(sys.argv[1]).resolve()
    full = Path(sys.argv[2]).resolve()
    ui = Path(sys.argv[3]).resolve()
    audit = Path(sys.argv[4]).resolve()
    work = Path(tempfile.mkdtemp(prefix='final-complete-', dir=ROOT / '.local'))
    catalog_dir = work / 'TranslationData'
    shutil.copytree(base, catalog_dir)
    catalog = nskr.read_json(catalog_dir / 'catalog.json')
    installation = original_installation(nskr.Installation(
        Path(r'C:\Modlists\NuclearSunset'), 'A - Uranium Haze NVR High'),
        catalog['excluded_test_providers'])
    report = nskr.read_json(full / 'Output.report.json')
    original_hashes = {}
    for row in report['files']:
        if nskr.sha256(full / 'Output' / row['output_path']) != row['output_sha256']:
            raise ValueError('Previously verified full output changed')
        if row.get('source_sha256'):
            source = installation.source(row['path'])
            if nskr.sha256(source) != row['source_sha256']:
                raise ValueError('Original installed source changed')
            original_hashes[source] = row['source_sha256']
    stage = work / 'Output'
    shutil.copytree(full / 'Output', stage)
    files = {row['output_path']: row for row in report['files']}
    for row in nskr.read_json(ui / 'Output.report.json')['files']:
        source = ui / 'Output' / row['output_path']
        if nskr.sha256(source) != row['output_sha256']:
            raise ValueError('Verified UI output changed')
        target = stage / row['output_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        files[row['output_path']] = row
    tale = next(row for row in files.values() if row['path'] == 'TaleOfTwoWastelands.esm')
    current = stage / tale['output_path']
    original = installation.source('TaleOfTwoWastelands.esm')
    old_notes = record_strings(current, 'QUST', 0x004c75, 'CNAM')
    source_notes = record_strings(original, 'QUST', 0x004c75, 'CNAM')
    if len(old_notes) != len(source_notes):
        raise ValueError('Quest stage log entry structure differs')
    updates = [{'owner': 'brokensteel.esm', 'id': '004c75', 'signature': 'QUST',
                'field': 'CNAM', 'field_occurrence': index, 'source': old,
                'dest': source} for index, (old, source) in enumerate(zip(old_notes, source_notes))
               if old != source]
    medical_source = record_strings(original, 'NOTE', 0x0b99a7, 'TNAM')[0]
    translated = nskr.read_json(audit / 'qa_accepted.json')
    medical = next(row for row in translated if row['signature'] == 'NOTE'
                   and row['field'] == 'TNAM' and row['source'] == medical_source)
    medical_update = {'owner': 'fallout3.esm', 'id': '0b99a7', 'signature': 'NOTE',
                      'field': 'TNAM', 'path': r'TNAM\Text', 'field_occurrence': 0,
                      'source': record_strings(current, 'NOTE', 0x0b99a7, 'TNAM')[0],
                      'dest': medical['dest']}
    updates.append(medical_update)
    patched = work / 'TaleOfTwoWastelands.esm'
    write_plugin(current, patched, updates, masters(current))
    hashes = verify_plugin(current, patched, updates, masters(current))
    native = ROOT / '.local/remaining-all-native-thjqv83c/Inspect'
    metadata = next(f for f in nskr.read_json(native / 'inspect.json')['files']
                    if f['plugin'] == 'TaleOfTwoWastelands.esm')
    job = work / 'NativeReadback'
    data = job / 'Game/Data'
    data.mkdir(parents=True)
    output_plugins = {row['path'].casefold(): stage / row['output_path']
                      for row in files.values() if row['path'].lower().endswith(('.esm', '.esp'))}
    active = list(installation.active)
    for plugin in active:
        shutil.copyfile(patched if plugin.casefold() == 'taleoftwowastelands.esm'
                        else output_plugins.get(plugin.casefold(), installation.source(plugin)),
                        data / plugin)
    changes = {'TaleOfTwoWastelands.esm': [medical_update]}
    request = {'game': str(job / 'Game'), 'plugins': active,
               'targets': ['TaleOfTwoWastelands.esm'], 'mode': 'verify',
               'fields': {'QUST': ['CNAM'], 'NOTE': ['TNAM']},
               'expected': {'TaleOfTwoWastelands.esm': hashes}, 'changes': changes,
               'expectedHeaders': {'TaleOfTwoWastelands.esm': metadata['headerHash']},
               'expectedRecordIndexes': {'TaleOfTwoWastelands.esm': metadata['recordIndexHash']},
               'output': str(job / 'verify.json')}
    worker = ROOT / 'dist/NuclearSunset-Dev-tn5xx8ca/NSKRXEditWorker.exe'
    backend = Path(r'D:\Codex_Trans\비바 뉴 베가스\.tools\xeditlib-native')
    nskr_xedit.runtime = lambda worker_override=None: (worker_override or worker, backend)
    print('FINAL_STALE_RECORD_READBACK', len(updates), 'TEXT_FIELDS', flush=True)
    nskr_xedit.run_worker(request, job, 'verify', worker)
    shutil.copyfile(patched, current)
    tale['output_sha256'] = nskr.sha256(current)
    restored_count = len(updates) - 1
    tale['translated'] -= restored_count
    stale = []
    for entry in catalog['files']:
        if entry['kind'] != 'plugin-records':
            continue
        kept = []
        for row in entry['mappings']:
            remove = (entry['path'] == 'TaleOfTwoWastelands.esm' and (
                row['id'] == '004c75' and row['signature'] == 'QUST' and row['field'] == 'CNAM'
                or row['id'] == '0b99a7' and row['signature'] == 'NOTE' and row['field'] == 'TNAM'))
            remove |= (entry['path'] == 'AWorldOfPainFO3.esm'
                       and row['id'] in {'037f8b', '0299b8'} and row['source'] == row['dest'])
            if remove:
                stale.append({'plugin': entry['path'], **row})
            else:
                kept.append(row)
        entry['mappings'] = kept
        if entry['path'] == 'TaleOfTwoWastelands.esm':
            entry['mappings'].append({**medical_update, 'source': medical_source,
                                      'origin': 'gemini_candidate'})
    spec = next(s for s in catalog['runtime_mods']
                if s['mod'] == 'Nuclear Sunset - Korean UI Runtime Translations')
    item = next(f for f in spec['files'] if f['path'].endswith('/NSKR_UI_Translations.json'))
    dictionary = nskr.read_json(catalog_dir / item['payload'])
    values = {row['original']: row['translation'] for row in dictionary}
    for row in translated:
        if not row.get('preserve_reason') and row['source'] != row['dest']:
            values.setdefault(row['source'], row['dest'])
    dictionary = [{'original': source, 'translation': target} for source, target in values.items()]
    nskr.write_json(catalog_dir / item['payload'], dictionary)
    item['payload_sha256'] = nskr.sha256(catalog_dir / item['payload'])
    runtime_path = f'mods/{spec["mod"]}/{item["path"]}'
    shutil.copyfile(catalog_dir / item['payload'], stage / runtime_path)
    files[runtime_path]['output_sha256'] = item['payload_sha256']
    for row in files.values():
        if row['path'] in {'TaleOfTwoWastelands.esm', 'AWorldOfPainFO3.esm'}:
            row['resolved_obsolete_mismatches'] = row.get('unmatched_entries', [])
            row['unmatched_entries'] = []
            row['unmatched'] = 0
        if nskr.sha256(stage / row['output_path']) != row['output_sha256']:
            raise ValueError('Final artifact readback mismatch')
    report['files'] = list(files.values())
    report['output'] = str(stage)
    report['report_json'] = str(work / 'Output.report.json')
    report['report_text'] = str(work / 'Output.report.txt')
    report['reused_native_verification_from'] = str(full / 'Output.report.json')
    report['runtime_dictionary_entries'] = len(dictionary)
    for outcome in report['plugin_outcomes']:
        if outcome['path'] in {'TaleOfTwoWastelands.esm', 'AWorldOfPainFO3.esm'}:
            outcome['unmatched'] = 0
        if outcome['path'] == 'TaleOfTwoWastelands.esm':
            outcome['translated'] -= restored_count
    catalog['candidate_summary']['remaining_runtime_dictionary_entries'] = len(dictionary)
    catalog['candidate_summary']['stale_sst_pairs_removed'] = len(stale)
    catalog['candidate_summary']['restored_developer_stage_notes'] = restored_count
    output_catalog(catalog, development=True, scopes={'ui', 'fonts', 'plugins'})
    nskr.write_json(catalog_dir / 'catalog.json', catalog)
    nskr.write_json(work / 'Output.report.json', report)
    (work / 'Output.report.txt').write_text(format_plugin_report(report), encoding='utf-8')
    if any(nskr.sha256(source) != expected for source, expected in original_hashes.items()):
        raise ValueError('Original source changed')
    print('FINAL_VERIFIED_OUTPUT', stage, 'CATALOG', catalog_dir,
          'RUNTIME_ENTRIES', len(dictionary), 'STALE_PAIRS_REMOVED', len(stale),
          'UNMATCHED', sum(f.get('unmatched', 0) for f in report['files']), flush=True)


if __name__ == '__main__':
    main()
