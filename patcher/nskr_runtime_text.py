"""Exact loose-script display literals that overwrite translated records/settings."""
from pathlib import Path
import re
from nskr_notifications import args, QUOTED

MIC='[ALT] - Misc Items and Crafting Tweaks'
FTE='Fast Travel Expenses'
CUSTOM='[#] [INF] - Fast Travel Expenses - Custom INI'
NAME_PATH='nvse/plugins/scripts/gr_p20MICingestiblenames.txt'
CLICK_PATH='nvse/user_defined_functions/Fast Travel Expenses/FastTravelExpenseClickHandler.gek'
START_PATH='nvse/plugins/scripts/gr_Fast Travel Expenses.txt'
INI_PATH='config/Fast Travel Expenses/Fast Travel Expenses.ini'
PATHS=((MIC,NAME_PATH),(FTE,CLICK_PATH),(FTE,START_PATH),(FTE,INI_PATH),(CUSTOM,INI_PATH))
MESSAGES={
    'sNoFastTravelMessage':('You cannot afford %g caps to fast travel','빠른 이동 비용 %g 캡이 부족합니다.'),
    'sFastTravelMessage':('Hire help for %g caps to travel to','안내인 고용료 %g 캡 / 이동할 장소:'),
    'sDogmeatMessage':('Have %n take you to','%n의 안내로 이동할 장소:'),
}
NAMES=(
    ('Apple','사과','Apple'),('Carrot','당근','Carrot'),
    ('Pear','배','Pear'),('Potato','감자','Potato'),
    ('Punga Fruit, Refined','잘 익은 펑가 열매','(EditorIDToFormID "DLC04PungaRefined")'),
    ('Punga Fruit','야생 펑가 열매','(EditorIDToFormID "DLC04PungaWild")'),
    ('Glowing Fungus','발광 버섯','(EditorIDToFormID "TTWGlowingMushroom")'),
)


def script_rules(path):
    if path.casefold()==NAME_PATH.casefold():
        return [('LNSetName "', '" '+target,old,new,'cp949') for old,new,target in NAMES]
    if path.casefold()==CLICK_PATH.casefold():
        return [('SetStringSetting "sTravelQuestion" "','"', 'Travel to','이동할 장소:','utf-8')]
    if path.casefold()==START_PATH.casefold():
        variables={'sNoFastTravelMessage':'NoFastTravelMessage',
                   'sFastTravelMessage':'FastTravelMessage','sDogmeatMessage':'DogmeatMessage'}
        return [('Goo1.AuxVarSetStr "*svFastTravelExpenses'+variables[key]+
                 '" (GetINIString_Cached "Settings:'+key+
                 '" "Fast Travel Expenses/Fast Travel Expenses.ini" "','")',old,new,'utf-8')
                for key,(old,new) in MESSAGES.items()]
    return []


def script_edit(raw,path):
    original=raw
    lines=raw.splitlines(keepends=True)
    changes,issues=[],[]
    for prefix,suffix,old,new,encoding in script_rules(path):
        if args(old)!=args(new):raise ValueError('Runtime format tokens changed')
        pattern=re.compile(rb'^([ \t]*'+re.escape(prefix.encode())+
                           rb')([^"\r\n]*)('+re.escape(suffix.encode())+rb'[ \t]*)(\r\n|\n|\r|$)',re.I)
        matches=[(i,pattern.fullmatch(line)) for i,line in enumerate(lines)]
        matches=[(i,m) for i,m in matches if m is not None]
        if len(matches)!=1:
            issues.append({'source':old,'reason':'expected_one_exact_command','matches':len(matches)})
            continue
        i,match=matches[0]
        target=new.encode(encoding)
        accepted={old.encode('utf-8'),new.encode('utf-8'),new.encode(encoding)}
        if match[2] not in accepted:
            issues.append({'source':old,'reason':'unreviewed_display_literal'})
            continue
        if match[2]!=target:
            lines[i]=match[1]+target+match[3]+match[4]
            changes.append({'source':old,'translation':new,'encoding':encoding})
    output=b''.join(lines)
    if QUOTED.sub(b'""',output)!=QUOTED.sub(b'""',original):
        raise ValueError('Runtime commands/control flow changed')
    return output,changes,issues


def ini_edit(raw):
    result=[];changes=[];issues=[];section=b''
    for line in raw.splitlines(keepends=True):
        stripped=line.strip()
        if stripped.startswith(b'[') and stripped.endswith(b']'):
            section=stripped[1:-1].lower()
        if section!=b'settings' or b'=' not in line or stripped.startswith((b';',b'#')):
            result.append(line);continue
        prefix,value=line.split(b'=',1)
        key=prefix.strip().decode('ascii')
        if key not in MESSAGES:result.append(line);continue
        ending=value[len(value.rstrip(b'\r\n')):];value=value.rstrip(b'\r\n')
        leading=value[:len(value)-len(value.lstrip(b' \t'))]
        trailing=value[len(value.rstrip(b' \t')):]
        literal=value.strip(b' \t');quoted=literal.startswith(b'"') and literal.endswith(b'"')
        if quoted:literal=literal[1:-1]
        old,new=MESSAGES[key]
        if args(old)!=args(new):raise ValueError('Runtime INI format tokens changed')
        if literal not in (old.encode(),new.encode(),new.encode('cp949')):
            issues.append({'key':key,'reason':'unreviewed_display_value'})
            result.append(line);continue
        target=new.encode('utf-8')
        if target!=literal:
            value=(b'"'+target+b'"') if quoted else target
            line=prefix+b'='+leading+value+trailing+ending
            changes.append({'key':key,'source':old,'translation':new,'encoding':'utf-8'})
        result.append(line)
    return b''.join(result),changes,issues


def edit(raw,provider,path):
    if (provider,path.casefold()) not in {(p,s.casefold()) for p,s in PATHS}:
        return raw,[],[]
    return ini_edit(raw) if path.casefold()==INI_PATH.casefold() else script_edit(raw,path)


def finalize(installation,stage,files):
    import nskr
    known={row['output_path'].casefold():row for row in files}
    for provider,path in PATHS:
        if provider not in installation.mods_enabled:continue
        output_path='mods/'+provider+'/'+path
        target=nskr.contained(stage,output_path)
        row=known.get(output_path.casefold())
        if row is None:
            source=nskr.contained(installation.mods,provider+'/'+path)
            if not source.is_file():continue
            before=nskr.sha256(source);raw=source.read_bytes()
            if nskr.sha256(source)!=before:raise ValueError('Runtime source changed during read')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            row={'output_path':output_path,'path':path,'provider':provider,
                 'source_sha256':before,'output_sha256':before,'status':'reviewed_runtime_source_copy'}
            files.append(row)
        raw=target.read_bytes();output,changes,issues=edit(raw,provider,path)
        if issues:row['runtime_text_review_notes']=issues
        if changes:
            target.write_bytes(output)
            if target.read_bytes()!=output:raise ValueError('Runtime text readback failed')
            row['runtime_text']=changes
            row['status']+='; runtime_display_literals_verified'
            row['output_sha256']=nskr.sha256(target)
