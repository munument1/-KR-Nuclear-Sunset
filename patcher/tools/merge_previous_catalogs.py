"""Add provenance-checked prior Korean text to a *new* Nuclear Sunset catalog.

Use before packaging a replacement release so previously installed Korean
plugins can be upgraded without restoring and re-patching original English
files. Never mutates input catalogs or the installed game.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import nskr
from nskr_xedit import validate_mapping


IDENTITY = ('owner', 'id', 'signature', 'field', 'path', 'source')


def key(entry, row):
    """The source and physical provider must agree, not merely a shared FormID."""
    return (entry['path'].casefold(),
            (entry.get('provider') or '').casefold(),
            *(row.get(part, '').casefold() if part in {'owner', 'id'}
              else row.get(part) for part in IDENTITY))


def merge(current, predecessors):
    if current.get('target_modlist') != 'nuclear-sunset-ttw':
        raise ValueError('Current catalog is not Nuclear Sunset')
    previous_destinations = defaultdict(set)
    for previous in predecessors:
        if (previous.get('target_modlist') != current['target_modlist']
                or previous.get('schema_version') != current.get('schema_version')):
            raise ValueError('A previous catalog targets a different modlist/schema')
        for entry in previous.get('files', []):
            if entry.get('kind') != 'plugin-records':
                continue
            for row in entry.get('mappings', []):
                validate_mapping(row)
                previous_destinations[key(entry, row)].update((
                    row['dest'], *(row.get('previous_dests') or ())))

    changed_rows = 0
    aliases = 0
    for entry in current.get('files', []):
        if entry.get('kind') != 'plugin-records':
            continue
        for row in entry.get('mappings', []):
            existing = set(row.get('previous_dests') or ())
            additions = (previous_destinations.get(key(entry, row), set())
                         - {row['dest'], row['source']} - existing)
            if additions:
                row['previous_dests'] = sorted(existing | additions)
                validate_mapping(row)
                aliases += len(additions)
                changed_rows += 1
    return {'rows_with_new_previous_destinations': changed_rows,
            'new_previous_destinations': aliases,
            'provenance': 'plugin/provider+owner+id+signature+field+path+original English source'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', type=Path, required=True)
    parser.add_argument('--previous', type=Path, required=True, action='append')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in ({args.current.resolve()} | {p.resolve() for p in args.previous}):
        raise ValueError('Output cannot replace an input catalog')
    current = nskr.read_json(args.current)
    summary = merge(current, [nskr.read_json(path) for path in args.previous])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        import json
        json.dump(current, stream, ensure_ascii=False, separators=(',', ':'))
        stream.write('\n')
    print(summary)


if __name__ == '__main__':
    main()
