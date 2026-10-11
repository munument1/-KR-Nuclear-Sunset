"""Independently validate every residual translation and prepare bounded corrective inputs."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from tools.residual_translation_validation import normalize_boundary_whitespace, validate
from tools.prepare_remaining_translation_work import classify

KEEP = {'HP', 'AP', 'XP', 'DPS', 'DT', 'DR', 'FPS', 'FOV', 'VATS', 'V.A.T.S.',
        'SPECIAL', 'S.P.E.C.I.A.L.', 'MCM', 'NVSE', 'TTW', 'Nuclear Sunset',
        'Fallout', 'Fallout 3', 'Fallout: New Vegas', 'Pip-Boy', 'Vault-Tec', 'ED-E'}


def assess(row, editor_ids):
    value = normalize_boundary_whitespace(row['source'], row['dest'])
    source = row['source'].strip()
    if row.get('origin') == 'contextual_retention_candidate':
        if row['dest'] != row['source']:
            raise ValueError('Retention decision modified its source')
        return {**row, 'validation_errors': []}
    classifications = {classify(location, set()) for location in row['locations']}
    if not classifications.intersection({'translation_candidate', 'mixed_korean_requires_review'}):
        return {**row, 'dest': row['source'], 'validation_errors': [],
                'preserve_reason': 'source_schema_non_display:' + ','.join(sorted(classifications))}
    if row['signature'] == 'INFO' and re.fullmatch(r'\{[^{}]*\}', source, re.S):
        return {**row, 'dest': row['source'], 'validation_errors': [],
                'preserve_reason': 'dialogue_brace_comment'}
    if row['signature'] == 'DIAL' and row['field'] == 'FULL' and (
            source in editor_ids or re.fullmatch(r'\{[^{}]*\}', source, re.S)):
        return {**row, 'dest': row['source'], 'validation_errors': [],
                'preserve_reason': 'editor_identifier_or_dialogue_node_comment'}
    if row['signature'] == 'AMMO' and re.fullmatch(
            r'[0-9.]+(?:mm|MG|LR)?(?:[ ,]+[A-Z0-9+./-]+)*', source, re.I):
        return {**row, 'dest': row['source'], 'validation_errors': [],
                'preserve_reason': 'ammunition_caliber_and_type_code'}
    if row['signature'] == 'AMMO' and row['field'] == 'ONAM' and re.fullmatch(
            r'[A-Z]{1,4}(?: [A-Z]{1,4})*', source):
        return {**row, 'dest': row['source'], 'validation_errors': [],
                'preserve_reason': 'ammunition_short_code'}
    reasons = validate(row['source'], value, row['signature'], row['field'])
    if row.get('repair_mask_error') or re.search(r'__NSKR_KEEP_\d{4}__', value):
        reasons.append('corrective_mask_not_restored')
    if (value.strip() == row['source'].strip() and value.strip() not in KEEP
            and row.get('origin') != 'saved_exact_text'):
        reasons.append('unchanged_source_needs_review')
    return {**row, 'dest': value, 'validation_errors': reasons}


def main():
    work = Path(sys.argv[1]).resolve()
    manifest = nskr.read_json(work / 'manifest.json')
    with (work / 'classified.jsonl').open(encoding='utf-8') as stream:
        editor_ids = {r['edid'] for r in map(json.loads, stream)
                      if r.get('edid') and r.get('signature') == 'DIAL'}
    rows = []
    missing = []
    for batch in manifest['batches']:
        source_path = work / 'inputs' / batch['file']
        if nskr.sha256(source_path) != batch['source_sha256']:
            raise ValueError('Translation input changed')
        source = nskr.read_json(source_path)
        result = work / 'results' / batch['file']
        if not result.is_file():
            missing.extend({**row, 'repair_reasons': ['failed_batch_shape']} for row in source)
            continue
        output = nskr.read_json(result)
        if [r['source'] for r in output] != [r['source'] for r in source]:
            raise ValueError('Translation batch identity/order mismatch')
        rows.extend(assess(row, editor_ids) for row in output)
    rows.extend(assess(row, editor_ids) for row in nskr.read_json(work / 'reused.json'))
    if len(sys.argv) > 2:
        repairs = nskr.read_json(Path(sys.argv[2]))
        by_key = {(r['signature'], r['field'], r['source']): r for r in repairs}
        replaced = []
        for row in rows:
            key = row['signature'], row['field'], row['source']
            replaced.append(assess(by_key.pop(key), editor_ids) if key in by_key else row)
        rows = replaced
        for row in missing:
            key = row['signature'], row['field'], row['source']
            if key in by_key:
                rows.append(assess(by_key.pop(key), editor_ids))
        missing = [r for r in missing if (r['signature'], r['field'], r['source']) not in {
            (x['signature'], x['field'], x['source']) for x in repairs}]
        if by_key:
            raise ValueError('Unexpected corrective translation identity')
    accepted = [row for row in rows if not row['validation_errors']]
    held = [{**row, 'repair_reasons': row['validation_errors']}
            for row in rows if row['validation_errors']] + missing
    nskr.write_json(work / 'qa_accepted.json', accepted)
    nskr.write_json(work / 'qa_held.json', held)
    if len(sys.argv) == 2:
        (work / 'repair_inputs').mkdir(exist_ok=True)
        batches = []
        group, chars = [], 0
        for row in held:
            if group and (len(group) >= 20 or chars + len(row['source']) > 3500):
                batches.append(group)
                group, chars = [], 0
            group.append(row)
            chars += len(row['source'])
        if group:
            batches.append(group)
        files = []
        for index, batch in enumerate(batches, 1):
            name = f'repair_{index:04d}.json'
            nskr.write_json(work / 'repair_inputs' / name, batch)
            files.append({'file': name, 'rows': len(batch),
                          'source_sha256': nskr.sha256(work / 'repair_inputs' / name)})
        nskr.write_json(work / 'repair_manifest.json', {'batches': files})
    print(json.dumps({'accepted_unique': len(accepted), 'held_unique': len(held),
                      'preserved_identifiers_and_codes': sum(bool(r.get('preserve_reason')) for r in accepted),
                      'held_reasons': dict(Counter(reason for r in held for reason in r['repair_reasons'])),
                      'missing_api_rows': len(missing)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
