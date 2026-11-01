"""Hash-pinned, source-only fixer for Aid Addon's dynamically named healing item.

The game scripts compute display text in LNSetName at runtime, overriding the
already-translated ALCH/MGEF records. We edit only literal payloads in two
verified SCPT records, preserving every byte of the compiled instruction stream
other than those literal bytes. All work must occur in a detached output file.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from nskr_compiled_scpt import _walk, _slots, _decode_record, _encode_record, _with_payload
from nskr_dynamic_display import digest
from nskr_notifications import QUOTED

PROVIDER = '[FL] [OP] - Aid Addon'
RELATIVE_PATH = 'Aid Addon.esp'
ORIGINAL_SHA256 = 'dbdb4d5a09026746dd87678879065f66298a496fff8e582c4294085e35a9902f'
APPROVED = {
    'SCPTUpdateDummyNamesCall': (
        '351cc32cee597ebb77e87539737aa8b2276a93a28b77f4fa188e17c78f10ea2f',
        '95c6e2298dde35b57977b8be878ec9a7c9a9ddc5a27cd68b26d07d71a2e13906',
    ),
    'SCPTUpdateDummyNamesHandler': (
        '77156fc00a99e362e0c63a62b6e07f87bb330c1e0de1f0568075a4c43754c860',
        '857510b60cf39fe0ee0e684943526129509385449fb473073bda28f0b98639a4',
    ),
}

# An exact byte-budget replacement, in the game's CP949 display-string path.
# `"% of max health"` is not a printf argument; its percent sign follows a
# previously concatenated number. The generic script_editor wrongly parses
# the sequence "% o" as a format token, so use an exact literal-count guard.
# The trailing spaces on the second SCDA operand are deliberately inside its
# original 15-byte slot; no compiled opcode offsets or lengths can shift.
PAIRS = (
    ('Restores ', '회복량:  '),
    ('% of max health', '% (최대 체력)'),
    ('Restores one limb by ', '한 부위의 체력 회복: '),
)
COUNTS = {'Restores ': 7, '% of max health': 6,
          'Restores one limb by ': 1}


def replace_literals(source: bytes, code: bytes):
    original_source, original_code = source, code
    changed_ranges = []
    stats = {}
    for old, dest in PAIRS:
        old_bytes = old.encode('ascii')
        utf8_dest = dest.encode('utf-8')
        cp949_dest = dest.encode('cp949')
        budget = len(old_bytes)
        if len(cp949_dest) > budget:
            raise ValueError(f'CP949 literal exceeds compiled budget: {old}')
        quoted_old = b'"' + old_bytes + b'"'
        if source.count(quoted_old) != COUNTS[old]:
            raise ValueError(f'Unapproved quoted source count: {old}')
        positions = []
        start = 0
        while True:
            at = code.find(old_bytes, start)
            if at < 0:
                break
            start = at + 1
            # A substring inside `Restores one limb by ` is not a separate
            # compiled string: its length operand is 21 rather than 9.
            if at < 2 or struct.unpack_from('<H', code, at - 2)[0] != budget:
                continue
            positions.append(at)
        if len(positions) != COUNTS[old]:
            raise ValueError(f'Unapproved SCDA string operand count: {old}: {positions}')
        for at in positions:
            before = code[at:at + budget]
            if before != old_bytes:
                raise ValueError('Overlapping compiled literal replacement')
            replacement = cp949_dest.ljust(budget, b' ')
            code = code[:at] + replacement + code[at + budget:]
            changed_ranges.append((at, before))
        source = source.replace(quoted_old, b'"' + utf8_dest + b'"')
        stats[old] = len(positions)
    if QUOTED.sub(b'""', source) != QUOTED.sub(b'""', original_source):
        raise ValueError('Script commands or unquoted source changed')
    reconstructed = bytearray(code)
    for at, original in changed_ranges:
        reconstructed[at:at + len(original)] = original
    if bytes(reconstructed) != original_code or len(code) != len(original_code):
        raise ValueError('Compiled bytes outside approved literals changed')
    return source, code, stats


def patch_bytes(data: bytes):
    changed = {}
    def visit(header: bytes, payload: bytes) -> bytes:
        if header[:4] != b'SCPT':
            return payload
        slots = list(_slots(_decode_record(header, payload)))
        edid = next((v.rstrip(b'\0').decode('ascii') for k, _, v in slots
                     if k == b'EDID'), '')
        if edid not in APPROVED:
            return payload
        if edid in changed:
            raise ValueError('Duplicate target script ID')
        positions = {k: i for i, (k, _, _) in enumerate(slots)}
        if b'SCTX' not in positions or b'SCDA' not in positions:
            raise ValueError(f'Missing script source/compiled pair: {edid}')
        src = slots[positions[b'SCTX']][2]
        code = slots[positions[b'SCDA']][2]
        if digest(src, code) != APPROVED[edid]:
            raise ValueError(f'Script hash changed, refusing unsafe edit: {edid}')
        translated_source, translated_code, stats = replace_literals(src, code)
        substitutions = {positions[b'SCTX']: translated_source,
                         positions[b'SCDA']: translated_code}
        changed[edid] = stats
        record = b''.join(_with_payload(field_header, substitutions.get(i, v))
                          for i, (_, field_header, v) in enumerate(slots))
        return _encode_record(header, record)
    output = _walk(data, visit)
    if set(changed) != set(APPROVED):
        raise ValueError('One or both reviewed scripts were not found')
    return output, changed


def finalize(installation, stage, files):
    """Apply only after native plugin record merging and dynamic script patches.

    Both target scripts are absent from the 1.0.10 translated record mappings;
    their reviewed SCTX/SCDA hashes must therefore remain unchanged. If not,
    stop rather than overwrite an unknown compiled script variant.
    """
    import nskr

    provider = PROVIDER.casefold()
    expected = ('mods/' + PROVIDER + '/' + RELATIVE_PATH).casefold()
    matched = [row for row in files
               if row.get('output_path', '').casefold() == expected
               and row.get('provider', PROVIDER).casefold() == provider]
    if not matched:
        return
    if len(matched) != 1:
        raise ValueError('Ambiguous Aid Addon translation output providers')
    row = matched[0]
    target = nskr.contained(stage, row['output_path'])
    before = target.read_bytes()
    after, changes = patch_bytes(before)
    if before == after:
        raise ValueError('Aid Addon dynamic description did not change')
    target.write_bytes(after)
    if target.read_bytes() != after:
        raise ValueError('Aid Addon dynamic description readback failed')
    row['medical_bag_dynamic'] = changes
    row['status'] += '; medical_bag_runtime_name_verified'
    row['output_sha256'] = nskr.sha256(target)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    options = parser.parse_args()
    source = options.source.resolve()
    output = options.output.resolve()
    if source == output:
        raise ValueError('Source and output must be different paths')
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('Input plugin changed from approved Aid Addon base')
    result, stats = patch_bytes(raw)
    if result == raw:
        raise ValueError('No changes applied')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
    if output.read_bytes() != result:
        raise ValueError('Output readback mismatch')
    print('input_sha256', hashlib.sha256(raw).hexdigest())
    print('output_sha256', hashlib.sha256(result).hexdigest())
    print('output_path', str(output))
    print('script changes', stats)


if __name__ == '__main__':
    main()
