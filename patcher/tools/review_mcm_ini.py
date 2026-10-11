"""Audit and build detached, version-pinned Nuclear Sunset MCM review output."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.loose_translation import decode, json_values
from nskr_output import check_pair, ini_rows, merge_loose, stable_context

SEEDS = (
    'mcm_ini_translation_seed_20261010.json',
    'mcm_npcdodge_translation_seed_20261010.json',
    'mcm_five_mods_translation_seed_20261010.json',
)


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(row, kind):
    if kind == 'json':
        return json.dumps(json.loads(row['context']), ensure_ascii=False, sort_keys=True)
    return row['section'], row['key']


def items(text, kind):
    if kind == 'ini':
        return list(ini_rows(text))
    obj = json.loads(text)
    return [{'pointer': list(pointer), 'source': source,
             'context': stable_context(obj, list(pointer))}
            for pointer, source in json_values(obj)]


def seed_entries(repo):
    for name in SEEDS:
        data = load(repo / '.local' / name)
        if data.get('translation_ready') or data.get('release_ready'):
            raise ValueError('Seed must stay unreleased')
        for row in data['entries']:
            yield {**row, 'file': row.get('file', data.get('source_file'))}


def audit(args):
    repo = Path(__file__).resolve().parents[1]
    index = defaultdict(list)
    sources = [('VNV', args.vnv),
               ('NS_PREP', repo / '.local/ns-sst-with-nexus-quest-esp-v2/catalog.json'),
               ('NS_DIRECT', repo / 'data/mcm_direct_mappings.json')]
    for origin, path in sources:
        catalog = load(path)
        if origin == 'NS_PREP' and catalog.get('translation_ready') is not False:
            raise ValueError('Existing Nuclear Sunset catalog must stay unreleased')
        for info in catalog['files']:
            kind = info.get('kind', 'json')
            if kind not in ('json', 'ini'):
                continue
            for row in info.get('mappings', []):
                index[(info['path'].casefold(), identity(row, kind), row['source'])].append(
                    {'dest': row['dest'], 'origin': origin})
    seeds = defaultdict(list)
    for row in seed_entries(repo):
        seeds[(row['file'].casefold(), row['source'], row.get('section', ''),
               row.get('ini_key', ''))].append(row['dest'])
    with (args.workspace / '00_MCM_번역대상목록.csv').open(encoding='utf-8-sig', newline='') as stream:
        providers = {r['virtual_path'].casefold(): r['provider'] for r in csv.DictReader(stream)}
    work = {'translation_ready': False, 'workspace': str(args.workspace.resolve()),
            'installation': str(args.installation.resolve()),
            'reference_hashes': {str(p): sha(p) for _, p in sources},
            'files': [], 'pending': [], 'conflicts': []}
    pending = {}
    for category in ('05_MCM_JSON', '06_Translations_INI'):
        for source in sorted((args.workspace / category).rglob('*')):
            if source.suffix not in ('.json', '.ini'):
                continue
            virtual = source.relative_to(args.workspace / category).as_posix()
            kind = source.suffix[1:]
            text, encoding = decode(source)
            provider = providers[virtual.casefold()]
            installed = args.installation / 'mods' / provider / virtual
            if sha(installed) != sha(source):
                raise ValueError(f'Installed source differs: {installed}')
            info = {'path': virtual, 'kind': kind, 'provider': provider,
                    'source': str(source), 'installed': str(installed),
                    'baseline_sha256': sha(source), 'encoding': encoding, 'mappings': []}
            for row in items(text, kind):
                old = index.get((virtual.casefold(), identity(row, kind), row['source']), [])
                seed = seeds.get((virtual.casefold(), row['source'], row.get('section', ''),
                                  row.get('key', '')), [])
                choices = {r['dest'] for r in old}
                drafts = set(seed)
                mapping = dict(row)
                if len(choices | drafts) > 1:
                    work['conflicts'].append({'file': virtual, **row, 'existing': old, 'seed': seed})
                if len(choices | drafts) == 1:
                    mapping['dest'] = next(iter(choices | drafts))
                    mapping['origin'] = 'SEED' if drafts else ('VNV' if any(r['origin'] == 'VNV' for r in old) else 'NS_EXISTING')
                    check_pair(row['source'], mapping['dest'])
                else:
                    key = virtual, row['source']
                    if key not in pending:
                        pending[key] = str(len(pending) + 1)
                        work['pending'].append({'id': pending[key], 'file': virtual,
                                                'source': row['source'], 'context': identity(row, kind)})
                    mapping['pending_id'] = pending[key]
                info['mappings'].append(mapping)
            work['files'].append(info)
    if len(work['files']) != 37:
        raise ValueError('Expected exactly 37 source files')
    review = Path(tempfile.mkdtemp(prefix='12_MCM_INI_검수_', dir=args.workspace))
    save(review / 'work.json', work)
    save(review / 'pending.json', work['pending'])
    print(json.dumps({'review': str(review), 'files': len(work['files']),
                      'entries': sum(len(f['mappings']) for f in work['files']),
                      'pending_unique': len(work['pending']), 'conflicts': len(work['conflicts'])}, ensure_ascii=False))


def verify(source, candidate, info):
    original, original_encoding = decode(source)
    translated, candidate_encoding = decode(candidate)
    if original_encoding != candidate_encoding:
        raise ValueError('Encoding changed')
    if re.findall(r'\r\n|\r|\n', original) != re.findall(r'\r\n|\r|\n', translated):
        raise ValueError('Line endings changed')
    before, after = items(original, info['kind']), items(translated, info['kind'])
    if len(before) != len(after) or len(before) != len(info['mappings']):
        raise ValueError('Display entry count changed')
    for old, new, mapping in zip(before, after, info['mappings']):
        if identity(old, info['kind']) != identity(new, info['kind']):
            raise ValueError('Display identity changed')
        if old['source'] != mapping['source'] or new['source'] != mapping['dest']:
            raise ValueError('Translation does not match mapping')
        check_pair(old['source'], new['source'])
    if info['kind'] == 'json':
        restored = json.loads(translated)
        for row in before:
            current = restored
            for part in row['pointer'][:-1]:
                current = current[part]
            current[row['pointer'][-1]] = row['source']
        if restored != json.loads(original):
            raise ValueError('Non-display JSON data changed')
        # Compare every byte outside string literals, including punctuation and indentation.
        string = r'"(?:[^"\\]|\\.)*"'
        if re.sub(string, '""', original) != re.sub(string, '""', translated):
            raise ValueError('JSON formatting changed')
    else:
        restored = translated.splitlines(keepends=True)
        originals = original.splitlines(keepends=True)
        changed_lines = {row['line'] for row in before}
        for number, (old, new) in enumerate(zip(originals, restored)):
            if number in changed_lines:
                if old.split('=', 1)[0] != new.split('=', 1)[0]:
                    raise ValueError('INI key changed')
                restored[number] = old
        if ''.join(restored) != original:
            raise ValueError('INI non-display data changed')


def build(args):
    work = load(args.review / 'work.json')
    translations = {}
    paths = sorted(args.translations.glob('*.json')) if args.translations.is_dir() else [args.translations]
    for path in paths:
        chunk = load(path)
        if translations.keys() & chunk.keys():
            raise ValueError(f'Duplicate translation IDs in {path}')
        translations.update(chunk)
    expected = {row['id'] for row in work['pending']}
    if set(translations) != expected:
        raise ValueError(f'Missing/extra translations: {expected - set(translations)} / {set(translations) - expected}')
    pending_sources = {row['id']: row['source'] for row in work['pending']}
    for key, value in translations.items():
        if isinstance(value, dict):
            other = value['same_as']
            if pending_sources[key] != pending_sources[other]:
                raise ValueError(f'Alias source mismatch: {key} / {other}')
            value = translations[other]
            if not isinstance(value, str):
                raise ValueError(f'Alias must reference a translated string: {key}')
            translations[key] = value
        elif value is None:
            translations[key] = pending_sources[key]
    seed_reviews = {(r['file'], r['source']): r['dest'] for r in load(args.seed_reviews)}
    applied_reviews = set()
    output = args.review / 'Output'
    if output.exists() or (args.review / 'catalog.json').exists():
        raise FileExistsError(output)
    counts = Counter()
    unique = defaultdict(set)
    rendered = []
    catalog = {'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
               'translation_ready': False, 'review_only': True, 'files': []}
    for info in work['files']:
        source, installed = Path(info['source']), Path(info['installed'])
        for path in (source, installed):
            if sha(path) != info['baseline_sha256']:
                raise ValueError(f'Source changed: {path}')
        entry = {k: info[k] for k in ('path', 'kind', 'provider', 'baseline_sha256')}
        entry['mappings'] = []
        for row in info['mappings']:
            mapping = dict(row)
            review_key = info['path'], mapping['source']
            if review_key in seed_reviews:
                if mapping.get('origin') != 'SEED':
                    raise ValueError('Seed review must match an existing draft')
                mapping['dest'] = seed_reviews[review_key]
                applied_reviews.add(review_key)
            if 'pending_id' in row:
                mapping['dest'] = translations[row['pending_id']]
                mapping['origin'] = 'NEW'
            check_pair(mapping['source'], mapping['dest'])
            counts['display_entries'] += 1
            if mapping['source'] != mapping['dest']:
                counts['translated'] += 1
                counts[mapping['origin']] += 1
                unique[mapping['origin']].add((info['path'], mapping['source']))
            else:
                counts['retained'] += 1
            entry['mappings'].append(mapping)
        raw, stats = merge_loose(installed, entry)
        if stats['unmatched']:
            raise ValueError(f'Unmatched mappings: {info["path"]}')
        relative = Path('mods') / info['provider'] / info['path']
        rendered.append((relative, raw, info, entry, stats))
        catalog['files'].append(entry)
    if applied_reviews != seed_reviews.keys():
        raise ValueError('Unmatched seed review')
    output.mkdir()
    results = []
    for relative, raw, info, entry, stats in rendered:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(raw)
        verify(Path(info['source']), target, entry)
        for path in (Path(info['source']), Path(info['installed'])):
            if sha(path) != info['baseline_sha256']:
                raise ValueError(f'Source changed after output: {path}')
        results.append({'path': info['path'], 'output': relative.as_posix(),
                        'source_sha256': info['baseline_sha256'], 'output_sha256': sha(target),
                        'encoding': info['encoding'], **stats})
    for path, digest in work['reference_hashes'].items():
        if sha(Path(path)) != digest:
            raise ValueError(f'Reference catalog changed: {path}')
    save(args.review / 'catalog.json', catalog)
    report = {'translation_ready': False, 'game_test': 'not_run',
              'output': str(output), 'files': results, 'counts': dict(counts),
              'unique_translations_by_origin': {k: len(v) for k, v in unique.items()},
              'seed_review_corrections': len(applied_reviews),
              'missing': 0, 'errors': 0,
              'checks': ['source_and_installed_hashes', 'protected_tokens', 'encoding',
                         'line_endings', 'json_reparse', 'non_display_data', 'exact_mapping',
                         'reference_catalog_hashes']}
    save(args.review / 'validation.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, ensure_ascii=False))


def seed_output(args):
    """Backward-compatible seed-only test, using the same lossless merger."""
    if args.output.exists():
        raise FileExistsError(args.output)
    repo = Path(__file__).resolve().parents[1]
    grouped = defaultdict(list)
    for row in seed_entries(repo):
        grouped[row['file']].append(row)
    rendered, results = [], []
    matched = set()
    for virtual, seeds in sorted(grouped.items()):
        if Path(virtual).is_absolute() or '..' in Path(virtual).parts or '\\' in virtual:
            raise ValueError('Unsafe seed path')
        kind = Path(virtual).suffix[1:]
        category = '05_MCM_JSON' if kind == 'json' else '06_Translations_INI'
        source = args.workspace / category / virtual
        text, encoding = decode(source)
        entry = {'path': virtual, 'kind': kind, 'mappings': []}
        for item in items(text, kind):
            matches = [r for r in seeds if r['source'] == item['source']
                       and (kind == 'json' or (r['section'], r['ini_key']) == (item['section'], item['key']))]
            choices = {r['dest'] for r in matches}
            if len(choices) > 1:
                raise ValueError('Conflicting seed translations')
            if matches:
                matched.add((virtual, item['source'], item.get('section'), item.get('key')))
            entry['mappings'].append({**item, 'dest': next(iter(choices)) if choices else item['source']})
        raw, stats = merge_loose(source, entry)
        rendered.append((source, args.output / virtual, raw, entry, sha(source), encoding, stats))
    expected = {(r['file'], r['source'], r.get('section'), r.get('ini_key'))
                for r in seed_entries(repo)}
    if matched != expected:
        raise ValueError(f'Unmatched seeds: {expected - matched}')
    args.output.mkdir(parents=True)
    for source, target, raw, entry, digest, encoding, stats in rendered:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(raw)
        verify(source, target, entry)
        if sha(source) != digest:
            raise ValueError(f'Source changed: {source}')
        results.append({'file': entry['path'], 'source_sha256': digest,
                        'candidate_sha256': sha(target), 'original_unchanged': True,
                        'encoding': encoding, **stats})
    report = {'translation_ready': False, 'applied_to_game': False,
              'source_files': len(results), 'translated_unique_source_keys': len(expected),
              'translated_occurrences': sum(r['translated'] for r in results), 'files': results}
    save(args.output / '00_REVIEW_STATUS.json', report)
    print(json.dumps({'files': len(results), 'unique': len(expected),
                      'translated': report['translated_occurrences'],
                      'output': str(args.output), 'release_ready': False}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    first = commands.add_parser('audit')
    first.add_argument('--workspace', type=Path, required=True)
    first.add_argument('--installation', type=Path, required=True)
    first.add_argument('--vnv', type=Path, required=True)
    second = commands.add_parser('build')
    second.add_argument('--review', type=Path, required=True)
    second.add_argument('--translations', type=Path, required=True)
    second.add_argument('--seed-reviews', type=Path, required=True)
    third = commands.add_parser('seed')
    third.add_argument('--workspace', type=Path, required=True)
    third.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    {'audit': audit, 'build': build, 'seed': seed_output}[args.command](args)


if __name__ == '__main__':
    main()
