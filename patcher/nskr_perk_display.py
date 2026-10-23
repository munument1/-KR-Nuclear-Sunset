"""Keep composed Korean perk text in CP949; verify all other bytes unchanged.

The font hook detects UTF-8 on a whole string. A perk description can be
composed with already converted requirement labels, so UTF-8 DESC payloads
must be normalized before that composition. Requirement GMST labels, AVIF
skill/attribute names and prerequisite PERK names use the same encoding.
Compiled SetFormDescription
operands use the same encoding; their byte budgets and opcodes never change.
SCTX remains UTF-8 source text with the same Unicode meaning as SCDA.
"""
from __future__ import annotations
import re
import struct
from pathlib import Path
from nskr_compiled_scpt import _walk, _slots, _decode_record, _encode_record, _with_payload

HANGUL = re.compile('[\uac00-\ud7a3]')
DESCRIPTION = re.compile(rb'\bSetFormDescription\s+(\w+)\s+"([^"\r\n]*)"', re.I)
REPLACEMENTS = {
    ('new blood.esp', 'SCPTNewBloodStartup', 'PiercingStrike'):
        ('%z Bleeding effects that you afflict to enemies will also be the maximum severity.',
         '%z 적에게 가하는 출혈 효과도 항상 최대 강도로 적용됩니다.'),
    ('ns.esp', 'SCPTPatchForJBT', 'sssPerkCoiledSnake'):
        ("You're extra dangerous when cornered or unseen. You gain +15%% throwing velocity and attack speed with thrown melee weapons while crouched, as well as +25%% movement speed and +15%% attack speed while prone.",
         '몰리거나 들키지 않았을 때 더 위험합니다. 웅크리면 투척 근접 무기의 투척 속도와 공격 속도 +15%%. 엎드리면 이동 속도 +25%%, 공격 속도 +15%%.'),
    ('s6s base game perks redux.esp', 'SCPTOnRestartBasePerks', 'CarefulHandling'):
        ('Your weapons deserve respect, and you know it. Your weapon AP cost, equip, reload, and attack speed are penalized by 5%%, but your spread and crit. chance are improved by 5%%, and your weapon condition decays 15%% slower, and your weapons are 20%% less likely to jam.',
         '무기를 소중히 다룹니다. 무기 AP 소모량과 장비·재장전·공격 속도에 5%%의 불이익을 받습니다. 탄 퍼짐과 치명타 확률은 5%% 개선되며, 내구도 감소 속도 -15%%, 작동 불량 확률 -20%%.'),
    ('s6s base game perks redux.esp', 'SCPTOnRestartBasePerks', 'GoodNatured'):
        ("You're Good Natured at heart, more prone to solving problems with your mind than violence. Your karma is immediately increased to Good if it is below that threshold, and you gain +1 to Charisma and +5 to Barter and Speech, but have -5 to Energy Weapons, Explosives, Guns, Big Guns, Melee Weapons, and Unarmed.",
         '폭력보다 지혜로 문제를 해결하는 선한 성품입니다. 카르마가 선함 미만이면 즉시 선함이 됩니다. 매력 +1, 흥정·화술 +5. 에너지 무기·폭발물·총기·중화기·근접 무기·격투 -5.'),
}
SCRIPT_PLUGINS = {'new blood.esp', 'ns.esp', 's6s base game perks redux.esp',
                  'sweet consumables.esp', 's6s perks.esp'}
CONCENTRATED_FIRE = {
    'falloutnv.esm': (
        'With Concentrated Fire, your accuracy to hit any body part in V.A.T.S. increases slightly with each subsequent hit on that body part.',
        '집중 사격 특성을 선택하면 V.A.T.S.에서 같은 신체 부위를 연속으로 공격할 때마다 명중률이 조금씩 증가합니다.'),
    's6s base game perks redux.esp': (
        'With Concentrated Fire, your accuracy when targeting any body part in V.A.T.S. increases slightly with each subsequent attack on that body part, and your spread is decreased by 20% when using an automatic weapon.',
        '집중 사격 특성을 선택하면 V.A.T.S.에서 같은 신체 부위를 연속으로 공격할 때마다 명중률이 조금씩 증가하며, 자동 무기의 탄 퍼짐이 20% 감소합니다.'),
}
TOKENS = re.compile(r'%%|%[0-9.]*[a-zA-Z]')
REQUIREMENT_GMSTS = {
    'srequirementstext', 'srankstext', 'slevelabbrev',
    'smenudisplaylevelstring', 'sinventorystrreq',
}

def display_bytes(raw: bytes):
    """Return lossless CP949 only for strictly valid Korean UTF-8 text."""
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw
    if not HANGUL.search(text):
        return raw
    # CP949 has HORIZONTAL BAR but not EM DASH. Two reviewed Elysium
    # descriptions use the latter; preserve the visible dash, never '?' it.
    text = text.replace('\u2014','\u2015')
    # Fail rather than replacing unsupported characters with question marks.
    encoded = text.encode('cp949')
    if encoded.decode('cp949') != text:
        raise ValueError('Non-roundtripping Korean perk text')
    return encoded

def patch_bytes(original: bytes, filename: str):
    changes = []
    filename = filename.casefold()
    def visit(header, payload):
        sig = header[:4]
        if sig not in {b'PERK', b'AVIF', b'GMST'} and not (sig == b'SCPT' and filename in SCRIPT_PLUGINS):
            return payload
        data = _decode_record(header, payload)
        slots = list(_slots(data))
        edid = next((v.rstrip(b'\0').decode('ascii') for k,h,v in slots if k == b'EDID'), '')
        replacements = {}
        if sig in {b'PERK', b'AVIF', b'GMST'}:
            for i,(key,h,value) in enumerate(slots):
                text_field = (
                    (sig == b'PERK' and key in {b'DESC', b'FULL'})
                    or (sig == b'AVIF' and key == b'FULL')
                    or (sig == b'GMST' and key == b'DATA'
                        and edid.casefold() in REQUIREMENT_GMSTS))
                if text_field:
                    restore = CONCENTRATED_FIRE.get(filename)
                    if (key == b'DESC' and restore and edid == 'ConcentratedFire'
                            and struct.unpack_from('<I',header,12)[0] & 0xFFFFFF == 0x044CAF
                            and value.rstrip(b'\0') == restore[0].encode('ascii')):
                        encoded = restore[1].encode('cp949') + b'\0'
                    else:
                        encoded = display_bytes(value)
                    if encoded != value:
                        replacements[i] = encoded
                        changes.append({'kind':sig.decode()+'/'+key.decode()+' CP949', 'edid':edid})
        else:
            indices = {k:i for i,(k,h,v) in enumerate(slots)}
            if b'SCTX' not in indices or b'SCDA' not in indices:
                return payload
            source = slots[indices[b'SCTX']][2]
            code = slots[indices[b'SCDA']][2]
            original_code = code
            for match in DESCRIPTION.finditer(source):
                form = match[1].decode('ascii')
                literal = match[2]
                spec = REPLACEMENTS.get((filename,edid,form))
                if spec:
                    old, new = spec
                    if TOKENS.findall(old) != TOKENS.findall(new):
                        raise ValueError('Perk format argument mismatch')
                    if literal.decode('utf-8') not in (old,new):
                        raise ValueError('Reviewed perk source changed: '+edid+'/'+form)
                    logical = new.encode('utf-8')
                else:
                    logical = literal
                encoded = display_bytes(logical)
                if encoded == literal:
                    continue
                if code.count(literal) != 1:
                    # A previous run retains UTF-8 SCTX and stores CP949 SCDA.
                    if code.count(encoded) == 1:
                        at = code.index(encoded)
                        budget = struct.unpack_from('<H',code,at-2)[0] if at >= 2 else 0
                        if (budget >= len(encoded) and at+budget <= len(code)
                                and code[at+len(encoded):at+budget] == b' '*(budget-len(encoded))):
                            continue
                    raise ValueError('Compiled perk literal is not unique: '+edid+'/'+form)
                if len(encoded) > len(literal):
                    raise ValueError('Compiled perk literal exceeds original byte budget')
                padded = encoded + b' ' * (len(literal)-len(encoded))
                offset = code.index(literal)
                if offset < 2 or struct.unpack_from('<H',code,offset-2)[0] != len(literal):
                    raise ValueError('Compiled perk literal size prefix mismatch')
                code = code[:offset] + padded + code[offset+len(literal):]
                if spec:
                    source = source.replace(literal,logical,1)
                changes.append({'kind':'SCPT literal CP949', 'edid':edid,'form':form,
                                'byte_budget':len(literal)})
            if code != original_code:
                assert len(code) == len(original_code)
                replacements[indices[b'SCDA']] = code
                replacements[indices[b'SCTX']] = source
        if not replacements:
            return payload
        out = b''.join(_with_payload(h,replacements.get(i,v)) for i,(k,h,v) in enumerate(slots))
        # Independently restore each edited subrecord and compare the full body.
        readback = list(_slots(out))
        restored = b''.join(_with_payload(h,slots[i][2] if i in replacements else v)
                            for i,(k,h,v) in enumerate(readback))
        if restored != data:
            raise ValueError('Perk edit touched unapproved record bytes')
        return _encode_record(header,out)
    return _walk(original,visit), changes

def patch_file(source: Path, target: Path):
    if source.resolve() == target.resolve() or target.exists():
        raise ValueError('A separate new output is required')
    original = source.read_bytes()
    out,changes = patch_bytes(original,source.name)
    if source.read_bytes() != original:
        raise ValueError('Perk source changed while staging')
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f: f.write(out)
    if target.read_bytes() != out:
        raise ValueError('Perk output readback failed')
    return changes
