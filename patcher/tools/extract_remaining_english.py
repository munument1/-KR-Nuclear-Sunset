"""Extract remaining English candidates from the current test VFS, without installation edits."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from tools.loose_translation import decode, json_values
from tools.tes4_text_scan import masters, plugin_records, clean_text, field_occurrences
from tools.translation_field_policy import skip_reason
from nskr_output import translation_companion, ini_rows

ENGLISH = re.compile(r'[A-Za-z]{2,}')
HANGUL = re.compile(r'[가-힣]')
QUOTED = re.compile(r'"((?:[^"]|"")*)"')
DISPLAY_COMMAND = re.compile(
    r'\b(?:Message(?:Box)?(?:Ex)?|SetUIString(?:Ex)?|DebugNotification)\b', re.I)
XML_COMMENT = re.compile(r'<!--.*?-->', re.S)
XML_STRING = re.compile(r'<string\b[^>]*>(.*?)</string\s*>', re.I | re.S)


def english(text):
    return isinstance(text, str) and bool(ENGLISH.search(text))


def xtranslator_fields(path):
    """Read xTranslator's FalloutNV definition data; conditional fields stay review-only."""
    definitions = defaultdict(set)
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.startswith('Def_:'):
            continue
        field, signature, options = line[5:].split('=')
        definitions[signature].add(field)
    return definitions


def extract():
    installation = nskr.Installation(
        Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    catalog = nskr.read_json(
        ROOT / 'dist/NuclearSunset-Dev-0_1189_j/TranslationData/catalog.json')
    output = Path(tempfile.mkdtemp(prefix='remaining-english-', dir=ROOT / '.local'))
    memory = defaultdict(set)
    for entry in catalog['files']:
        if entry['kind'] != 'plugin-records':
            continue
        for row in entry['mappings']:
            memory[(row['owner'].casefold(), row['id'].casefold(), row['signature'],
                    row['field'], row['source'].replace('\r\n', '\n'))].add(row['dest'])
    definition_path = Path(sys.argv[1])
    fields = xtranslator_fields(definition_path)
    winners = {}
    script_winners = {}
    hashes = {}
    counts = Counter()
    problems = []
    for number, plugin in enumerate(installation.active, 1):
        source = installation.source(plugin)
        hashes[source] = nskr.sha256(source)
        names = [n.casefold() for n in masters(source)] + [plugin.casefold()]
        for fid, signature, slots in plugin_records(source):
            counts['records_scanned'] += 1
            owner_index = fid >> 24
            if owner_index >= len(names):
                problems.append({'plugin': plugin, 'formid': f'{fid:08x}',
                                 'reason': 'owner_out_of_range'})
                continue
            identity = names[owner_index], f'{fid & 0xffffff:06x}', signature
            editor = next((clean_text(raw) for field, raw in slots if field == 'EDID'), '') or ''
            rows = []
            script_rows = []
            for field, occurrence, raw in field_occurrences(slots):
                if signature == 'SCPT' and field == 'SCTX':
                    try:
                        script = raw.rstrip(b'\0').decode('utf-8')
                    except UnicodeDecodeError:
                        script = raw.rstrip(b'\0').decode('cp1252', errors='replace')
                    if script:
                        for line_number, line in enumerate(script.splitlines(), 1):
                            if DISPLAY_COMMAND.search(line):
                                for match in QUOTED.finditer(line):
                                    if english(match[1]):
                                        script_rows.append({
                                            'kind': 'script_display_literal_review',
                                            'plugin': plugin, 'owner': identity[0],
                                            'id': identity[1], 'edid': editor,
                                            'line': line_number, 'source': match[1],
                                            'context': line})
                if field not in fields.get(signature, set()) | fields.get('****', set()):
                    continue
                if signature == 'TES4' or (signature == 'GMST' and (
                        field != 'DATA' or not editor.startswith('s'))):
                    continue
                text = clean_text(raw) or clean_text(raw, 'cp1252')
                if not english(text) or skip_reason(signature, field, text):
                    continue
                key = (*identity, field, text.replace('\r\n', '\n'))
                choices = memory.get(key, set())
                rows.append({
                    'kind': 'plugin_display_candidate',
                    'plugin': plugin, 'owner': identity[0], 'id': identity[1],
                    'signature': signature, 'edid': editor, 'field': field,
                    'field_occurrence': occurrence, 'source': text,
                    'mixed_korean': bool(HANGUL.search(text)),
                    'existing_translation': next(iter(choices)) if len(choices) == 1 else '',
                    'translation_conflict': len(choices) > 1,
                    'native_path_validation_required': True})
            winners[identity] = rows
            if signature == 'SCPT':
                script_winners[identity] = script_rows
        if number % 30 == 0 or number == len(installation.active):
            print('SCANNED_PLUGINS', number, '/', len(installation.active), flush=True)
    records = [row for rows in winners.values() for row in rows]
    scripts = [row for rows in script_winners.values() for row in rows]
    loose = []
    for key, chain in installation.providers.items():
        chosen = chain[-1]
        if chosen['category'] != 'loose_text_candidate':
            continue
        source = Path(chosen['physical'])
        suffix = source.suffix.casefold()
        hashes[source] = nskr.sha256(source)
        try:
            text, encoding = decode(source)
        except UnicodeError as error:
            problems.append({'path': chosen['path'], 'reason': str(error)})
            continue
        base = {'path': chosen['path'], 'provider': chosen['provider'], 'encoding': encoding}
        if suffix == '.json' and key.startswith('mcm/'):
            companion = translation_companion(installation, chosen['path'])
            if companion:
                counts['json_preserved_for_translation_companion'] += 1
                continue
            try:
                values = json_values(json.loads(text))
                for pointer, value in values:
                    if english(value):
                        loose.append({**base, 'kind': 'mcm_display', 'pointer': list(pointer),
                                      'source': value, 'mixed_korean': bool(HANGUL.search(value))})
            except (ValueError, TypeError) as error:
                problems.append({**base, 'reason': str(error)})
        elif suffix == '.xml' and key.startswith(('menus/', 'interface/')):
            # Fallout menu files are fragments with engine-defined entities,
            # not standalone XML documents. Extract literal string traits only.
            fragment = XML_COMMENT.sub('', text)
            for index, match in enumerate(XML_STRING.finditer(fragment)):
                value = match[1].strip()
                if '<' not in value and english(value):
                    loose.append({**base, 'kind': 'xml_text_review', 'element_index': index,
                                  'tag': 'string', 'source': value})
        elif suffix in ('.txt', '.ini'):
            if suffix == '.ini' and key.startswith(('config/', 'nvse/')):
                for row in ini_rows(text):
                    if row['key'].startswith('s') and english(row['source']):
                        loose.append({**base, **row, 'kind': 'ini_string_value_review'})
            for line_number, line in enumerate(text.splitlines(), 1):
                if DISPLAY_COMMAND.search(line) and not line.lstrip().startswith((';', '#')):
                    for match in QUOTED.finditer(line):
                        if english(match[1]):
                            loose.append({**base, 'kind': 'script_display_literal_review',
                                          'line': line_number, 'source': match[1], 'context': line})
                if suffix == '.ini' and 'translations/' in key and '=' in line:
                    name, value = line.split('=', 1)
                    if not name.lstrip().startswith((';', '#')) and english(value):
                        loose.append({**base, 'kind': 'translation_ini_review',
                                      'line': line_number, 'key': name, 'source': value})
    for source, before in hashes.items():
        if nskr.sha256(source) != before:
            raise RuntimeError('Source changed while extracting: ' + str(source))
    groups = defaultdict(list)
    for index, row in enumerate(records + scripts + loose):
        groups[row['source']].append(index)
    for name, rows in (('plugin_candidates.jsonl', records),
                       ('script_candidates.jsonl', scripts),
                       ('loose_candidates.jsonl', loose),
                       ('parse_issues.jsonl', problems)):
        with (output / name).open('x', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    with (output / 'unique_sources.jsonl').open('x', encoding='utf-8') as stream:
        for text, indexes in groups.items():
            stream.write(json.dumps({'source': text, 'locations': len(indexes),
                                     'translation': ''}, ensure_ascii=False) + '\n')
    print(json.dumps({
        'output': str(output), 'active_plugins_scanned': len(installation.active),
        'records_scanned': counts['records_scanned'],
        'winning_plugin_candidates': len(records),
        'english_only_plugin_candidates': sum(not r['mixed_korean'] for r in records),
        'existing_exact_translation_candidates': sum(bool(r['existing_translation']) for r in records),
        'embedded_script_candidates': len(scripts), 'loose_candidates': len(loose),
        'unique_sources': len(groups), 'parse_issues': len(problems),
        'source_files_unchanged': len(hashes),
        'json_preserved_for_translation_companion': counts['json_preserved_for_translation_companion'],
        'xtranslator_definition_sha256': nskr.sha256(definition_path),
        'scope_limitations': [
            'Candidates are not confirmed untranslated text; names, tags and proper nouns require classification.',
            'BSA-only UI/scripts and DLL-generated literals need separate extraction.',
            'Binary candidates require native path validation before application.']},
        ensure_ascii=False), flush=True)


if __name__ == '__main__':
    extract()
