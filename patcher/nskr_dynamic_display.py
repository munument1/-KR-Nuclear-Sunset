"""Reviewed UTF-8 message consumers of raw UTF-8 actor/location names.

Only exact quoted operands are rewritten, inside their original byte budgets.
The command stream, operand lengths, branches and all non-literal bytes stay.
Reviewed whole-script hashes gate every accepted input variant.
"""
import hashlib
from pathlib import Path
import re
import struct

from nskr_compiled_scpt import _walk, _slots, _decode_record, _encode_record, _with_payload
from nskr_notifications import args, QUOTED

PLAYER = ('당신: ', '나: ')
MEDKIT = ('%z메드킷이 필요하지 않습니다.', '%z치료 불필요.')
SPLINT = ('%z부목이 필요하지 않습니다.', '%z부목 불필요.')
HEMOSTATIC = ('%z의 사지 피해와 회복량이 %.0f%%로 감소.',
              '%z의 사지 피해와 회복량이 %.0f%%로 감소.')
STIM = ('전투용 스팀팩과 울트라 스팀팩 병용으로 %z의 체력과 가슴이 손상됐습니다!',
        '전투용·울트라 스팀팩 병용: %z의 체력·흉부 손상!')
RECALL = ('%n: %pp 원래 위치 %z로 귀환.', '%n: %pp 원래 위치 %z로 귀환.')
PLAN = {
    ('aid addon.esp', 'SCPTOnUseAidAddonMedkit'): (PLAYER, MEDKIT),
    ('aid addon.esp', 'SCPTSplintMenuUDF'): (PLAYER, SPLINT),
    ('aid addon.esp', 'SCPTOnUseAidAddonHemostatic'): (HEMOSTATIC,),
    ('aid addon.esp', 'SCPTOnUseAidAddonCombatStim'): (STIM,),
    ('aid addon.esp', 'SCPTOnUseAidAddonCombatStimUltra'): (STIM,),
    ('jip companions command & control.esp', 'JIPCCCMainScript'): (RECALL,),
}


def digest(source, code):
    return hashlib.sha256(source).hexdigest(), hashlib.sha256(code).hexdigest()


def script_edit(source, code, mappings, *, encoding='utf-8'):
    initial_source, initial_code = source, code
    ledger = []
    changes = []
    for old, new in mappings:
        if args(old) != args(new) or old.count('|') != new.count('|') or old.count('^') != new.count('^'):
            raise ValueError('Dynamic message arguments/choices changed')
        literals = [m[1] for m in QUOTED.finditer(source)]
        old_raw, new_source = old.encode('utf-8'), new.encode('utf-8')
        new_raw = new.encode(encoding)
        active = old if old_raw in literals else new if new_source in literals else None
        if active is None:
            return initial_source, initial_code, [], 'source_literal_not_found'
        expected = literals.count(active.encode('utf-8'))
        variants = {active.encode('utf-8'), active.encode('cp949')}
        positions = {}
        for literal in variants:
            start = 0
            while True:
                at = code.find(literal, start)
                if at < 0:
                    break
                start = at + 1
                if at < 2:
                    continue
                budget = struct.unpack_from('<H', code, at-2)[0]
                if (budget >= len(literal) and at+budget <= len(code)
                        and code[at+len(literal):at+budget] == b' '*(budget-len(literal))):
                    positions[at] = budget
        if len(positions) != expected:
            return initial_source, initial_code, [], 'compiled_literal_count_mismatch'
        if any(len(new_raw) > budget for budget in positions.values()):
            return initial_source, initial_code, [], 'over_budget'
        for at, budget in sorted(positions.items()):
            before = code[at:at+budget]
            after = new_raw + b' '*(budget-len(new_raw))
            if before != after:
                code = code[:at] + after + code[at+budget:]
                ledger.append((at, before))
                changes.append({'source':active, 'translation':new, 'offset':at,
                                'byte_budget':budget, 'to_encoding':encoding})
        if active != new:
            source = source.replace(b'"'+active.encode('utf-8')+b'"', b'"'+new_source+b'"')
    restored = bytearray(code)
    for at, before in reversed(ledger):
        restored[at:at+len(before)] = before
    if bytes(restored) != initial_code or len(code) != len(initial_code):
        raise ValueError('Dynamic message changed non-literal bytecode')
    if QUOTED.sub(b'""',source) != QUOTED.sub(b'""',initial_source):
        raise ValueError('Dynamic message source commands changed')
    return source, code, changes, None


def patch_bytes(raw, filename, reviewed=None):
    if reviewed is None:
        from nskr_dynamic_variants import REVIEWED
        reviewed = REVIEWED
    changes, issues = [], []
    def visit(header, payload):
        if header[:4] != b'SCPT':
            return payload
        data = _decode_record(header,payload)
        slots = list(_slots(data))
        edid = next((v.rstrip(b'\0').decode('ascii') for k,h,v in slots if k==b'EDID'),'')
        key = (filename.casefold(),edid)
        if key not in PLAN:
            return payload
        indices = {k:i for i,(k,h,v) in enumerate(slots)}
        if b'SCTX' not in indices or b'SCDA' not in indices:
            issues.append({'edid':edid,'reason':'missing_source_or_bytecode'})
            return payload
        source,code = (slots[indices[k]][2] for k in (b'SCTX',b'SCDA'))
        allowed = reviewed.get(filename.casefold()+'/'+edid,[])
        if list(digest(source,code)) not in allowed:
            issues.append({'edid':edid,'reason':'unreviewed_dynamic_script_hash'})
            return payload
        out_source,out_code,edits,error = script_edit(source,code,PLAN[key])
        if error:
            issues.append({'edid':edid,'reason':error})
            return payload
        if out_source==source and out_code==code:
            return payload
        changes.extend({'signature':'SCPT','field':'SCDA/SCTX','edid':edid,**edit} for edit in edits)
        replacements = {indices[b'SCTX']:out_source,indices[b'SCDA']:out_code}
        output = b''.join(_with_payload(h,replacements.get(i,v)) for i,(k,h,v) in enumerate(slots))
        return _encode_record(header,output)
    return _walk(raw,visit),changes,issues


def finalize(stage,files):
    import nskr
    names={key[0] for key in PLAN}
    for row in files:
        target=nskr.contained(stage,row['output_path'])
        if target.name.casefold() not in names:
            continue
        original=target.read_bytes()
        output,changes,issues=patch_bytes(original,target.name)
        if issues:
            row['dynamic_encoding_review_notes']=issues
        if changes:
            if target.read_bytes()!=original:
                raise ValueError('Dynamic source changed during finalization')
            target.write_bytes(output)
            if target.read_bytes()!=output:
                raise ValueError('Dynamic display readback failed')
            row['dynamic_display']=changes
            row['status']+='; UTF8_dynamic_name_messages_verified'
            row['output_sha256']=nskr.sha256(target)
