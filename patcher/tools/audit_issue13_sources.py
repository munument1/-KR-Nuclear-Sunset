"""Verify issue #13 on explicitly supplied real ESP/script copies, outside MO2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nskr_issue13 import SCRIPT_CASES, translate_runtime_plugin, name_entries, digest
from nskr_nvse import merge_script
from nskr_compiled_scpt import _walk, _decode_record, _slots


def unique(root, filename):
    paths = list(root.rglob(filename))
    if len(paths) != 1:
        raise ValueError(f'Expected one source {filename}, found {len(paths)}')
    return paths[0]


def independent_compare(source, target):
    """Compare all raw unrelated records and every affected SCPT subrecord."""
    def records(raw):
        result = []
        def visit(header, data):
            result.append((header, data))
            return data
        if _walk(raw, visit) != raw:
            raise ValueError('Invalid input/output framing')
        return result
    a, b = records(source.read_bytes()), records(target.read_bytes())
    if len(a) != len(b):
        raise ValueError('Record count changed')
    allowed = {c['formid'] for c in SCRIPT_CASES if c['plugin'].casefold() == source.name.casefold()}
    modified, untouched = 0, 0
    for (ha, da), (hb, db) in zip(a, b):
        if ha == hb and da == db:
            untouched += 1
            continue
        if (ha[:4] != b'SCPT' or struct.unpack_from('<I', ha, 12)[0] not in allowed
                or ha[:4] + ha[8:] != hb[:4] + hb[8:]):
            raise ValueError('Unexpected unrelated record/header change')
        fa, fb = list(_slots(_decode_record(ha, da))), list(_slots(_decode_record(hb, db)))
        if len(fa) != len(fb):
            raise ValueError('Subrecord count changed')
        for (ka, hfa, va), (kb, hfb, vb) in zip(fa, fb):
            if ka != kb or (ka not in {b'SCDA', b'SCTX'} and hfa + va != hfb + vb):
                raise ValueError('Non-text SCPT metadata changed')
            if ka == b'SCDA' and len(va) != len(vb):
                raise ValueError('Compiled size changed')
        modified += 1
    return {'changed_scripts': modified, 'unrelated_records_byte_identical': untouched,
            'total_records': len(a)}


def audit(plugin_root, loose_root, output):
    plugin_root, loose_root, output = (p.resolve() for p in (plugin_root, loose_root, output))
    if output.exists() or output.is_relative_to(plugin_root) or output.is_relative_to(loose_root):
        raise ValueError('Output must be new and outside both source trees')
    report = {'plugins': [], 'loose_scripts': [], 'in_game_validation': 'not_run'}
    for name in sorted({c['plugin'] for c in SCRIPT_CASES}):
        source = unique(plugin_root, name)
        target = output / 'verified' / name
        result = translate_runtime_plugin(source, target)
        result.update(independent_compare(source, target), plugin=name)
        second = output / 'reapply' / name
        replay = translate_runtime_plugin(target, second)
        if target.read_bytes() != second.read_bytes() or replay['translated']:
            raise ValueError('Actual plugin replay not idempotent')
        report['plugins'].append(result)
    for entry in name_entries():
        source = unique(loose_root, Path(entry['path']).name)
        before = source.read_bytes()
        raw, stats = merge_script(source, entry)
        if stats['unmatched'] or stats['translated'] + stats['already_translated'] == 0:
            raise ValueError('Actual loose script did not match')
        target = output / 'verified' / entry['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        replay, replay_stats = merge_script(target, entry)
        if raw != replay or replay_stats['translated'] or source.read_bytes() != before:
            raise ValueError('Actual loose script replay/source preservation failed')
        report['loose_scripts'].append({'file': entry['path'], 'source_sha256': digest(before),
                                       'output_sha256': digest(raw), **stats})
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin-root', required=True, type=Path)
    parser.add_argument('--loose-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.plugin_root, args.loose_root, args.output), ensure_ascii=False, indent=2))
