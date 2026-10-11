"""Extract B42 description values and loose GECK display literals overlooked by extension filtering."""
from pathlib import Path
import json
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from nskr_output import ini_rows
from tools.prepare_remaining_translation_work import COMMAND, QUOTED


def main():
    installation = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    folder = Path(tempfile.mkdtemp(prefix='extra-loose-display-', dir=ROOT / '.local'))
    scripts, descriptions, hashes = [], [], {}
    for key, chain in installation.providers.items():
        row = chain[-1]
        description = key.startswith('config/b42descriptions/') and key.endswith('.ini')
        script = key.endswith('.gek') or key.startswith('scripts/') and key.endswith('.txt')
        if not (description or script):
            continue
        source = Path(row['physical'])
        hashes[source] = nskr.sha256(source)
        raw = source.read_bytes()
        try:
            text = raw.decode('utf-8-sig')
            encoding = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
        except UnicodeDecodeError:
            text = raw.decode('cp1252')
            encoding = 'cp1252'
        base = {'path': row['path'], 'provider': row['provider'], 'encoding': encoding}
        if description:
            for item in ini_rows(text):
                if re.search(r'[A-Za-z]{2,}', item['source']):
                    descriptions.append({**base, **item, 'kind': 'ini_description_value',
                                         'signature': 'ini_description_value', 'field': ''})
        else:
            for number, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith(';'):
                    continue
                match = COMMAND.search(line.split('"', 1)[0])
                if not match:
                    continue
                values = QUOTED.findall(line[match.end():])
                if match[1].lower().startswith('setuistring'):
                    values = values[1:]
                for value in values:
                    if re.search(r'[A-Za-z]{2,}', value):
                        scripts.append({**base, 'kind': 'script_display_literal_review',
                                        'line': number, 'source': value, 'context': line})
    for source, before in hashes.items():
        if nskr.sha256(source) != before:
            raise ValueError('Extra loose source changed during extraction')
    for name, rows in (('plugin_candidates', []), ('script_candidates', scripts),
                       ('loose_candidates', descriptions), ('bsa_ui_candidates', [])):
        with (folder / (name + '.jsonl')).open('x', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('EXTRA_LOOSE_SOURCES', len(hashes), 'B42_DESCRIPTIONS', len(descriptions),
          'GECK_DISPLAY_LITERALS', len(scripts), 'WORKSPACE', folder, flush=True)


if __name__ == '__main__':
    main()
