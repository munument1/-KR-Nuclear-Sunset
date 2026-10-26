"""Audited notification literals and CP949 composition inputs.

Only reviewed string operands change. Compiled byte budgets, instructions,
condition data, numeric effects and control flow remain byte-identical.
Oversized translations are reported and retain their existing dictionary path.
"""
from pathlib import Path
import re,struct
from nskr_compiled_scpt import _walk,_slots,_decode_record,_encode_record,_with_payload
from nskr_perk_display import display_bytes,HANGUL

QUOTED=re.compile(rb'"([^"\r\n]*)"')
SINK=re.compile(rb'^\s*(?:\w+\.)?(?:SetFormDescription|MessageBoxExAlt|MessageBoxEx|MessageEx|MessageBox|Message|DebugNotification|ShowNotification)\b',re.I)
ARGS=re.compile(r'%%|%[{}]|%[-+ #0]*\d*(?:\.\d+)?(?:pp|[A-Za-z])')
IDENTIFIER_ARGUMENT=re.compile(
    rb'\b(?:GetPluginVersion|IsModLoaded|GetModIndex|GetFormFromMod|GFFM|EditorIDToFormID|'
    rb'CompileScript|RunScript|ReadFromJSON|WriteToJSON|SetEventHandler|RemoveEventHandler|'
    rb'GetINIFloat_Cached|GetINIString_Cached)\s*\(?\s*"([^"\r\n]*)"',re.I)
PLUGIN_IDENTIFIER_REPAIRS={'ShowOffNVSE 플러그인':'ShowOffNVSE Plugin',
                           'UI Organizer 플러그인':'UI Organizer Plugin'}

def protected_literal(line,match):
    return any(m.span(1)==match.span(1) for m in IDENTIFIER_ARGUMENT.finditer(line))

def repair_plugin_identifiers(raw):
    """Restore the two exact identifiers emitted by the earlier notification pass."""
    changes=[]
    def repair(match):
        value=match[1]
        for corrupted,original in PLUGIN_IDENTIFIER_REPAIRS.items():
            if value in (corrupted.encode('utf-8'),corrupted.encode('cp949')):
                changes.append({'kind':'plugin_identifier_restored','source':corrupted,'translation':original})
                start,end=match.span(1);offset=match.start()
                return match[0][:start-offset]+original.encode('ascii')+match[0][end-offset:]
        return match[0]
    return IDENTIFIER_ARGUMENT.sub(repair,raw),changes
def args(text):return [x for x in ARGS.findall(text) if x not in ('%%','%r','%R','%q','%Q','%e','%E')]

def compiled_edit(code,old,new):
    """Return same-size SCDA and a ledger of exact operand replacements."""
    transforms=[lambda s:s,lambda s:s.replace('%r','\n').replace('%R','\n'),
                lambda s:s.replace('%q','"').replace('%Q','"'),
                lambda s:s.replace('%r','\n').replace('%R','\n').replace('%q','"').replace('%Q','"')]
    for transform in transforms:
        literal=transform(old).encode('utf-8')
        target=display_bytes(transform(new).encode('utf-8'))
        found=[];pos=0
        while True:
            pos=code.find(literal,pos)
            if pos<0:break
            if pos>=2 and struct.unpack_from('<H',code,pos-2)[0]==len(literal):found.append(pos)
            pos+=max(1,len(literal))
        if not found:continue
        if len(target)>len(literal):return code,[],'over_budget'
        padded=target+b' '*(len(literal)-len(target))
        edited=bytearray(code);ledger=[]
        for at in found:
            edited[at:at+len(literal)]=padded
            ledger.append((at,literal,padded))
        if bytes(edited)==code:return code,[],'already'
        restored=bytearray(edited)
        for at,before,after in ledger:restored[at:at+len(before)]=before
        if bytes(restored)!=code:raise ValueError('Notification operand invariant failed')
        return bytes(edited),ledger,'changed'
    # A prior pass keeps UTF-8 source and CP949 compiled text.
    for transform in transforms:
        target=display_bytes(transform(new).encode('utf-8'))
        pos=code.find(target)
        if pos>=2:
            budget=struct.unpack_from('<H',code,pos-2)[0]
            if (budget>=len(target) and pos+budget<=len(code)
                    and code[pos+len(target):pos+budget]==b' '*(budget-len(target))):
                return code,[],'already'
    return code,[],'compiled_literal_not_found'

def script_edit(source,code,mappings,*,preserve_utf8_literals=()):
    by_source={row['old']:row['new'] for row in mappings}
    edits=[];changes=[];issues=[];initial_code=code;ledger=[]
    offset=0
    for line in source.splitlines(keepends=True):
        if SINK.match(line) or (not line.lstrip().startswith((b';',b'//'))
                               and any(b'"'+s.encode()+b'"' in line for s in by_source)):
            for match in QUOTED.finditer(line):
                if protected_literal(line,match):continue
                raw=match[1]
                try:old=raw.decode('utf-8')
                except UnicodeDecodeError:continue
                if old in preserve_utf8_literals:continue
                new=by_source.get(old,old if HANGUL.search(old) else None)
                if new is None:continue
                if args(old)!=args(new):raise ValueError('Notification format arguments changed')
                if old.count('|')!=new.count('|') or old.count('^')!=new.count('^'):
                    raise ValueError('Notification choice structure changed')
                try:code,changed,status=compiled_edit(code,old,new)
                except UnicodeEncodeError:status='unsupported_cp949';changed=[]
                if status=='changed':
                    edits.append((offset+match.start(1),offset+match.end(1),new.encode()))
                    changes.append({'kind':'notification_literal','source':old,'translation':new})
                    ledger.extend(changed)
                elif status=='already' and new!=old:
                    edits.append((offset+match.start(1),offset+match.end(1),new.encode()))
                    changes.append({'kind':'notification_source_sync','source':old,'translation':new})
                elif status not in ('already',):issues.append({'source':old,'reason':status})
        offset+=len(line)
    result=bytearray();pos=0
    for start,end,new in edits:
        result.extend(source[pos:start]);result.extend(new);pos=end
    result.extend(source[pos:])
    result=bytes(result)
    if QUOTED.sub(b'""',result)!=QUOTED.sub(b'""',source):
        raise ValueError('Notification source commands changed')
    restored=bytearray(code)
    for at,before,after in reversed(ledger):restored[at:at+len(before)]=before
    if bytes(restored)!=initial_code:raise ValueError('Notification bytecode changed outside literals')
    return result,code,changes,issues

def patch_bytes(original,filename,plan):
    changes=[];issues=[]
    relevant={}
    for row in plan:
        if Path(row['file']).name.casefold()==filename.casefold() and row['signature']=='SCPT':
            relevant.setdefault(row['edid'],[]).append(row)
    static={(row['edid'],row.get('field')):row for row in plan
            if Path(row['file']).name.casefold()==filename.casefold() and row['signature']=='MESG'}
    def visit(header,payload):
        sig=header[:4]
        if sig not in {b'SCPT',b'MESG',b'MGEF',b'ALCH',b'SPEL',b'BOOK'}:return payload
        data=_decode_record(header,payload);slots=list(_slots(data))
        edid=next((v.rstrip(b'\0').decode('ascii','replace') for k,h,v in slots if k==b'EDID'),'')
        replacements={}
        if sig==b'SCPT':
            indices={k:i for i,(k,h,v) in enumerate(slots)}
            if b'SCTX' not in indices or b'SCDA' not in indices:return payload
            source,code=slots[indices[b'SCTX']][2],slots[indices[b'SCDA']][2]
            # A small reviewed set consumes raw UTF-8 actor/location names.
            # Do not undo its consumer-specific encoding on regeneration.
            from nskr_dynamic_display import PLAN as DYNAMIC_PLAN
            preserve=[new for old,new in DYNAMIC_PLAN.get((filename.casefold(),edid),())]
            from nskr_runtime_override_data import COMPILED as OVERRIDES
            preserve.extend(new for old,new,encoding in
                            OVERRIDES.get((filename.casefold(),edid),()) if encoding=='utf-8')
            out_source,out_code,records,errors=script_edit(source,code,relevant.get(edid,[]),
                                                         preserve_utf8_literals=preserve)
            changes.extend({**x,'edid':edid} for x in records)
            issues.extend({**x,'edid':edid} for x in errors)
            if out_code!=code or out_source!=source:
                assert len(out_code)==len(code)
                replacements[indices[b'SCTX']]=out_source;replacements[indices[b'SCDA']]=out_code
        else:
            for i,(key,h,value) in enumerate(slots):
                if ((sig==b'MESG' and key in {b'DESC',b'ITXT'})
                        or (sig in {b'MGEF',b'ALCH',b'SPEL',b'BOOK'} and key==b'FULL')):
                    replacement=static.get((edid,key.decode()))
                    if replacement and value.rstrip(b'\0').decode('utf-8','replace')==replacement['old']:
                        converted=display_bytes(replacement['new'].encode('utf-8'))+b'\0'
                    else:
                        try:converted=display_bytes(value)
                        except UnicodeEncodeError:
                            issues.append({'edid':edid,'reason':'unsupported_cp949','field':key.decode()});continue
                    if converted!=value:
                        replacements[i]=converted
                        changes.append({'edid':edid,'kind':sig.decode()+'/'+key.decode()+' CP949'})
        if not replacements:return payload
        out=b''.join(_with_payload(h,replacements.get(i,v)) for i,(k,h,v) in enumerate(slots))
        parsed=list(_slots(out))
        restored=b''.join(_with_payload(h,slots[i][2] if i in replacements else v) for i,(k,h,v) in enumerate(parsed))
        if restored!=data:raise ValueError('Notification record invariant failed')
        return _encode_record(header,out)
    return _walk(original,visit),changes,issues

def loose_edit(raw,mappings):
    raw,changes=repair_plugin_identifiers(raw)
    lookup={row['old']:row['new'] for row in mappings}
    result=[]
    for line in raw.splitlines(keepends=True):
        if SINK.match(line):
            def convert(match):
                if protected_literal(line,match):return match[0]
                value=match[1]
                try:old=value.decode('utf-8')
                except UnicodeDecodeError:return match[0]
                new=lookup.get(old)
                if new is not None:
                    if args(old)!=args(new):raise ValueError('Loose notification arguments changed')
                    if old.count('|')!=new.count('|') or old.count('^')!=new.count('^'):
                        raise ValueError('Loose notification choices changed')
                    encoded=new.encode('cp949')
                    if encoded!=value:
                        changes.append({'kind':'loose_notification','source':old,'translation':new})
                        return b'"'+encoded+b'"'
                try:converted=display_bytes(value)
                except UnicodeEncodeError:return match[0]
                if converted!=value:
                    changes.append({'kind':'loose_display_CP949','source':value.decode('utf-8')})
                    return b'"'+converted+b'"'
                return match[0]
            line=QUOTED.sub(convert,line)
        result.append(line)
    return b''.join(result),changes


def ini_edit(raw,filename,translations):
    """Only display values in three reviewed localization INIs may change."""
    sections={'lang_en.ini':{'Messages','Tutorial','Perks'},
              'EnhancedMovement_Translations.ini':{'Translations'},
              'TNW_Translations.ini':{'Translations'}}
    if filename not in sections:return raw,[]
    out=[];changes=[];section=''
    for line in raw.splitlines(keepends=True):
        stripped=line.strip()
        if stripped.startswith(b'[') and stripped.endswith(b']'):
            section=stripped[1:-1].decode('ascii')
        if section in sections[filename] and b'=' in line and not line.lstrip().startswith((b';',b'#')):
            prefix,value=line.split(b'=',1)
            ending=value[len(value.rstrip(b'\r\n')):];value=value.rstrip(b'\r\n')
            try:old=value.decode('utf-8')
            except UnicodeDecodeError:out.append(line);continue
            new=translations.get(old,old)
            if args(old)!=args(new):raise ValueError('INI format arguments changed')
            if old.count('|')!=new.count('|') or old.count('^')!=new.count('^'):
                raise ValueError('INI choice structure changed')
            encoded=display_bytes(new.encode('utf-8'))
            if encoded!=value:
                line=prefix+b'='+encoded+ending
                changes.append({'kind':'translation_ini_value','section':section,
                                'key':prefix.decode('ascii'),'source':old,'translation':new})
        out.append(line)
    return b''.join(out),changes


def normalize_loose_input(raw,provider,path):
    """Recover UTF-8 only from exact CP949 literals previously emitted here."""
    from nskr_notification_data import PLAN
    raw,_=repair_plugin_identifiers(raw)
    key=(provider+'/'+path.replace('\\','/')).casefold()
    for row in PLAN:
        if row['signature']=='loose' and row['file'].casefold()==key:
            new=row['new']
            raw=raw.replace(b'"'+new.encode('cp949')+b'"',b'"'+new.encode('utf-8')+b'"')
    raw.decode('utf-8')
    return raw


def finalize(stage,files):
    """Finalize existing output artifacts with the bundled reviewed operands."""
    from nskr_notification_data import PLAN,INI_TRANSLATIONS
    import nskr
    for row in files:
        target=nskr.contained(stage,row['output_path']);raw=target.read_bytes()
        if target.suffix.casefold() in ('.esm','.esp'):
            output,changes,issues=patch_bytes(raw,target.name,PLAN)
            if issues:row['notification_review_notes']=issues
        elif target.name.casefold()=='tnvse.ini':
            import nskr_skill_display
            if row.get('provider') not in nskr_skill_display.PROVIDERS:continue
            output=nskr_skill_display.patch_config(raw)
            changes=[{'kind':'JIP Big Guns Korean runtime description'}] if output!=raw else []
        elif target.name in {'lang_en.ini','EnhancedMovement_Translations.ini','TNW_Translations.ini'}:
            output,changes=ini_edit(raw,target.name,INI_TRANSLATIONS)
        else:
            key=(row.get('provider','')+'/'+row.get('path','')).replace('\\','/').casefold()
            mappings=[x for x in PLAN if x['signature']=='loose' and x['file'].casefold()==key]
            output,changes=loose_edit(raw,mappings) if target.suffix.casefold() in ('.txt','.gek') else (raw,[])
        if changes:
            target.write_bytes(output);row['notification_display']=changes
            row['output_sha256']=nskr.sha256(target)
            row['status']+='; notification_literals_verified'


def add_outputs(installation,stage,files):
    """Include enabled reviewed loose providers absent from the older catalog."""
    from nskr_notification_data import PLAN
    import nskr
    known={row['output_path'].casefold() for row in files}
    paths={x['file'] for x in PLAN if x['signature']=='loose'}
    paths.add('WordleHack/config/WordleHack/lang_en.ini')
    for path in sorted(paths):
        provider,relative=path.split('/',1)
        if provider not in installation.mods_enabled:continue
        source=nskr.contained(installation.mods,path)
        output_path='mods/'+path
        if not source.is_file() or output_path.casefold() in known:continue
        target=nskr.contained(stage,output_path)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
        files.append({'path':relative,'provider':provider,'output_path':output_path,
                      'source_sha256':nskr.sha256(source),'output_sha256':nskr.sha256(target),
                      'status':'reviewed_notification_source_copy','translated':0,'unmatched':0})
        known.add(output_path.casefold())
