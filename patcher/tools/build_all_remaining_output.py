"""Build byte-preserving plugin corrections plus a runtime UI dictionary and full catalog."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
import nskr_xedit
from nskr_output import original_installation, destination, ini_rows, output_catalog
from nskr_plugin_text import write_plugin, verify_plugin
from tools.loose_translation import decode
from tools.residual_translation_validation import validate
from tools.tes4_text_scan import masters

RUNTIME = 'Nuclear Sunset - Korean UI Runtime Translations'


def mapping_key(row):
    return tuple(row[k] for k in ('owner', 'id', 'signature', 'field', 'path', 'source'))


def main():
    work = Path(sys.argv[1]).resolve()
    accepted = nskr.read_json(work / 'qa_accepted.json')
    translated = {(r['signature'], r['field'], r['source']): r for r in accepted
                  if not r.get('preserve_reason') and r['source'] != r['dest']}
    if len(translated) != sum(not r.get('preserve_reason') and r['source'] != r['dest']
                              for r in accepted):
        raise ValueError('Duplicate translation identities')
    for row in translated.values():
        if validate(row['source'], row['dest'], row['signature'], row['field']):
            raise ValueError('Unvalidated translation reached Output builder')
    installed = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    base = ROOT / 'dist/NuclearSunset-Dev-q92bqkq0/TranslationData'
    catalog = nskr.read_json(base / 'catalog.json')
    original = original_installation(installed, catalog['excluded_test_providers'])
    grouped = defaultdict(list)
    for row in nskr.read_json(work / 'native_paths.json'):
        result = translated.get((row['signature'], row['field'], row['source']))
        if result:
            update = {**row, 'dest': result['dest'], 'origin': 'gemini_candidate'}
            nskr_xedit.validate_mapping(update)
            grouped[row['plugin']].append(update)
    build = Path(tempfile.mkdtemp(prefix='all-remaining-output-', dir=ROOT / '.local'))
    stage = build / 'Output'
    files, changed, expected, source_hashes, protected = [], {}, {}, {}, {}
    runtime_plugins = {}
    for plugin, updates in grouped.items():
        source = installed.source(plugin)
        source_hashes[source] = nskr.sha256(source)
        if plugin.casefold() in original.providers:
            baseline = original.source(plugin)
            relative = destination(original, baseline, plugin)
        else:
            matches = [(spec, row) for spec in catalog.get('runtime_mods', [])
                       for row in spec['files'] if row['path'].casefold() == plugin.casefold()]
            if len(matches) != 1:
                raise ValueError('Missing unique packaged runtime plugin source')
            spec, item = matches[0]
            baseline = nskr.contained(base, item['payload'])
            if nskr.sha256(baseline) != item['payload_sha256']:
                raise ValueError('Packaged runtime plugin source hash mismatch')
            relative = f'mods/{spec["mod"]}/{plugin}'
            runtime_plugins[plugin] = item
        protected[baseline] = nskr.sha256(baseline)
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        write_plugin(source, target, updates, masters(source))
        expected[plugin] = verify_plugin(source, target, updates, masters(source))
        changed[plugin] = updates
        files.append({'path': plugin, 'output_path': relative,
                      'source_sha256': source_hashes[source],
                      'output_sha256': nskr.sha256(target), 'translated': len(updates)})
    print('PLUGIN_BINARY_VERIFIED', len(grouped), 'FILES',
          sum(len(rows) for rows in grouped.values()), 'STRINGS', flush=True)
    native = ROOT / '.local/remaining-all-native-thjqv83c/Inspect'
    inspection = nskr.read_json(native / 'inspect.json')
    metadata = {r['plugin']: r for r in inspection['files']}
    job = build / 'NativeReadback'
    data = job / 'Game/Data'
    data.mkdir(parents=True)
    output_by_plugin = {r['path']: stage / r['output_path'] for r in files}
    for plugin in installed.active:
        source = installed.source(plugin)
        snapshot = native / 'Game/Data' / plugin
        if nskr.sha256(source) != nskr.sha256(snapshot):
            raise ValueError('Plugin changed since the native validation snapshot: ' + plugin)
        shutil.copyfile(output_by_plugin.get(plugin, source), data / plugin)
    fields = defaultdict(set)
    for rows in grouped.values():
        for row in rows:
            fields[row['signature']].add(row['field'])
    request = {'mode': 'verify', 'game': str(job / 'Game'),
               'plugins': installed.active, 'targets': sorted(grouped),
               'fields': {s: sorted(f) for s, f in fields.items()},
               'expected': expected, 'changes': changed,
               'expectedHeaders': {p: metadata[p]['headerHash'] for p in grouped},
               'expectedRecordIndexes': {p: metadata[p]['recordIndexHash'] for p in grouped},
               'output': str(job / 'verify.json')}
    worker = ROOT / 'dist/NuclearSunset-Dev-q92bqkq0/NSKRXEditWorker.exe'
    backend = Path(r'D:\Codex_Trans\비바 뉴 베가스\.tools\xeditlib-native')
    nskr_xedit.runtime = lambda worker_override=None: (worker_override or worker, backend)
    print('PLUGIN_FRESH_NATIVE_READBACK', len(grouped), 'FILES', flush=True)
    nskr_xedit.run_worker(request, job, 'verify', worker)
    runtime = defaultdict(set)
    for row in translated.values():
        if any(location['kind'] != 'plugin_display_candidate'
               for location in row['locations']):
            runtime[row['source']].add(row['dest'])
    runtime['purchases'].add('구매')
    runtime['Purchases'].add('구매')
    runtime['permanent'].add('영구')
    runtime['Permanent'].add('영구')
    dictionary = [{'original': source, 'translation': next(iter(values))}
                  for source, values in runtime.items() if len(values) == 1]
    conflicts = {s: sorted(v) for s, v in runtime.items() if len(v) > 1}
    runtime_root = stage / 'mods' / RUNTIME
    plugins = runtime_root / 'NVSE/Plugins'
    plugins.mkdir(parents=True)
    nskr.write_json(plugins / 'NSKR_UI_Translations.json', dictionary)
    xml = '<tNVSE><dictionary><json path="Data/nvse/plugins/NSKR_UI_Translations.json" priority="50"/></dictionary></tNVSE>\n'
    ET.fromstring(xml)
    (plugins / 'tnvse_dictionary.xml').write_text(xml, encoding='utf-8')
    config = installed.source('nvse/plugins/tnvse.ini')
    config_before = nskr.sha256(config)
    text, encoding = decode(config)
    lines = text.splitlines(keepends=True)
    desired = {'bEnableDictionaryTranslation': '1',
               'bEnableDictionaryWildcardTranslation': '1',
               'bDisableDictionaryTranslationInConsole': '1'}
    found = set()
    for row in ini_rows(text):
        if row['section'] == '[Dictionary]' and row['key'] in desired:
            index = row['line']
            line = lines[index]
            end = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
            body = line[:-len(end)] if end else line
            lhs, rhs = body.split('=', 1)
            lead = rhs[:len(rhs) - len(rhs.lstrip())]
            trail = rhs[len(rhs.rstrip()):]
            lines[index] = lhs + '=' + lead + desired[row['key']] + trail + end
            found.add(row['key'])
    if found != desired.keys():
        raise ValueError('Missing exact existing dictionary configuration keys')
    (plugins / 'tnvse.ini').write_bytes(''.join(lines).encode(encoding))
    entries = {e['path'].casefold(): e for e in catalog['files']}
    for plugin, updates in grouped.items():
        if plugin in runtime_plugins:
            continue
        entry = entries.get(plugin.casefold())
        if entry is None:
            source = original.source(plugin)
            entry = {'path': plugin, 'kind': 'plugin-records',
                     'baseline_sha256': nskr.sha256(source),
                     'review_status': 'source_matched_candidate', 'mappings': []}
            catalog['files'].append(entry)
        known = {mapping_key(r): r['dest'] for r in entry['mappings']}
        for row in updates:
            if mapping_key(row) in known:
                if known[mapping_key(row)] != row['dest']:
                    raise ValueError('New translation conflicts with a saved target mapping')
                continue
            entry['mappings'].append({k: v for k, v in row.items() if k in {
                'owner', 'id', 'signature', 'field', 'path', 'source', 'dest',
                'origin', 'field_occurrence'}})
        for row in updates:
            catalog['plugin_fields'].setdefault(row['signature'], [])
            if row['field'] not in catalog['plugin_fields'][row['signature']]:
                catalog['plugin_fields'][row['signature']].append(row['field'])
    catalog_dir = build / 'TranslationData'
    shutil.copytree(base, catalog_dir)
    for plugin, item in runtime_plugins.items():
        shutil.copyfile(output_by_plugin[plugin], nskr.contained(catalog_dir, item['payload']))
        item['payload_sha256'] = nskr.sha256(output_by_plugin[plugin])
    spec = {'mod': RUNTIME, 'review_status': 'validated_runtime_dictionary_candidate',
            'required_masters': [], 'plugins': [], 'files': []}
    for source in plugins.iterdir():
        virtual = 'NVSE/Plugins/' + source.name
        payload = 'runtime_ui/' + source.name
        target = catalog_dir / payload
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        spec['files'].append({'path': virtual, 'payload': payload,
                              'payload_sha256': nskr.sha256(source)})
        files.append({'path': virtual, 'output_path': f'mods/{RUNTIME}/{virtual}',
                      'output_sha256': nskr.sha256(source), 'translated': 0})
    catalog.setdefault('runtime_mods', []).append(spec)
    catalog['translation_ready'] = False
    catalog['candidate_summary']['remaining_plugin_strings_added'] = sum(map(len, grouped.values()))
    catalog['candidate_summary']['remaining_runtime_dictionary_entries'] = len(dictionary)
    output_catalog(catalog, development=True, scopes={'ui', 'fonts', 'plugins'})
    nskr.write_json(catalog_dir / 'catalog.json', catalog)
    if nskr.sha256(config) != config_before or any(nskr.sha256(p) != h for p, h in source_hashes.items()):
        raise ValueError('Current test source changed during generation')
    if any(nskr.sha256(p) != h for p, h in protected.items()):
        raise ValueError('Original installed source changed')
    nskr.write_json(build / 'output.json', {'files': files, 'runtime_conflicts': conflicts,
                    'catalog': str(catalog_dir), 'translation_ready': False,
                    'game_validation': 'not_run'})
    print('OUTPUT_COMPLETE', stage, 'CATALOG', catalog_dir, 'RUNTIME_ENTRIES', len(dictionary),
          'RUNTIME_CONFLICTS', len(conflicts), flush=True)


if __name__ == '__main__':
    main()
