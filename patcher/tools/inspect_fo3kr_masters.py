from pathlib import Path
import struct,collections,json,zlib
paths=[
Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm"),
Path(r"C:\Modlists\NuclearSunset\mods\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)\ThePitt.esm"),
Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\TaleOfTwoWastelands.esm")
]
def extract(path):
    with path.open("rb") as f:
        hdr=f.read(24)
        if hdr[:4]!=b'TES4':raise ValueError("Not TES4: "+repr(hdr[:4]))
        n=struct.unpack_from("<I",hdr,4)[0]
        dat=f.read(n)
    pos=0; records=[]; masters=[]
    while pos+6<=len(dat):
        typ=dat[pos:pos+4].decode("ascii","replace")
        size=struct.unpack_from("<H",dat,pos+4)[0]
        if typ=="XXXX":
            if size!=4: break
            extended=struct.unpack_from("<I",dat,pos+6)[0]
            pos+=10
            typ=dat[pos:pos+4].decode("ascii","replace")
            size=extended
        else:
            pos+=6
        if pos+size>len(dat): break
        val=dat[pos:pos+size]
        if typ=="MAST":masters.append(val.decode("utf-8","replace").strip("\0"))
        if typ in ("CNAM","SNAM","HEDR"):records.append((typ,val[:160].hex()))
        pos+=size
    counts=collections.Counter()
    # Count FormID origin indexes, and signatures of all plugin records.
    with path.open("rb") as f:
        f.seek(24+n)
        filelen=path.stat().st_size
        bytes_scanned=0; groups=0; recs=0; errors=0
        while f.tell()+24<=filelen:
            offset=f.tell()
            tag=f.read(4)
            raw=f.read(20)
            if len(raw)<20:break
            length=struct.unpack_from("<I",raw,0)[0]
            if tag==b'GRUP':
                if length<24 or offset+length>filelen:
                    errors+=1
                    break
                groups+=1
                # descend into group: group header is only 24 bytes, contents follow
                continue
            if length>filelen-f.tell():
                errors+=1
                break
            fid=struct.unpack_from("<I",raw,8)[0]
            idx=(fid>>24)&255
            counts[("%02X"%idx,tag.decode("ascii","replace"))]+=1
            recs+=1
            f.seek(length,1)
        suffix= f.tell()
    perindex=collections.Counter()
    for (idx,tag),count in counts.items():perindex[idx]+=count
    return {"path":str(path),"size":path.stat().st_size,"masters":masters,"record_count":recs,"group_count":groups,"formid_high_byte_counts":dict(perindex),"top_signatures":counts.most_common(12),"scan_ended_at":suffix,"errors":errors}
for p in paths:
    if p.exists():
        try: print(json.dumps(extract(p),ensure_ascii=False))
        except Exception as e: print(json.dumps({"file":str(p),"error":repr(e)},ensure_ascii=False))
    else: print("MISSING",str(p))
