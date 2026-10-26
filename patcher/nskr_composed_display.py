"""Keep reviewed challenge prompts and named notification templates in CP949.

AVIF/PERK names and ALCH/SPEL names already use CP949 in v1.0.7.
Only their reviewed composition inputs are changed here. NPC response text,
conditions, references and embedded scripts remain byte-identical.
"""
from pathlib import Path
import struct

from nskr_compiled_scpt import (_walk, _slots, _decode_record, _encode_record,
                                _with_payload, _masters)
from nskr_perk_display import display_bytes

# Reviewed templates whose inserted AVIF / ALCH / SPEL names use CP949.
CP949_GMSTS = {'schemswornoff', 'schemsaddicted', 'schemswithdrawal',
               'shackineligible'}


def identity(form, owners):
    index = form >> 24
    if index >= len(owners):
        raise ValueError('Composition FormID has no master owner')
    return owners[index].casefold(), form & 0xFFFFFF


def challenge(slots):
    return any(k == b'KNAM' and len(v) == 4 and v != b'\0'*4
               for k, h, v in slots)


def challenge_topics(raw, filename):
    """Find shared DIAL fallbacks, including INFO overrides in other plugins."""
    owners = [*_masters(raw), filename]
    topics = set()

    def scan(start, end, topic=None, depth=0):
        if depth > 32:
            raise ValueError('Excessive composition GRUP nesting')
        pos = start
        while pos < end:
            if pos + 24 > end:
                raise ValueError('Truncated composition record header')
            header = raw[pos:pos+24]
            size = struct.unpack_from('<I', header, 4)[0]
            if header[:4] == b'GRUP':
                if size < 24 or pos + size > end:
                    raise ValueError('Invalid composition GRUP boundary')
                group_type = struct.unpack_from('<I', header, 12)[0]
                parent = (identity(struct.unpack_from('<I', header, 8)[0], owners)
                          if group_type == 7 else topic)
                scan(pos+24, pos+size, parent, depth+1)
                pos += size
            else:
                if pos + 24 + size > end:
                    raise ValueError('Composition record crosses group')
                if header[:4] == b'INFO' and topic is not None:
                    slots = list(_slots(_decode_record(header, raw[pos+24:pos+24+size])))
                    if challenge(slots):
                        topics.add(topic)
                pos += 24 + size
    scan(0, len(raw))
    return topics


def patch_bytes(raw, filename, topics=None):
    owners = [*_masters(raw), filename]
    if topics is None:
        topics = challenge_topics(raw, filename)
    changes, issues = [], []

    def visit(header, payload):
        sig = header[:4]
        if sig not in (b'INFO', b'DIAL', b'GMST'):
            return payload
        data = _decode_record(header, payload)
        slots = list(_slots(data))
        form = struct.unpack_from('<I', header, 12)[0]
        edid = next((v.rstrip(b'\0').decode('ascii') for k,h,v in slots if k == b'EDID'), '')
        field = None
        if sig == b'INFO' and challenge(slots):
            field = b'RNAM'
        elif sig == b'DIAL' and identity(form, owners) in topics:
            field = b'FULL'
        elif sig == b'GMST' and edid.casefold() in CP949_GMSTS:
            field = b'DATA'
        if field is None:
            return payload
        replacements = {}
        for i, (key, h, value) in enumerate(slots):
            if key != field:
                continue
            detail = dict(signature=sig.decode(), form=f'{form:08X}', edid=edid,
                          field=key.decode())
            try:
                converted = display_bytes(value)
            except UnicodeEncodeError:
                issues.append({**detail, 'reason':'unsupported_cp949'})
                continue
            if converted != value:
                replacements[i] = converted
                changes.append({**detail, 'from_encoding':'utf-8', 'to_encoding':'cp949'})
        if not replacements:
            return payload
        out = b''.join(_with_payload(h, replacements.get(i, v))
                       for i,(k,h,v) in enumerate(slots))
        parsed = list(_slots(out))
        restored = b''.join(_with_payload(h, slots[i][2] if i in replacements else v)
                            for i,(k,h,v) in enumerate(parsed))
        if restored != data:
            raise ValueError('Composition edit changed unapproved bytes')
        return _encode_record(header, out)
    return _walk(raw, visit), changes, issues


def finalize(stage, files):
    import nskr
    targets = [(row, nskr.contained(stage, row['output_path'])) for row in files
               if Path(row['output_path']).suffix.casefold() in ('.esm', '.esp')]
    # Resolve master-owned topics before editing any provider: an INFO override
    # may add a challenge to a DIAL whose text is supplied by a different file.
    topics = set()
    for row, target in targets:
        topics.update(challenge_topics(target.read_bytes(), target.name))
    for row, target in targets:
        original = target.read_bytes()
        output, changes, issues = patch_bytes(original, target.name, topics)
        if issues:
            row['composition_review_notes'] = issues
        if changes:
            if target.read_bytes() != original:
                raise ValueError('Composition source changed during finalization')
            target.write_bytes(output)
            if target.read_bytes() != output:
                raise ValueError('Composition output readback failed')
            row['composition_display'] = changes
            row['status'] += '; CP949_composition_readback_verified'
            row['output_sha256'] = nskr.sha256(target)
