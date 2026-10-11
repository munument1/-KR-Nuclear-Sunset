"""Carry verified residual translations into a new complete development catalog."""
from collections import defaultdict
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from nskr_output import ini_rows, output_catalog, original_installation
from tools.loose_translation import decode
from tools.tes4_text_scan import plugin_records, clean_text


def main():
    corrections = nskr.read_json(Path(sys.argv[1]) / 'corrections.json')
    source = ROOT / 'dist/NuclearSunset-Dev-0_1189_j/TranslationData'
    catalog = nskr.read_json(source / 'catalog.json')
    installation = original_installation(nskr.Installation(
        Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1'),
        catalog['excluded_test_providers'])
    entries = {e['path'].casefold(): e for e in catalog['files']}
    added = 0
    for row in corrections['plugin_updates']:
        entry = entries[row['plugin'].casefold()]
        identity = tuple(row[k] for k in ('owner', 'id', 'signature', 'field', 'path', 'source'))
        if any(tuple(v[k] for k in ('owner', 'id', 'signature', 'field', 'path', 'source')) == identity
               for v in entry['mappings']):
            raise ValueError('Residual mapping already exists in target plugin catalog')
        entry['mappings'].append({**{k: v for k, v in row.items() if k != 'plugin'},
                                  'origin': 'base_translation_inherited'})
        added += 1
    ui = nskr.read_json(ROOT / 'data/remaining_ui_direct_mappings.json')
    for virtual, pairs in ui.items():
        physical = installation.source(virtual)
        text, encoding = decode(physical)
        rows = [{'section': r['section'], 'key': r['key'], 'source': r['source'],
                 'dest': pairs[r['source']]} for r in ini_rows(text) if r['source'] in pairs]
        entry = {'path': installation.providers[virtual.casefold()][-1]['path'],
                 'kind': 'ini', 'provider': installation.providers[virtual.casefold()][-1]['provider'],
                 'baseline_sha256': nskr.sha256(physical), 'mappings': rows,
                 'review_status': 'ui_reviewed', 'display_mappings_only': True}
        if virtual.casefold() in entries:
            raise ValueError('Supplemental UI file already has a catalog policy')
        catalog['files'].append(entry)
    tutorial = entries['ns tutorial.esm']
    ids = {'000ae0', '000ae2', '000dc0'}
    current = Path(r'C:\Modlists\NuclearSunset\mods\NSKR Test - 1cxljp5s\NS Tutorial.esm')
    messages = {}
    for fid, signature, slots in plugin_records(current):
        ident = f'{fid & 0xffffff:06x}'
        if signature == 'MESG' and ident in ids:
            messages[ident] = next(clean_text(raw) for field, raw in slots if field == 'DESC')
    if set(messages) != ids:
        raise ValueError('Missing concise tutorial messages')
    for row in tutorial['mappings']:
        if row['id'] in ids and row['field'] == 'DESC':
            row['dest'] = messages[row['id']]
    catalog['translation_ready'] = False
    catalog['candidate_summary'].update(
        residual_existing_translations_added=added,
        residual_ui_translations_added=sum(len(p) for p in ui.values()),
        json_with_translation_companion='preserve_original_json')
    output_catalog(catalog, development=True, scopes={'ui', 'fonts', 'plugins'})
    work = Path(tempfile.mkdtemp(prefix='remaining-catalog-', dir=ROOT / '.local'))
    target = work / 'TranslationData'
    shutil.copytree(source, target)
    nskr.write_json(target / 'catalog.json', catalog)
    print('CATALOG', target, 'EXISTING_TRANSLATIONS_ADDED', added,
          'UI_TRANSLATIONS_ADDED', sum(len(p) for p in ui.values()), flush=True)


if __name__ == '__main__':
    main()
