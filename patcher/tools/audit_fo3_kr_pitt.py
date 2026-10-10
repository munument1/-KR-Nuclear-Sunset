"""Read-only audit of The Pitt references and translated text in FO3 KR.esm.
Does not modify or distribute source ESM files.
"""
import argparse
from collections import Counter
import json, re, struct, zlib
from pathlib import Path

KOR_RE = re.compile(r"[\uac00-\ud7a3]")
SIG_RE = re.compile(r"^[A-Z0-9_]{4}$")
RECORD_HEADER_SIZE=24
def fields(blob):
    pos=0
    extended=None
    while pos+6<=len(blob):
        tag=blob[pos:pos+4].decode("latin1")
        size=struct.unpack_from("<H",blob,pos+4)[0]
        pos+=6
        if tag=="XXXX":
            if size != 4 or pos+4>len(blob): raise ValueError("bad XXXX")
            extended=struct.unpack_from("<I",blob,pos)[0]
            pos+=4
            continue
        if extended is not None:
            size, extended=extended,None
        if pos+size>len(blob): raise ValueError("subrecord exceeds bounds")
        yield tag,blob[pos:pos+size]
        pos+=size
def masters(path):
    with path.open("rb") as f:
        header=f.read(24)
        if header[:4]!=b"TES4":raise ValueError("not a TES4 plugin")
        body=f.read(struct.unpack_from("<I",header,4)[0])
    return [data.split(b"\0")[0].decode("cp1252",errors="replace") for tag,data in fields(body) if tag=="MAST"]
def plugin_records(path):
    data=path.read_bytes()
    size=len(data)
    if data[:4]!=b"TES4": raise ValueError("not TES4")
    pos=24+struct.unpack_from("<I",data,4)[0]
    while pos+24<=size:
        typ=data[pos:pos+4]
        if typ==b"GRUP":
            n=struct.unpack_from("<I",data,pos+4)[0]
            if n<24 or pos+n>size:raise ValueError(f"invalid group at {pos}")
            pos+=24
            continue
        s=struct.unpack_from("<I",data,pos+4)[0]
        flags=struct.unpack_from("<I",data,pos+8)[0]
        formid=struct.unpack_from("<I",data,pos+12)[0]
        end=pos+24+s
        if end>size:raise ValueError(f"record extends beyond file at {pos}")
        tag=typ.decode("latin1")
        if not SIG_RE.fullmatch(tag):raise ValueError(f"bad record signature {tag}@{pos}")
        payload=data[pos+24:end]
        if flags & 0x00040000:
            if len(payload)<4: raise ValueError("compressed record too short")
            payload=zlib.decompress(payload[4:])
        yield tag,formid,payload
        pos=end
    if pos != size: raise ValueError(f"unread trailing bytes {size-pos}")

def text_subrecords(payload):
    out=[]
    for tag,raw in fields(payload):
        if tag not in {"FULL","DESC","NAM1"}: continue
        if not raw or raw.find(b"\x00")<0: continue
        # Only record clear, single null-terminated text strings.
        b=raw.rstrip(b"\0")
        if b"\0" in b or len(b)<2: continue
        for enc in ("utf-8","cp1252"):
            try:
                val=b.decode(enc,errors="strict")
                if not val.isprintable(): continue
                if any(ord(c)<32 for c in val):continue
                out.append((tag,val))
                break
            except UnicodeDecodeError:continue
    return out

def audit(original, translated, owner="ThePitt.esm"):
    origmasters=masters(original)
    trmasters=masters(translated)
    if owner.casefold() not in {x.casefold() for x in origmasters} and original.name.casefold()!=owner.casefold():
        raise ValueError("owner absent from original")
    if owner.casefold() not in {x.casefold() for x in trmasters}:
        raise ValueError("owner absent from localized plugin")
    origindex=next((i for i,x in enumerate(origmasters) if x.casefold()==owner.casefold()),len(origmasters))
    trindex=next(i for i,x in enumerate(trmasters) if x.casefold()==owner.casefold())
    original_self={}
    origtypes=Counter()
    for sig,formid,payload in plugin_records(original):
        if formid>>24==origindex:
            local=formid&0xffffff
            original_self[(local,sig)]=payload
            origtypes[sig]+=1
    trtypes=Counter()
    comparable=0; with_hangul=0; changed=0; text_records=0; sample_sigs=Counter(); unicode_errors=0
    tr_records=0; match_records=0
    for sig,formid,payload in plugin_records(translated):
        if formid>>24 != trindex:continue
        tr_records+=1
        trtypes[sig]+=1
        key=(formid&0xffffff,sig)
        if key not in original_self:continue
        match_records+=1
        try:
            trt=text_subrecords(payload)
            src=text_subrecords(original_self[key])
        except ValueError:
            unicode_errors+=1
            continue
        srcdict={}
        for tag,value in src:
            srcdict.setdefault(tag,[]).append(value)
        used=Counter()
        if trt: text_records+=1
        for tag,val in trt:
            index=used[tag]
            used[tag]+=1
            values=srcdict.get(tag,[])
            if index>=len(values):continue
            comparable+=1
            if val !=values[index]: changed+=1
            if KOR_RE.search(val):
                with_hangul+=1
                sample_sigs[sig]+=1
    return {
      "localized_plugin":str(translated),
      "original_plugin":str(original),
      "original_masters":origmasters,
      "localized_masters":trmasters,
      "original_owner_index":origindex,
      "localized_owner_index":trindex,
      "original_self_owned_records":len(original_self),
      "localized_owner_records":tr_records,
      "localized_records_matching_original":match_records,
      "localized_owner_record_types":trtypes.most_common(20),
      "compared_text_subfields":comparable,
      "changed_text_subfields":changed,
      "korean_text_subfields":with_hangul,
      "example_korean_record_types":sample_sigs.most_common(15),
      "unreadable_subrecords":unicode_errors,
      "notes":["Counts concern The Pitt-owned records only, not Fallout3 base records overridden by The Pitt.",
               "Only FULL/DESC/NAM1 are sampled for text evidence; other dialogue and quest fields require native validation.",
               "No translation or distribution rights implied by this inspection."]}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--translated",type=Path,default=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm"))
    ap.add_argument("--original",type=Path,default=Path(r"C:\Modlists\NuclearSunset\mods\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)\ThePitt.esm"))
    ap.add_argument("--report",type=Path)
    a=ap.parse_args()
    r=audit(a.original,a.translated)
    txt=json.dumps(r,ensure_ascii=False,indent=2)
    print(txt)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(txt+"\n",encoding="utf-8")
if __name__=="__main__": main()
