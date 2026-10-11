"""Write approved TES4 strings into original bytes, without xEdit serialization."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import struct
import zlib
import hashlib

U32 = struct.Struct('<I')
U16 = struct.Struct('<H')
COMPRESSED = 0x00040000


def record_slots(data):
    """Strictly parse each original subrecord, including its size header."""
    offset = 0
    while offset < len(data):
        start = offset
        if offset + 6 > len(data):
            raise ValueError('Truncated subrecord header')
        field = data[offset:offset + 4]
        size = U16.unpack_from(data, offset + 4)[0]
        offset += 6
        extended = field == b'XXXX'
        if extended:
            if size != 4 or offset + 10 > len(data):
                raise ValueError('Invalid extended subrecord header')
            size = U32.unpack_from(data, offset)[0]
            offset += 4
            field = data[offset:offset + 4]
            offset += 6
        end = offset + size
        if end > len(data):
            raise ValueError('Truncated subrecord payload')
        raw = data[offset:end]
        yield field, data[start:offset], raw
        offset = end


def source_encodings(source):
    values = [source.encode('utf-8') + b'\0']
    try:
        values.append(source.encode('cp1252') + b'\0')
    except UnicodeEncodeError:
        pass
    return values


def replace_record(data, updates):
    """Require exact field/source/count correspondence; ambiguous slots fail closed."""
    replacements = defaultdict(list)
    for row in updates:
        replacements[(row['field'].encode('ascii'), row['source'],
                      row.get('field_occurrence'))].append(row['dest'])
    for destinations in replacements.values():
        if len(set(destinations)) != 1:
            raise ValueError('Different destinations for indistinguishable binary string slots')
    matched = Counter()
    field_occurrences = Counter()
    result = bytearray()
    for field, original_header, raw in record_slots(data):
        occurrence = field_occurrences[field]
        field_occurrences[field] += 1
        candidates = []
        for key in replacements:
            code, source, approved_occurrence = key
            if (code != field or (approved_occurrence is not None
                                  and approved_occurrence != occurrence)):
                continue
            if raw in source_encodings(source):
                candidates.append(key)
        if len(candidates) > 1:
            raise ValueError('Ambiguous binary source encoding')
        if not candidates:
            result.extend(original_header + raw)
        else:
            key = candidates[0]
            matched[key] += 1
            dest = replacements[key][0].encode('utf-8') + b'\0'
            if len(original_header) == 16:
                header = bytearray(original_header)
                U32.pack_into(header, 6, len(dest))
                result.extend(header)
            elif len(dest) > 65535:
                result.extend(b'XXXX' + U16.pack(4) + U32.pack(len(dest)))
                result.extend(field + U16.pack(0))
            else:
                result.extend(field + U16.pack(len(dest)))
            result.extend(dest)
    expected = Counter({key: len(rows) for key, rows in replacements.items()})
    if matched != expected:
        raise ValueError('Binary string slots do not exactly match approved native changes')
    return bytes(result)


def verify_plugin(source: Path, target: Path, updates, masters):
    """Independently compare every byte except approved strings and size/compression bytes."""
    owner_names = [name.casefold() for name in masters] + [source.name.casefold()]
    by_record = defaultdict(list)
    for row in updates:
        by_record[(row['owner'].casefold(), row['id'].casefold(), row['signature'])].append(row)
    verified = []

    def decoded(header, payload):
        if U32.unpack_from(header, 8)[0] & COMPRESSED:
            if len(payload) < 4:
                raise ValueError('Truncated compressed record during verification')
            body = zlib.decompress(payload[4:])
            if len(body) != U32.unpack_from(payload)[0]:
                raise ValueError('Compressed record size mismatch during verification')
            return body
        return payload

    with source.open('rb') as original, target.open('rb') as written:
        def walk(original_end, written_end):
            while original.tell() < original_end:
                a, b = original.read(24), written.read(24)
                if len(a) != 24 or len(b) != 24 or a[:4] + a[8:] != b[:4] + b[8:]:
                    raise ValueError('Non-text record/group header changed')
                sa, sb = U32.unpack_from(a, 4)[0], U32.unpack_from(b, 4)[0]
                if a[:4] == b'GRUP':
                    if (sa < 24 or sb < 24 or original.tell() + sa - 24 > original_end
                            or written.tell() + sb - 24 > written_end):
                        raise ValueError('Invalid verified group boundary')
                    walk(original.tell() + sa - 24, written.tell() + sb - 24)
                    continue
                if original.tell() + sa > original_end or written.tell() + sb > written_end:
                    raise ValueError('Verified record crosses group boundary')
                ra, rb = original.read(sa), written.read(sb)
                fid = U32.unpack_from(a, 12)[0]
                index = fid >> 24
                owner = owner_names[index] if index < len(owner_names) else None
                identity = owner, f'{fid & 0xffffff:06x}', a[:4].decode('ascii')
                rows = by_record.get(identity)
                if not rows:
                    if a != b or ra != rb:
                        raise ValueError('Untranslated record bytes changed')
                    continue
                approvals = {(row['field'].encode('ascii'), row['field_occurrence']): row
                             for row in rows}
                if len(approvals) != len(rows):
                    raise ValueError('Duplicate approved binary positions')
                slots_a = list(record_slots(decoded(a, ra)))
                slots_b = list(record_slots(decoded(b, rb)))
                if len(slots_a) != len(slots_b):
                    raise ValueError('Subrecord count changed')
                occurrences = Counter()
                matched = set()
                for (fa, ha, va), (fb, hb, vb) in zip(slots_a, slots_b):
                    position = fa, occurrences[fa]
                    occurrences[fa] += 1
                    if fa != fb:
                        raise ValueError('Subrecord order changed')
                    row = approvals.get(position)
                    if row is None:
                        if ha + va != hb + vb:
                            raise ValueError('Non-text subrecord bytes changed')
                        continue
                    if va not in source_encodings(row['source']) or vb != row['dest'].encode('utf-8') + b'\0':
                        raise ValueError('Approved binary string readback mismatch')
                    if len(ha) == 16 and (len(hb) != 16 or ha[:6] + ha[10:] != hb[:6] + hb[10:]):
                        raise ValueError('Extended string header metadata changed')
                    if len(ha) == 6 and len(hb) == 16 and (
                            len(vb) <= 65535 or hb[:6] != b'XXXX\x04\0' or hb[10:] != fa + b'\0\0'):
                        raise ValueError('Invalid extended string promotion')
                    matched.add(position)
                if matched != approvals.keys():
                    raise ValueError('Approved binary positions missing')
                verified.append({'owner': identity[0], 'id': identity[1],
                                 'signature': identity[2],
                                 'hash': hashlib.sha256(a + ra).hexdigest()})
            if original.tell() != original_end or written.tell() != written_end:
                raise ValueError('Verified plugin/group boundary mismatch')
        walk(source.stat().st_size, target.stat().st_size)
    if len(verified) != len(by_record):
        raise ValueError('Approved records missing from verified output')
    return verified


def write_plugin(source: Path, target: Path, updates, masters):
    """Stream untouched records verbatim; update only string and size bytes."""
    if source.resolve() == target.resolve():
        raise ValueError('Plugin output must not replace its source')
    by_record = defaultdict(list)
    for row in updates:
        identity = row['owner'].casefold(), row['id'].casefold(), row['signature']
        by_record[identity].append(row)
    applied = set()
    owner_names = [name.casefold() for name in masters] + [source.name.casefold()]
    with source.open('rb') as reader, target.open('xb') as writer:
        file_end = source.stat().st_size

        def copy(size):
            while size:
                chunk = reader.read(min(size, 1024 * 1024))
                if not chunk:
                    raise ValueError('Truncated plugin data')
                writer.write(chunk)
                size -= len(chunk)

        def walk(end):
            while reader.tell() < end:
                header = reader.read(24)
                if len(header) != 24:
                    raise ValueError('Truncated record/group header')
                signature = header[:4]
                size = U32.unpack_from(header, 4)[0]
                if signature == b'GRUP':
                    if size < 24 or reader.tell() + size - 24 > end:
                        raise ValueError('Invalid group size')
                    group_end = reader.tell() + size - 24
                    position = writer.tell()
                    writer.write(header)
                    walk(group_end)
                    final = writer.tell()
                    writer.seek(position + 4)
                    writer.write(U32.pack(final - position))
                    writer.seek(final)
                    continue
                if reader.tell() + size > end:
                    raise ValueError('Record crosses its containing group')
                fid = U32.unpack_from(header, 12)[0]
                owner_index = fid >> 24
                owner = owner_names[owner_index] if owner_index < len(owner_names) else None
                identity = owner, f'{fid & 0xffffff:06x}', signature.decode('ascii')
                rows = by_record.get(identity)
                if not rows:
                    writer.write(header)
                    copy(size)
                    continue
                if identity in applied:
                    raise ValueError('Duplicate changed record identity')
                applied.add(identity)
                raw = reader.read(size)
                flags = U32.unpack_from(header, 8)[0]
                if flags & COMPRESSED:
                    if len(raw) < 4:
                        raise ValueError('Truncated compressed record')
                    data = zlib.decompress(raw[4:])
                    if len(data) != U32.unpack_from(raw)[0]:
                        raise ValueError('Compressed record length mismatch')
                    changed = replace_record(data, rows)
                    payload = U32.pack(len(changed)) + zlib.compress(changed)
                else:
                    payload = replace_record(raw, rows)
                updated_header = bytearray(header)
                U32.pack_into(updated_header, 4, len(payload))
                writer.write(updated_header)
                writer.write(payload)
            if reader.tell() != end:
                raise ValueError('Plugin boundary mismatch')

        walk(file_end)
        if applied != by_record.keys():
            raise ValueError('Native changes refer to missing original records')
