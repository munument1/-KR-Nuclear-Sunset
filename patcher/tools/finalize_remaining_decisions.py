"""Finalize the bounded remainder: explicit UI translations or preserved technical literals."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr

KEEP = {
    'Caps Lock', 'FF', 'SOS', 'NCR?', 'NCR.', 'NCR', 'LAER', 'ED-210', 'DLC',
    'HNVSAGateLockACTIVATOR', 'ARMABBHoloTagFistUnique',
    'DIEOGaryMuggerFaction', 'MQ09DIEOEnclaveBossFaction',
    'TTWRepAddOnStartupQuest', '00legionradioguard', '-20 DT', '-30 DT',
    '%.2fdB', 'dB', 'CellHUD', 'JIP LN NVSE', 'JohnnyGuitarNVSE',
    '/text/string', '/string',
    'X948KJ \r\nL4IERU \r\nER32J7', '10mm.', '9mm.', 'HP +1',
}


def main():
    work = Path(sys.argv[1]).resolve()
    held = nskr.read_json(work / 'qa_held.json')
    explicit = nskr.read_json(ROOT / 'data/remaining_final_manual_mappings.json')
    previous = Path(sys.argv[2]) if len(sys.argv) > 2 else work / 'all_corrective_decisions.json'
    combined = {(r['signature'], r['field'], r['source']): r
                for r in nskr.read_json(previous)}
    handled = 0
    for row in held:
        source = row['source']
        if source in explicit:
            item = {**row, 'dest': explicit[source], 'origin': 'manual_ui_correction',
                    'repair_mask_error': False}
        elif source.strip() in KEEP:
            item = {**row, 'dest': source, 'origin': 'contextual_retention_candidate',
                    'preserve_reason': 'reviewed_standard_abbreviation_unit_or_internal_identifier'}
        elif re.fullmatch(r'(?:\s*\{[^{}]*\})+\s*', source, re.S):
            item = {**row, 'dest': source, 'origin': 'contextual_retention_candidate',
                    'preserve_reason': 'dialogue_authoring_comments_without_spoken_text'}
        elif row['signature'] == 'BOOK' and source.startswith('[Path=ALNewspaper01.xml]'):
            if re.search(r'[^<>\s]+', re.sub(r'<[^>]*>|\[Path=[^\]]+\]', '', source)):
                raise ValueError('Unexpected prose inside an image-only newspaper wrapper')
            item = {**row, 'dest': source, 'origin': 'contextual_retention_candidate',
                    'preserve_reason': 'image_only_book_wrapper_no_textual_body'}
        elif re.search('[가-힣]', source) and row['dest'] == source:
            item = {**row, 'dest': source, 'origin': 'contextual_retention_candidate',
                    'preserve_reason': 'already_korean_with_required_acronym_or_resource_reference'}
        else:
            raise ValueError('Unclassified final source: ' + source)
        combined[(row['signature'], row['field'], source)] = item
        handled += 1
    nskr.write_json(work / 'final_decisions.json', list(combined.values()))
    print('FINAL_REMAINDER_CLASSIFIED', handled, flush=True)


if __name__ == '__main__':
    main()
