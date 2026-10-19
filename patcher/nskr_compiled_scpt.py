"""Surgical translation of two reviewed New Vegas compiled SCPT literals.

The caller passes an explicitly approved source SHA-256, normally from
``tools.audit_issue11_compiled_scripts.CASES``.  When patching a previously
staged/translated ESP, pass its *verified* SHA in a copy of that case dictionary.

    from tools.audit_issue11_compiled_scripts import CASES
    translate_compiled_scpt(source_esp, separate_output_esp, CASES[0])

The output is an ESP copy with the matching SCTX text and embedded SCDA string
bytes replaced.  The preceding SCDA uint16 byte length, SCHR compiled-size
uint32, SCDA/SCTX subrecord sizes, containing record size and all enclosing
GRUP sizes are adjusted.  Every unaffected byte is checked by a separate
structural readback.  Live MO2 files are never valid output destinations.

Compiled string bytes are UTF-8, consistent with this patcher's native text
translation.  Neither this surgical change nor roundtrip verification proves
that a particular runtime xNVSE/JIP/tNVSE combination renders compiled UTF-8
correctly.  In-game validation remains necessary; CP949 is not assumed safe.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import struct
import zlib

from tools.audit_issue11_compiled_scripts import CASES as _REVIEWED_CASES

_COMPRESSED = 0x00040000
_U16 = struct.Struct('<H')
_U32 = struct.Struct('<I')
HEADHUNTER_KO = (
    '적의 두 눈 사이에 총알을 명중시키기 위해 신중하게 조준합니다. '
    '불릿 타임에서 적의 머리를 명중시킬 확률이 25% 증가하는 대신 AP 소모량이 50% 증가합니다. '
    '2단계에서는 엎드린 자세에서 재장전 속도가 25% 증가하고, '
    '불릿 타임에서 적의 머리를 공격할 때 치명타 피해량이 15% 증가합니다.'
)
FAST_SUFFIX_KO = ' 술을 마시면 방사능 수치도 두 배 빠르게 감소합니다.'
_CASE_LITERALS = {
    'SCPTPatchForJBT': HEADHUNTER_KO.replace('%', '%%'),
    'sssSCPTIngestiblesStartup': '%z' + FAST_SUFFIX_KO,
}


def _read_u32(raw: bytes, offset: int = 0) -> int:
    return _U32.unpack_from(raw, offset)[0]


def _slots(raw: bytes):
    """Parse entire record body, rejecting malformed/ambiguous XXXX framing."""
    pos = 0
    while pos < len(raw):
        start = pos
        if pos + 6 > len(raw):
            raise ValueError('Truncated subrecord header')
        field = raw[pos:pos + 4]
        size = _U16.unpack_from(raw, pos + 4)[0]
        pos += 6
        if field == b'XXXX':
            if size != 4 or pos + 10 > len(raw):
                raise ValueError('Invalid XXXX subrecord framing')
            size = _read_u32(raw, pos)
            pos += 4
            field = raw[pos:pos + 4]
            if field == b'XXXX' or _U16.unpack_from(raw, pos + 4)[0] != 0:
                raise ValueError('Invalid extended field header')
            pos += 6
        end = pos + size
        if end > len(raw):
            raise ValueError('Subrecord crosses record boundary')
        yield field, raw[start:pos], raw[pos:end]
        pos = end


def _with_payload(original_header: bytes, data: bytes) -> bytes:
    header = bytearray(original_header)
    if len(header) == 6:
        if len(data) > 65535:
            raise ValueError('Unsupported growth beyond uint16 subrecord size')
        _U16.pack_into(header, 4, len(data))
    elif len(header) == 16 and header[:6] == b'XXXX\x04\0':
        if len(data) > 0xFFFFFFFF:
            raise ValueError('Extended subrecord size overflow')
        _U32.pack_into(header, 6, len(data))
    else:
        raise ValueError('Unknown subrecord header length')
    return bytes(header) + data


def _decode_record(header: bytes, payload: bytes) -> bytes:
    if not _read_u32(header, 8) & _COMPRESSED:
        return payload
    if len(payload) < 4:
        raise ValueError('Compressed record missing decompressed size')
    expected = _read_u32(payload)
    dec = zlib.decompressobj()
    try:
        result = dec.decompress(payload[4:]) + dec.flush()
    except zlib.error as exc:
        raise ValueError('Invalid compressed record') from exc
    if not dec.eof or dec.unused_data or dec.unconsumed_tail or len(result) != expected:
        raise ValueError('Compressed record length/trailing data mismatch')
    return result


def _encode_record(header: bytes, raw: bytes) -> bytes:
    if _read_u32(header, 8) & _COMPRESSED:
        return _U32.pack(len(raw)) + zlib.compress(raw)
    return raw


def _walk(raw: bytes, visit, *, verify_tree=False):
    """Process complete plugin recursively; preserve untouched record bytes."""
    def walk(start: int, end: int, depth: int) -> bytes:
        if depth > 32:
            raise ValueError('Excessive GRUP nesting')
        result = bytearray()
        pos = start
        while pos < end:
            if pos + 24 > end:
                raise ValueError('Truncated TES4 record/group header')
            header = raw[pos:pos + 24]
            size = _read_u32(header, 4)
            if header[:4] == b'GRUP':
                if size < 24 or pos + size > end:
                    raise ValueError('Invalid recursive GRUP size')
                body = walk(pos + 24, pos + size, depth + 1)
                new_header = bytearray(header)
                _U32.pack_into(new_header, 4, 24 + len(body))
                result.extend(new_header + body)
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError('Record extends past containing group')
            data = raw[pos + 24:pos + 24 + size]
            new_data = visit(header, data)
            if new_data is data:
                result.extend(header + data)
            else:
                new_header = bytearray(header)
                _U32.pack_into(new_header, 4, len(new_data))
                result.extend(new_header + new_data)
            pos += 24 + size
        if pos != end:
            raise ValueError('Plugin/group boundary mismatch')
        return bytes(result)
    return walk(0, len(raw), 0)


def _masters(raw: bytes) -> list[str]:
    if len(raw) < 24 or raw[:4] != b'TES4':
        raise ValueError('Plugin does not start with a TES4 record')
    end = 24 + _read_u32(raw, 4)
    if end > len(raw) or _read_u32(raw, 8) & _COMPRESSED:
        raise ValueError('Unexpected TES4 header layout')
    master_names = []
    for key, _, payload in _slots(raw[24:end]):
        if key == b'MAST':
            master_names.append(payload.rstrip(b'\0').decode('ascii'))
    return master_names


def _one(fields, name: bytes) -> tuple[bytes, bytes]:
    found = [(header, value) for key, header, value in fields if key == name]
    if len(found) != 1:
        raise ValueError(f'Expected exactly one {name!r} subrecord')
    return found[0]


def _validate_format(spec: dict, translated: str):
    if spec.get('editor_id') not in _CASE_LITERALS:
        raise ValueError('Unreviewed compiled script identity')
    if translated != _CASE_LITERALS[spec['editor_id']]:
        raise ValueError('Unreviewed or unsafe translated printf format')
    if any(char in translated for char in ('\0', '"', '\r', '\n')):
        raise ValueError('Compiled literal contains unsupported source characters')
    if len(translated.encode('utf-8')) > 65535:
        raise ValueError('Compiled literal exceeds uint16 byte length')


def _change_script(data: bytes, spec: dict) -> tuple[bytes, bytes, bytes]:
    fields = list(_slots(data))
    (_, edid) = _one(fields, b'EDID')
    if edid.rstrip(b'\0') != spec['editor_id'].encode('ascii'):
        raise ValueError('SCPT EDID does not match reviewed script')
    (_, schr) = _one(fields, b'SCHR')
    (_, scda) = _one(fields, b'SCDA')
    (_, sctx) = _one(fields, b'SCTX')
    if len(schr) != 20 or _read_u32(schr, 8) != len(scda):
        raise ValueError('SCHR compiled size does not equal SCDA length')

    source_literals = (spec['source_en'],
                       *spec.get('previous_script_literals', ()),
                       _CASE_LITERALS[spec['editor_id']])
    matches = []
    for source in dict.fromkeys(source_literals):
        if not isinstance(source, str):
            raise ValueError('Script literal must be a string')
        old = source.encode('utf-8')
        if sctx.count(old) == 1 and scda.count(old) == 1:
            matches.append(old)
    if len(matches) != 1:
        raise ValueError(f'Expected one reviewed SCPT literal candidate, got {len(matches)}')
    old = matches[0]
    offset = scda.find(old)
    if offset < 2 or _U16.unpack_from(scda, offset - 2)[0] != len(old):
        raise ValueError('SCDA compiled string uint16 length mismatch')
    command = (rb'\bSetFormDescription\s+' + re.escape(spec['target'].encode('ascii'))
               + rb'\s+"' + re.escape(old) + rb'"')
    if len(list(re.finditer(command, sctx))) != 1:
        raise ValueError('Expected exact SetFormDescription target/quoted literal absent')

    new = _CASE_LITERALS[spec['editor_id']].encode('utf-8')
    if old == new:
        return data, old, new
    updated_scda = (scda[:offset - 2] + _U16.pack(len(new)) + new
                    + scda[offset + len(old):])
    updated_sctx = sctx.replace(old, new, 1)
    changed_schr = bytearray(schr)
    _U32.pack_into(changed_schr, 8, len(updated_scda))
    substitutions = {b'SCHR': bytes(changed_schr), b'SCDA': updated_scda,
                     b'SCTX': updated_sctx}
    updated = b''.join(
        _with_payload(header, substitutions[key]) if key in substitutions else header + payload
        for key, header, payload in fields
    )
    return updated, old, new


def _verify_output(original: bytes, output: bytes, formid: int, old: bytes, new: bytes):
    """Read both complete TES4 trees and compare all unaffected bytes/headers."""
    visited = [0]

    def compare(a_start, a_end, b_start, b_end, depth):
        if depth > 32:
            raise ValueError('Verification GRUP nesting exceeds limit')
        pa, pb = a_start, b_start
        while pa < a_end and pb < b_end:
            if pa + 24 > a_end or pb + 24 > b_end:
                raise ValueError('Verification truncated record/group')
            ha, hb = original[pa:pa + 24], output[pb:pb + 24]
            if ha[:4] + ha[8:] != hb[:4] + hb[8:]:
                raise ValueError('Non-size record/group header changed')
            sa, sb = _read_u32(ha, 4), _read_u32(hb, 4)
            if ha[:4] == b'GRUP':
                if sa < 24 or sb < 24 or pa + sa > a_end or pb + sb > b_end:
                    raise ValueError('Verification invalid GRUP size')
                compare(pa + 24, pa + sa, pb + 24, pb + sb, depth + 1)
                pa += sa
                pb += sb
                continue
            ea, eb = pa + 24 + sa, pb + 24 + sb
            if ea > a_end or eb > b_end:
                raise ValueError('Verification record past group boundary')
            data_a, data_b = original[pa + 24:ea], output[pb + 24:eb]
            if ha[:4] != b'SCPT' or _read_u32(ha, 12) != formid:
                if ha != hb or data_a != data_b:
                    raise ValueError('Unrelated record bytes changed')
            else:
                visited[0] += 1
                fields_a = list(_slots(_decode_record(ha, data_a)))
                fields_b = list(_slots(_decode_record(hb, data_b)))
                if len(fields_a) != len(fields_b):
                    raise ValueError('SCPT subrecord count changed')
                src_scda = _one(fields_a, b'SCDA')[1]
                dest_scda = _one(fields_b, b'SCDA')[1]
                position = src_scda.find(old)
                if position < 2 or src_scda.count(old) != 1:
                    raise ValueError('Readback cannot locate original SCDA literal')
                expected_scda = (src_scda[:position - 2] + _U16.pack(len(new)) + new
                                 + src_scda[position + len(old):])
                if dest_scda != expected_scda:
                    raise ValueError('SCDA readback includes unrelated byte changes')
                for (fa, hfa, va), (fb, hfb, vb) in zip(fields_a, fields_b):
                    if fa != fb:
                        raise ValueError('SCPT subrecord order changed')
                    if fa == b'SCHR':
                        expected = bytearray(va)
                        _U32.pack_into(expected, 8, len(dest_scda))
                        if vb != bytes(expected):
                            raise ValueError('SCHR readback mismatch')
                    elif fa == b'SCDA':
                        if vb != expected_scda:
                            raise ValueError('SCDA readback mismatch')
                    elif fa == b'SCTX':
                        if va.count(old) != 1 or vb != va.replace(old, new, 1):
                            raise ValueError('SCTX readback mismatch')
                    elif hfa + va != hfb + vb:
                        raise ValueError('Unexpected SCPT subrecord change')
                    if fa in (b'SCHR', b'SCDA', b'SCTX'):
                        if len(hfa) != len(hfb) or (hfa[:4] != hfb[:4]) or (
                                len(hfa) == 16 and hfa[:6] + hfa[10:] != hfb[:6] + hfb[10:]):
                            raise ValueError('SCPT changed subrecord framing')
                        if len(hfb) == 6 and _U16.unpack_from(hfb, 4)[0] != len(vb):
                            raise ValueError('SCPT changed subrecord length mismatch')
                        if len(hfb) == 16 and _read_u32(hfb, 6) != len(vb):
                            raise ValueError('SCPT extended size mismatch')
                if _read_u32(_one(fields_b, b'SCHR')[1], 8) != len(dest_scda):
                    raise ValueError('SCHR and SCDA length mismatch after readback')
            pa, pb = ea, eb
        if pa != a_end or pb != b_end:
            raise ValueError('TES4 structural traversal lengths differ')

    compare(0, len(original), 0, len(output), 0)
    if visited[0] != 1:
        raise ValueError(f'Expected exactly one target SCPT, verified {visited[0]}')


def translate_compiled_scpt(source: Path, target: Path, spec: dict) -> dict:
    """Write/verify one SCPT translation in a separate, new ESP.

    A previously translated source can be upgraded when its SHA is approved in
    ``spec['expected_sha256']``; optionally list exact reviewed old translations
    in ``spec['previous_script_literals']``.  Repeated current translation is
    idempotent.  No operation writes the source or any installed MO2 directory.
    """
    source, target = Path(source).resolve(), Path(target).resolve()
    reviewed = {case['editor_id']: case for case in _REVIEWED_CASES}.get(
        spec.get('editor_id'))
    if reviewed is None or any(
            spec.get(key) != reviewed[key] for key in
            ('record_formid', 'record_owner', 'editor_id', 'target',
             'source_en', 'filename')):
        raise ValueError('Compiled script spec differs from reviewed source identity')
    if source == target or source.suffix.lower() != '.esp' or target.suffix.lower() != '.esp':
        raise ValueError('Source and separate target must be distinct .esp paths')
    if target.exists():
        raise FileExistsError(target)
    installed_mods = Path(r'C:\Modlists\NuclearSunset\mods').resolve()
    if target.is_relative_to(installed_mods):
        raise ValueError('Refusing output into installed Nuclear Sunset MO2 mods')
    approved = spec.get('expected_sha256')
    if not isinstance(approved, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', approved):
        raise ValueError('Explicit expected_sha256 is required')
    translated = _CASE_LITERALS.get(spec.get('editor_id'))
    _validate_format(spec, translated)
    original = source.read_bytes()
    source_sha = hashlib.sha256(original).hexdigest()
    if source_sha != approved.lower():
        raise ValueError(f'Unapproved source SHA-256: {source_sha}; expected {approved}')
    owners = _masters(original) + [source.name]
    formid = spec['record_formid']
    index = formid >> 24
    if index >= len(owners) or owners[index].casefold() != spec['record_owner'].casefold():
        raise ValueError('SCPT record owner differs from approved master list')
    hits, found = [0], []

    def edit(header: bytes, raw: bytes) -> bytes:
        if header[:4] != b'SCPT' or _read_u32(header, 12) != formid:
            return raw
        hits[0] += 1
        if hits[0] != 1:
            raise ValueError('Repeated matching SCPT formid')
        changed, old, new = _change_script(_decode_record(header, raw), spec)
        found.append((old, new))
        if changed == _decode_record(header, raw):
            return raw
        return _encode_record(header, changed)

    written = _walk(original, edit)
    if hits[0] != 1:
        raise ValueError(f'Expected one SCPT formid {formid:08X}, found {hits[0]}')
    old, new = found[0]
    _verify_output(original, written, formid, old, new)
    if source.read_bytes() != original:
        raise ValueError('Source ESP changed while building verified output')
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open('xb') as stream:
            stream.write(written)
        if target.read_bytes() != written:
            raise ValueError('Disk write readback differs from validated ESP')
        _verify_output(original, target.read_bytes(), formid, old, new)
    except Exception:
        if target.is_file():
            target.unlink()
        raise
    return {'status': 'already_translated' if old == new else 'translated',
            'editor_id': spec['editor_id'], 'formid': f'{formid:08X}',
            'source_sha256': source_sha,
            'output_sha256': hashlib.sha256(written).hexdigest(),
            'old_string_bytes': len(old), 'new_string_bytes': len(new),
            'encoding': 'utf-8', 'runtime_validation': 'not_run'}
