"""Prepare all remaining display candidates, reusing unambiguous saved translations."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr

RESOURCE = re.compile(r'\.(?:dds|nif|kf|wav|ogg|mp3|xml|ini|json|txt|esp|esm|dll|bsa)(?:\s*)$', re.I)
ENTITY = re.compile(r'&[^;]+;')
HANGUL = re.compile('[가-힣]')
COMMAND = re.compile(r'\b(MessageBoxEx|MessageEx|MessageBox|Message|SetUIStringEx|SetUIString)\b', re.I)
QUOTED = re.compile(r'"([^"]*)"')


def load_rows(path):
    with path.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def saved_translation_is_localized(source, destination):
    return bool(HANGUL.search(destination)) or source == destination


def classify(row, translated):
    source = row['source'].strip()
    if source in translated:
        return 'already_translated'
    if not source or ENTITY.fullmatch(source):
        return 'engine_reference'
    if RESOURCE.search(source) and not any(c in source for c in '\r\n'):
        return 'resource_or_file_reference'
    kind = row['kind']
    if kind == 'archive_literal_review':
        if row['tag'].casefold() != 'string':
            return 'archive_non_string_trait_or_reference'
    if kind == 'script_display_literal_review':
        line = row['context'].lstrip()
        if line.startswith(';'):
            return 'commented_script'
        line = line.split(';', 1)[0]
        command = COMMAND.search(line.split('"', 1)[0])
        if not command:
            return 'not_supported_display_command'
        if command[1].lower().startswith('setuistring'):
            strings = QUOTED.findall(line[command.end():])
            if not strings or row['source'] == strings[0]:
                return 'ui_path_argument'
    if kind == 'ini_string_value_review' and row['key'] in {
            'sEditorID', 'sSound', 'sSoundA', 'sSoundB', 'sSoundName', 'sSoundNameAlt',
            'sJumpSound', 'sToggleOffSound', 'sToggleOnSound', 'sFilename',
            'sExtension', 'sTiffCompression', 'sRemoveItemModSound'}:
        return 'ini_non_display_setting'
    if HANGUL.search(source):
        return 'mixed_korean_requires_review'
    return 'translation_candidate'


def main():
    folder, archive_folder = map(Path, sys.argv[1:3])
    catalog = nskr.read_json(ROOT / 'dist/NuclearSunset-Dev-q92bqkq0/TranslationData/catalog.json')
    memory = defaultdict(set)
    translated = set()
    for entry in catalog['files']:
        for row in entry.get('mappings', []):
            if saved_translation_is_localized(row['source'], row['dest']):
                translated.add(row['dest'].strip())
                memory[(row.get('signature', entry['kind']), row.get('field', ''),
                        row['source'].replace('\r\n', '\n'))].add(row['dest'])
    rows = (load_rows(folder / 'plugin_candidates.jsonl')
            + load_rows(folder / 'script_candidates.jsonl')
            + load_rows(folder / 'loose_candidates.jsonl')
            + load_rows(archive_folder / 'bsa_ui_candidates.jsonl'))
    statuses = Counter()
    groups = defaultdict(list)
    classified = []
    for row in rows:
        status = classify(row, translated)
        statuses[status] += 1
        row = {**row, 'classification': status}
        classified.append(row)
        if status not in ('translation_candidate', 'mixed_korean_requires_review'):
            continue
        groups[(row.get('signature', row['kind']), row.get('field', ''), row['source'])].append(row)
    work = Path(tempfile.mkdtemp(prefix='remaining-translation-', dir=ROOT / '.local'))
    (work / 'inputs').mkdir()
    reused, inputs = [], []
    for (signature, field, source), locations in groups.items():
        choices = memory.get((signature, field, source.replace('\r\n', '\n')), set())
        item = {'source': source, 'signature': signature, 'field': field, 'locations': locations}
        if len(choices) == 1:
            reused.append({**item, 'dest': next(iter(choices)), 'origin': 'saved_exact_text'})
        else:
            inputs.append(item)
    batches, group, length = [], [], 0
    for item in inputs:
        if group and (len(group) >= 60 or length + len(item['source']) > 6500):
            batches.append(group)
            group, length = [], 0
        group.append(item)
        length += len(item['source'])
    if group:
        batches.append(group)
    manifest = []
    for number, batch in enumerate(batches, 1):
        filename = f'batch_{number:04d}.json'
        nskr.write_json(work / 'inputs' / filename, batch)
        manifest.append({'file': filename, 'rows': len(batch),
                         'source_sha256': nskr.sha256(work / 'inputs' / filename)})
    nskr.write_json(work / 'manifest.json', {
        'batches': manifest, 'inputs': len(inputs), 'reused': len(reused),
        'classification_counts': dict(statuses), 'translation_ready': False})
    nskr.write_json(work / 'reused.json', reused)
    with (work / 'classified.jsonl').open('x', encoding='utf-8') as stream:
        for row in classified:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps({'work': str(work), 'all_locations': len(rows),
                      'classification_counts': dict(statuses), 'reused_unique': len(reused),
                      'new_unique': len(inputs), 'new_batches': len(batches),
                      'new_characters': sum(len(r['source']) for r in inputs)},
                     ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
