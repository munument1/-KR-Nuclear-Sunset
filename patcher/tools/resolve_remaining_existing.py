"""Native-path validation of exact existing translations remaining in winning records."""
from collections import defaultdict
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
import nskr_xedit
from tools.prepare_full_translation import inspect
from nskr_xedit_worker import row_key


def main():
    candidates = Path(sys.argv[1])
    rows = [json.loads(line) for line in (candidates / 'plugin_candidates.jsonl').read_text(
        encoding='utf-8').splitlines()]
    rows = [row for row in rows if row['existing_translation']]
    keys = {row_key(row) for row in rows}
    targets = sorted({row['plugin'] for row in rows})
    catalog = nskr.read_json(ROOT / 'dist/NuclearSunset-Dev-0_1189_j/TranslationData/catalog.json')
    work = Path(tempfile.mkdtemp(prefix='remaining-native-', dir=ROOT / '.local'))
    installation = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    worker = ROOT / 'dist/NuclearSunset-Dev-0_1189_j/NSKRXEditWorker.exe'
    backend = Path(r'D:\Codex_Trans\비바 뉴 베가스\.tools\xeditlib-native')
    nskr_xedit.runtime = lambda worker_override=None: (worker_override or worker, backend)
    result = inspect(installation, catalog['plugin_fields'], keys, work, 'Inspect',
                     worker, targets=targets)
    native = defaultdict(list)
    for file in result['files']:
        for row in file['rows']:
            native[(file['plugin'], row_key(row), row['field'],
                    row['source'].replace('\r\n', '\n'), row['field_occurrence'])].append(row)
    resolved, held = [], []
    for row in rows:
        match = native.get((row['plugin'], row_key(row), row['field'],
                            row['source'].replace('\r\n', '\n'), row['field_occurrence']), [])
        if len(match) != 1:
            held.append(row)
            continue
        update = {**match[0], 'dest': row['existing_translation'], 'plugin': row['plugin']}
        nskr_xedit.validate_mapping(update)
        resolved.append(update)
    nskr.write_json(work / 'resolved.json', resolved)
    nskr.write_json(work / 'held.json', held)
    print(json.dumps({'work': str(work), 'candidates': len(rows), 'native_resolved': len(resolved),
                      'held': len(held), 'plugins': len(targets)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
