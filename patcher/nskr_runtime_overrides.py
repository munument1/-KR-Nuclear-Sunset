"""Reviewed direct display setters; compiled byte budgets and commands stay."""
import json,re
from pathlib import Path
from nskr_dynamic_display import script_edit,digest
from nskr_notifications import QUOTED,args
from nskr_runtime_override_data import COMPILED,LOOSE
from nskr_compiled_scpt import _walk,_slots,_decode_record,_encode_record,_with_payload

def compiled_script(source,code,plan):
    initial=(source,code);changes=[]
    for old,new,encoding in plan:
        source,code,edits,error=script_edit(source,code,[(old,new)],encoding=encoding)
        if error:return *initial,[],{'source':old,'reason':error}
        changes.extend(edits)
    return source,code,changes,None

def patch_bytes(raw,filename,reviewed=None):
    if reviewed is None:
        from nskr_override_variants import REVIEWED
        reviewed=REVIEWED
    changes=[];issues=[]
    def visit(h,payload):
        if h[:4]!=b'SCPT':return payload
        data=_decode_record(h,payload);slots=list(_slots(data))
        edid=next((v.rstrip(b'\0').decode('ascii') for k,sh,v in slots if k==b'EDID'),'')
        key=(filename.casefold(),edid)
        if key not in COMPILED:return payload
        indices={k:i for i,(k,sh,v) in enumerate(slots)}
        if b'SCTX' not in indices or b'SCDA' not in indices:
            issues.append({'edid':edid,'reason':'missing_script_parts'});return payload
        source,code=(slots[indices[k]][2] for k in (b'SCTX',b'SCDA'))
        if list(digest(source,code)) not in reviewed.get('/'.join(key),[]):
            issues.append({'edid':edid,'reason':'unreviewed_override_script_hash'});return payload
        out_source,out_code,edits,error=compiled_script(source,code,COMPILED[key])
        if error:issues.append({'edid':edid,**error});return payload
        if (out_source,out_code)==(source,code):return payload
        changes.extend({'edid':edid,**edit} for edit in edits)
        replacement={indices[b'SCTX']:out_source,indices[b'SCDA']:out_code}
        output=b''.join(_with_payload(sh,replacement.get(i,v)) for i,(k,sh,v) in enumerate(slots))
        return _encode_record(h,output)
    return _walk(raw,visit),changes,issues

def loose_edit(raw,provider,path):
    plan=next((plan for p,s,plan in LOOSE if p==provider and s.casefold()==path.casefold()),None)
    if plan is None:return raw,[],[]
    lines=raw.splitlines(keepends=True);changes=[];issues=[]
    ranks=provider=='Generic NPC Namer'
    for old,new,encoding in plan:
        if args(old)!=args(new):raise ValueError('Runtime setter arguments changed')
        target=new.encode(encoding);found=0
        for i,line in enumerate(lines):
            if line.lstrip().startswith((b';',b'//')):continue
            # Ignore quoted event IDs and editor-name search patterns.
            if not ranks and not re.search(rb'\b(?:LNSetName|SetNameEx|SetName)\s+"',line,re.I):continue
            def replace(m):
                nonlocal found
                if m[1] not in {old.encode(),new.encode(),new.encode(encoding)}:return m[0]
                found+=1
                if m[1]==target:return m[0]
                changes.append({'source':old,'translation':new,'encoding':encoding})
                return b'"'+target+b'"'
            if ranks:
                lines[i]=QUOTED.sub(replace,line)
            else:
                command=re.search(rb'\b(?:LNSetName|SetNameEx|SetName)\s+(".*?")',line,re.I)
                start,end=command.span(1)
                lines[i]=line[:start]+QUOTED.sub(replace,line[start:end])+line[end:]
        if not found:issues.append({'source':old,'reason':'reviewed_setter_not_found'})
    output=b''.join(lines)
    if QUOTED.sub(b'""',raw)!=QUOTED.sub(b'""',output):raise ValueError('Setter commands changed')
    return output,changes,issues

def finalize(installation,stage,files):
    import nskr
    known={row['output_path'].casefold():row for row in files}
    for provider,path,plan in LOOSE:
        if provider not in installation.mods_enabled:continue
        output_path='mods/'+provider+'/'+path
        target=nskr.contained(stage,output_path)
        row=known.get(output_path.casefold())
        if row is None:
            source=nskr.contained(installation.mods,provider+'/'+path)
            if not source.is_file():continue
            raw=source.read_bytes();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            row={'path':path,'provider':provider,'output_path':output_path,
                 'source_sha256':nskr.sha256(source),'output_sha256':nskr.sha256(target),
                 'status':'reviewed_display_setter_copy'}
            files.append(row);known[output_path.casefold()]=row
        raw=target.read_bytes();output,changes,issues=loose_edit(raw,provider,path)
        if issues:row['override_review_notes']=issues
        if changes:
            target.write_bytes(output);row['runtime_overrides']=changes
            row['output_sha256']=nskr.sha256(target)
    names={key[0] for key in COMPILED}
    for row in files:
        target=nskr.contained(stage,row['output_path'])
        if target.name.casefold() not in names:continue
        raw=target.read_bytes();output,changes,issues=patch_bytes(raw,target.name)
        if issues:row['override_review_notes']=issues
        if changes:
            target.write_bytes(output);row['runtime_overrides']=changes
            row['output_sha256']=nskr.sha256(target)
