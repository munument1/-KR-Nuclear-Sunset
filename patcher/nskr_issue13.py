"""Translate reviewed runtime UI strings without relocating compiled bytecode.

UTF-8 literals fit inside the original byte budget; trailing ASCII spaces pad
the message body (before its buttons) or description. All compiled lengths,
instruction framing, branches, embedded lambdas and variable references remain
byte-identical. SCTX mirrors SCDA, including the compiler's %r -> LF conversion.
The complete source AND result SCDA/SCTX hashes are pinned per script.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
import struct

from nskr_compiled_scpt import (
    _walk, _slots, _one, _decode_record, _encode_record, _with_payload, _masters,
)
from nskr_issue13_data import SCRIPT_CASES, NAME_ENTRIES
from tools.loose_translation import TOKEN


def name_entries():
    return deepcopy(NAME_ENTRIES) + [{
        'kind': 'nvse-script', 'provider': 'Dynamic Scaling Level Stat Choice',
        'path': 'nvse/user_defined_functions/DSLC_LevelUp.gek',
        'script_transform': 'dslc_menu_literals', 'mappings': [],
        'encoding': 'utf-8', 'review_status': 'runtime_script_reviewed'}]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def merge_stat_menu(raw):
    """Only the reviewed .gek menu's four UI constants; no AV identifiers."""
    source_hash = '93e1cbc956aa39f6096d12b4d50aaca1712773e5832ae6cae9eaca9689f85236'
    translated_hash = '00d943bae0ef0456187b5072cdbbf170d303b92fb4fc5a701c49b363980e626b'
    actual = digest(raw)
    if actual == translated_hash:
        return raw, {'translated': 0, 'already_translated': 4, 'unmatched': 0}
    if actual != source_hash:
        raise ValueError('Unreviewed DSLC level-up function source')
    result = raw
    for old, new in (
            ('^Select a stat to increase^', '^올릴 능력치를 선택하세요^'),
            ('|Health', '|체력'), ('|Action Points', '|행동력'), ('|Carry Weight', '|휴대 중량')):
        before, after = ('"' + old + '"').encode(), ('"' + new + '"').encode()
        if result.count(before) != 1:
            raise ValueError('DSLC quoted UI operand is not unique')
        result = result.replace(before, after, 1)
    if digest(result) != translated_hash:
        raise ValueError('DSLC translated function hash mismatch')
    return result, {'translated': 4, 'already_translated': 0, 'unmatched': 0}


def validate_mapping(row):
    source, dest = row['source'], row['dest']
    if any(c in dest for c in ('"', '\\', '\0', '\r', '\n')):
        raise ValueError('Unsupported runtime literal characters')
    if Counter(TOKEN.findall(source)) != Counter(TOKEN.findall(dest)):
        raise ValueError('Runtime literal format tokens differ')
    if source.count('|') != dest.count('|') or source.count('^') != dest.count('^'):
        raise ValueError('Message title/button delimiters differ')
    old = source.replace('%r', '\n').encode('utf-8')
    new = dest.replace('%r', '\n').encode('utf-8')
    if len(old) != len(new):
        raise ValueError('Runtime literal exceeds its fixed compiled byte budget')
    return old, new


def _edit_record(data, case):
    fields = list(_slots(data))
    edid = _one(fields, b'EDID')[1].rstrip(b'\0').decode('ascii')
    if edid != case['edid']:
        raise ValueError('Issue #13 SCPT editor ID mismatch')
    scda, sctx = (_one(fields, key)[1] for key in (b'SCDA', b'SCTX'))
    schr = _one(fields, b'SCHR')[1]
    if len(schr) != 20 or struct.unpack_from('<I', schr, 8)[0] != len(scda):
        raise ValueError('Issue #13 SCHR/SCDA compiled-size mismatch')
    for row in case['mappings']:
        validate_mapping(row)
    source_hashes = case['scda_sha256'], case['sctx_sha256']
    result_hashes = case['translated_scda_sha256'], case['translated_sctx_sha256']
    actual = digest(scda), digest(sctx)
    from nskr_runtime_variants import is_reviewed_finalized
    if is_reviewed_finalized(edid,scda,sctx):
        return data,'already_translated'
    if actual == result_hashes:
        return data, 'already_translated'
    if actual != source_hashes:
        raise ValueError(f"Unreviewed issue #13 SCDA/SCTX: {case['edid']}")
    original_scda, original_sctx = scda, sctx
    spans = []
    for row in case['mappings']:
        old, new = validate_mapping(row)
        if scda.count(old) != 1 or sctx.count(row['source'].encode()) != 1:
            raise ValueError('Runtime literal is not unique in both SCDA and SCTX')
        offset = scda.index(old)
        if offset < 2 or struct.unpack_from('<H', scda, offset - 2)[0] != len(old):
            raise ValueError('Compiled literal uint16 length differs')
        spans.append((offset, offset + len(old)))
        scda = scda.replace(old, new, 1)
        sctx = sctx.replace(row['source'].encode(), row['dest'].encode(), 1)
    if (digest(scda), digest(sctx)) != result_hashes:
        raise ValueError('Translated issue #13 script hash mismatch')
    # Independently mask the literal bytes: every opcode, operand size, branch
    # and nested function framing byte outside those spans must be identical.
    before, after = bytearray(original_scda), bytearray(scda)
    for start, end in spans:
        before[start:end] = after[start:end] = bytes(end - start)
    if before != after or len(scda) != len(original_scda):
        raise ValueError('Compiled code changed outside approved literal bytes')
    substitutions = {b'SCDA': scda, b'SCTX': sctx}
    changed = b''.join(_with_payload(header, substitutions[key])
                       if key in substitutions else header + payload
                       for key, header, payload in fields)
    # Reverse only the approved string replacements and prove full recovery of
    # every original subrecord, including SCHR, SCRO, SLSD and local variables.
    restored = {b'SCDA': scda, b'SCTX': sctx}
    for row in reversed(case['mappings']):
        old, new = validate_mapping(row)
        restored[b'SCDA'] = restored[b'SCDA'].replace(new, old, 1)
        restored[b'SCTX'] = restored[b'SCTX'].replace(row['dest'].encode(), row['source'].encode(), 1)
    if restored != {b'SCDA': original_scda, b'SCTX': original_sctx}:
        raise ValueError('Runtime literal reverse verification failed')
    for (key, _, value), (other, _, updated) in zip(fields, _slots(changed)):
        if key != other or (key not in substitutions and value != updated):
            raise ValueError('Unexpected script metadata change')
    return changed, 'translated'


def translate_runtime_plugin(source: Path, target: Path):
    """Write a separate verified ESP; reject unknown/partially modified scripts."""
    source, target = Path(source).resolve(), Path(target).resolve()
    cases = [c for c in SCRIPT_CASES if c['plugin'].casefold() == source.name.casefold()]
    if not cases or source == target or target.suffix.casefold() != '.esp':
        raise ValueError('Expected a reviewed plugin and a separate ESP target')
    if target.exists():
        raise FileExistsError(target)
    # Callers stage outside MO2. Guard the common installation as a second check.
    if target.is_relative_to(Path(r'C:\Modlists\NuclearSunset').resolve()):
        raise ValueError('Runtime translation output must be outside the installation')
    original = source.read_bytes()
    owners = _masters(original) + [source.name]
    by_id = {c['formid']: c for c in cases}
    seen, statuses = set(), []

    def visit(header, raw):
        fid = struct.unpack_from('<I', header, 12)[0]
        if header[:4] != b'SCPT' or fid not in by_id:
            return raw
        case = by_id[fid]
        if fid in seen or fid >> 24 >= len(owners) or owners[fid >> 24].casefold() != case['owner']:
            raise ValueError('Duplicate runtime SCPT or unexpected master owner')
        seen.add(fid)
        data = _decode_record(header, raw)
        changed, status = _edit_record(data, case)
        statuses.append({'editor_id': case['edid'], 'status': status,
                         'literals': len(case['mappings'])})
        return raw if changed == data else _encode_record(header, changed)

    written = _walk(original, visit)
    if seen != set(by_id):
        raise ValueError('Expected issue #13 runtime script is missing')
    # A separate full traversal must see all targets already translated, and
    # must be byte-identical, including all unrelated records and GRUP framing.
    seen.clear()
    statuses_before_readback = statuses[:]
    statuses.clear()
    if _walk(written, visit) != written or seen != set(by_id) or any(
            r['status'] != 'already_translated' for r in statuses):
        raise ValueError('Issue #13 plugin readback/idempotence check failed')
    if source.read_bytes() != original:
        raise ValueError('Source plugin changed during translation')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(written)
    if target.read_bytes() != written:
        target.unlink()
        raise ValueError('Written runtime plugin differs from verified bytes')
    return {'scripts': statuses_before_readback, 'source_sha256': digest(original),
            'output_sha256': digest(written), 'runtime_validation': 'not_run',
            'translated': sum(r['literals'] for r in statuses_before_readback if r['status'] == 'translated'),
            'already_translated': sum(r['literals'] for r in statuses_before_readback
                                      if r['status'] == 'already_translated')}
