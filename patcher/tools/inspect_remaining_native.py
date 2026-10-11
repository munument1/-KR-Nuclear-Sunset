"""Native-type/path validation for every remaining plugin display candidate."""
from collections import defaultdict
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
import nskr_xedit
from nskr_xedit_worker import row_key
from tools.prepare_full_translation import inspect


def main():
    work = Path(sys.argv[1]).resolve()
    with (work / 'classified.jsonl').open(encoding='utf-8') as stream:
        rows = [r for r in map(json.loads, stream)
                if r['kind'] == 'plugin_display_candidate' and r['classification'] in {
                    'translation_candidate', 'mixed_korean_requires_review'}]
    fields = defaultdict(set)
    for row in rows:
        fields[row['signature']].add(row['field'])
    fields = {signature: sorted(names) for signature, names in fields.items()}
    keys = {row_key(row) for row in rows}
    targets = sorted({row['plugin'] for row in rows})
    installation = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    worker = ROOT / 'dist/NuclearSunset-Dev-q92bqkq0/NSKRXEditWorker.exe'
    backend = Path(r'D:\Codex_Trans\비바 뉴 베가스\.tools\xeditlib-native')
    nskr_xedit.runtime = lambda worker_override=None: (worker_override or worker, backend)
    reuse = len(sys.argv) > 2
    native_work = (Path(sys.argv[2]) if reuse else
                   Path(tempfile.mkdtemp(prefix='remaining-all-native-', dir=ROOT / '.local')))
    result = inspect(installation, fields, keys, native_work, 'Inspect',
                     worker, targets=targets, reuse=reuse)
    lookups = defaultdict(list)
    positions = defaultdict(list)
    for file in result['files']:
        for row in file['rows']:
            lookups[(file['plugin'], row_key(row), row['field'],
                     row['source'].replace('\r\n', '\n'),
                     row['field_occurrence'])].append(row)
            positions[(file['plugin'], row_key(row), row['field'],
                       row['field_occurrence'])].append(row)
    prior = nskr.read_json(ROOT / '.local/remaining-corrections-pax5n_rs/corrections.json')
    applied = {(r['plugin'], row_key(r), r['field'], r['field_occurrence']): r['dest']
               for r in prior['plugin_updates']}
    accepted, held, already = [], [], []
    for row in rows:
        match = lookups.get((row['plugin'], row_key(row), row['field'],
                             row['source'].replace('\r\n', '\n'),
                             row['field_occurrence']), [])
        if len(match) == 1:
            accepted.append({**row, 'path': match[0]['path']})
        else:
            position = row['plugin'], row_key(row), row['field'], row['field_occurrence']
            native = positions.get(position, [])
            if len(native) == 1 and applied.get(position) == native[0]['source']:
                already.append(row)
                continue
            try:
                raw_utf8_view = row['source'].encode('cp1252').decode('utf-8', errors='replace')
            except UnicodeEncodeError:
                raw_utf8_view = None
            if len(native) == 1 and raw_utf8_view == native[0]['source']:
                accepted.append({**row, 'path': native[0]['path'], 'source_encoding': 'cp1252',
                                 'validation': 'native_string_type_and_exact_original_byte_decode'})
            else:
                held.append({**row, 'reason': 'not_unique_native_string_slot'})
    nskr.write_json(work / 'native_paths.json', accepted)
    nskr.write_json(work / 'native_held.json', held)
    nskr.write_json(work / 'native_already_applied.json', already)
    print(json.dumps({'candidate_locations': len(rows), 'native_validated': len(accepted),
                      'held': len(held), 'already_applied': len(already),
                      'native_work': str(native_work)},
                     ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
