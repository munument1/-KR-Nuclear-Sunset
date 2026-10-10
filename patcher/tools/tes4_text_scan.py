"""Safe, read-only TES4/TTW record scanner for Korean localization feasibility audits."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import struct,zlib,re

HANGUL=re.compile("[\uac00-\ud7a3]")
ENGLISH=re.compile("[A-Za-z]{2}")
# Subrecords whose payload can be text; signature context prevents treating raw binary as prose.
TEXT_FIELDS={
 "FULL","DESC","NAM1","NAM2","NAM3","NAM4","RNAM","CNAM","TNAM",
 "NNAM","ITXT","SNAM","XNAM","MNAM","ONAM","FNAM","BNAM","DNAM",
 "SCTX","SCRO","INAM","ENAM","ETYP","DATA","EDID",
}
# Most reliable displayable source text (exclude editor identifiers, scripts, generic binary DATA).
DISPLAY_FIELDS=TEXT_FIELDS-{"SCTX","SCRO","INAM","ENAM","ETYP","DATA","EDID","BNAM","FNAM","MNAM","ONAM","DNAM"}
# xEdit encoded dialogue/quest etc; string subrecord types in these signatures.
RECORD_SIGS={
 "INFO","DIAL","QUST","BOOK","NOTE","GMST","NPC_","CREA","ARMO","WEAP","MISC","ACTI",
 "DOOR","CELL","WRLD","RACE","MGEF","ENCH","SPEL","ALCH","INGR","LSCR","CONT",
 "FURN","FACT","KEYM","MESG","PERK","TERM","REPU","CHAL","IMOD","CCRD","ARMA",
 "AMMO","WATR","LIGH","MSTT","EXPL","SCPT","COBJ","RCPE","TACT","ACHR","REFR",
 "HDPT","HAIR","CLAS","EYES","GLOB","PACK","LVLI","LVLN","LVLC","SOUN","PROJ",
}
def masters(path:Path):
    with path.open("rb") as f:
        head=f.read(24)
        if head[:4]!=b"TES4":raise ValueError("Not TES4 plugin "+str(path))
        data=f.read(struct.unpack_from("<I",head,4)[0])
    out=[]
    for field,raw in subrecords(data):
        if field=="MAST":
            out.append(raw.rstrip(b"\0").decode("ascii","replace"))
    return out
def subrecords(data:bytes):
    pos=0
    dlen=len(data)
    extended=None
    while pos+6<=dlen:
        typ=data[pos:pos+4]
        sz=struct.unpack_from("<H",data,pos+4)[0]
        pos+=6
        if typ==b"XXXX":
            if sz!=4 or pos+4>dlen:break
            extended=struct.unpack_from("<I",data,pos)[0]
            pos+=4
            continue
        if extended is not None:
            sz=extended
            extended=None
        if sz<0 or pos+sz>dlen:break
        yield typ.decode("ascii","replace"),data[pos:pos+sz]
        pos+=sz
def plugin_records(path:Path, selected_ids=None, only_display=False):
    """Yield (full_formid, signature, list[(subrecord_sig, bytes)]) within plugin.
    Caller must consume iterator before closing.
    """
    with path.open("rb") as f:
        head=f.read(24)
        if head[:4]!=b"TES4":raise ValueError(f"Not TES4: {path}")
        f.seek(struct.unpack_from("<I",head,4)[0],1)
        total=path.stat().st_size
        while f.tell()+24<=total:
            h=f.read(24)
            if len(h)!=24:break
            name=h[:4]
            n=struct.unpack_from("<I",h,4)[0]
            if name==b"GRUP":
                if n<24:break
                continue
            flags=struct.unpack_from("<I",h,8)[0]
            fid=struct.unpack_from("<I",h,12)[0]
            if (selected_ids is not None and fid not in selected_ids) or (only_display and name.decode("ascii","replace") not in RECORD_SIGS) or n>5_000_000:
                f.seek(n,1)
                continue
            raw=f.read(n)
            if flags & 0x00040000:
                if len(raw)<4:continue
                try:raw=zlib.decompress(raw[4:])
                except zlib.error:continue
            sig=name.decode("ascii","replace")
            yield fid,sig,list(subrecords(raw))
def clean_text(raw:bytes,encoding="utf-8"):
    raw=raw.rstrip(b"\x00")
    if not raw or b"\x00" in raw:return None
    try:txt=raw.decode(encoding)
    except UnicodeError:return None
    if len(txt)>4000 or not txt.strip():return None
    if sum(ord(c)<32 and c not in "\n\r\t" for c in txt)>0:return None
    return txt
def field_occurrences(items):
    seen=Counter()
    for f,raw in items:
        index=seen[f]
        seen[f]+=1
        yield f,index,raw
