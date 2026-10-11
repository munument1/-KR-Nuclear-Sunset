"""Resolve the reviewed runtime wording variants in an already verified correction build."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr


def main():
    build = Path(sys.argv[1]).resolve()
    catalog_dir = build / 'TranslationData'
    catalog = nskr.read_json(catalog_dir / 'catalog.json')
    output = nskr.read_json(build / 'output.json')
    spec = next(s for s in catalog['runtime_mods']
                if s['mod'] == 'Nuclear Sunset - Korean UI Runtime Translations')
    file = next(f for f in spec['files'] if f['path'].endswith('/NSKR_UI_Translations.json'))
    target = build / 'Output/mods' / spec['mod'] / file['path']
    values = {r['original']: r['translation'] for r in nskr.read_json(target)}
    values.update(nskr.read_json(ROOT / 'data/remaining_runtime_direct_mappings.json'))
    rows = [{'original': source, 'translation': dest} for source, dest in values.items()]
    nskr.write_json(target, rows)
    nskr.write_json(catalog_dir / file['payload'], rows)
    file['payload_sha256'] = nskr.sha256(target)
    if nskr.sha256(catalog_dir / file['payload']) != file['payload_sha256']:
        raise ValueError('Runtime dictionary payload mismatch')
    for row in output['files']:
        if row['output_path'] == f'mods/{spec["mod"]}/{file["path"]}':
            row['output_sha256'] = file['payload_sha256']
    output['runtime_conflicts'] = {}
    catalog['candidate_summary']['remaining_runtime_dictionary_entries'] = len(rows)
    nskr.write_json(build / 'output.json', output)
    native = nskr.read_json(ROOT / '.local/remaining-translation-nvd39gt5/native_paths.json')
    encodings = {(r['plugin'].casefold(), r['owner'], r['id'], r['signature'],
                  r['field'], r['path'], r['source']): r['source_encoding']
                 for r in native if r.get('source_encoding')}
    added = 0
    for entry in catalog['files']:
        if entry['path'].casefold() == 'nvse/plugins/nvse_stewie_tweaks.ini':
            entry.pop('updated_source_exact_matches_only', None)
            entry['display_mappings_only'] = True
        if entry['kind'] != 'plugin-records':
            continue
        for row in entry['mappings']:
            key = (entry['path'].casefold(), row['owner'], row['id'], row['signature'],
                   row['field'], row['path'], row['source'])
            if key in encodings:
                row['source_encoding'] = encodings[key]
                added += 1
    nskr.write_json(catalog_dir / 'catalog.json', catalog)
    print('RUNTIME_DICTIONARY_ENTRIES', len(rows), 'CONFLICTS', 0,
          'EXPLICIT_CP1252_MAPPING_SOURCES', added, flush=True)


if __name__ == '__main__':
    main()
