"""Requeue non-Korean changed SST destinations; preserve developer-only quest stage notes."""
from pathlib import Path
import json
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from nskr_output import original_installation
from tools.tes4_text_scan import plugin_records, clean_text


def main():
    catalog = nskr.read_json(ROOT / 'dist/NuclearSunset-Dev-tn5xx8ca/TranslationData/catalog.json')
    changed = {r['dest'] for e in catalog['files'] for r in e.get('mappings', [])
               if r['dest'] != r['source'] and not re.search('[가-힣]', r['dest'])}
    with (ROOT / '.local/remaining-translation-nvd39gt5/classified.jsonl').open(encoding='utf-8') as stream:
        rows = [r for r in map(json.loads, stream)
                if r['classification'] == 'already_translated' and r['source'] in changed
                and not re.search('[가-힣]', r['source'])]
    rows = [r for r in rows if not (
        r.get('plugin') == 'TaleOfTwoWastelands.esm' and (
            r.get('id') == '004c75' and r.get('signature') == 'QUST' and r.get('field') == 'CNAM'
            or r.get('id') == '0b99a7' and r.get('signature') == 'NOTE' and r.get('field') == 'TNAM'))]
    installation = original_installation(nskr.Installation(
        Path(r'C:\Modlists\NuclearSunset'), 'A - Uranium Haze NVR High'),
        catalog['excluded_test_providers'])
    source = installation.source('TaleOfTwoWastelands.esm')
    for fid, signature, slots in plugin_records(source):
        if signature == 'NOTE' and fid & 0xffffff == 0x0b99a7:
            text = next(clean_text(raw) or clean_text(raw, 'cp1252')
                        for field, raw in slots if field == 'TNAM')
            rows.append({'kind': 'plugin_display_candidate', 'plugin': 'TaleOfTwoWastelands.esm',
                         'owner': 'fallout3.esm', 'id': '0b99a7', 'signature': 'NOTE',
                         'edid': 'CitadelTerminalMedical1', 'field': 'TNAM',
                         'field_occurrence': 0, 'source': text, 'mixed_korean': False,
                         'existing_translation': '', 'translation_conflict': False})
            break
    folder = Path(tempfile.mkdtemp(prefix='sst-language-audit-', dir=ROOT / '.local'))
    for name, items in (('plugin_candidates', rows), ('script_candidates', []),
                        ('loose_candidates', []), ('bsa_ui_candidates', [])):
        with (folder / (name + '.jsonl')).open('x', encoding='utf-8') as stream:
            for row in items:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('SST_LANGUAGE_AUDIT', folder, 'LOCATIONS', len(rows), flush=True)


if __name__ == '__main__':
    main()
