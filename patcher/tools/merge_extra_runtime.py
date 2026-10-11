"""Merge verified extra descriptions into a new full catalog, keeping saved wording first."""
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from nskr_output import output_catalog
from tools.residual_translation_validation import validate


def main():
    extra = Path(sys.argv[1]).resolve()
    source = Path(sys.argv[2]).resolve()
    work = Path(tempfile.mkdtemp(prefix='complete-translation-', dir=ROOT / '.local'))
    target = work / 'TranslationData'
    shutil.copytree(source, target)
    catalog = nskr.read_json(target / 'catalog.json')
    runtime = next(r for r in catalog['runtime_mods']
                   if r['mod'] == 'Nuclear Sunset - Korean UI Runtime Translations')
    item = next(r for r in runtime['files'] if r['path'].endswith('/NSKR_UI_Translations.json'))
    path = nskr.contained(target, item['payload'])
    values = {r['original']: r['translation'] for r in nskr.read_json(path)}
    added, previous = 0, []
    rows = nskr.read_json(extra / 'qa_accepted.json')
    held = nskr.read_json(extra / 'qa_held.json')
    if held:
        raise ValueError('Extra translation queue still has held rows')
    for row in rows:
        if row.get('preserve_reason') or row['source'] == row['dest']:
            continue
        if validate(row['source'], row['dest'], row['signature'], row['field']):
            raise ValueError('Extra translation failed independent validation')
        if row['source'] in values:
            if values[row['source']] != row['dest']:
                previous.append(row['source'])
            continue
        values[row['source']] = row['dest']
        added += 1
    values.update(nskr.read_json(ROOT / 'data/remaining_runtime_direct_mappings.json'))
    nskr.write_json(path, [{'original': source, 'translation': dest}
                           for source, dest in values.items()])
    item['payload_sha256'] = nskr.sha256(path)
    for entry in catalog['files']:
        if entry['path'].casefold() == 'nvse/plugins/nvse_stewie_tweaks.ini':
            entry.pop('updated_source_exact_matches_only', None)
            entry['display_mappings_only'] = True
    catalog['candidate_summary']['extra_loose_unique_translations_added'] = added
    catalog['candidate_summary']['remaining_runtime_dictionary_entries'] = len(values)
    catalog['translation_ready'] = False
    output_catalog(catalog, development=True, scopes={'ui', 'fonts', 'plugins'})
    nskr.write_json(target / 'catalog.json', catalog)
    print('COMPLETE_CATALOG', target, 'EXTRA_TRANSLATIONS_ADDED', added,
          'RUNTIME_ENTRIES', len(values), 'SAVED_WORDING_REUSED', len(previous), flush=True)


if __name__ == '__main__':
    main()
