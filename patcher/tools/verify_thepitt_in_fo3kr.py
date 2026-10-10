"""Read-only The Pitt translation content verification by FormID and raw text bytes."""
from pathlib import Path
from collections import Counter
import re,struct,zlib,json
kr=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm")
pitt=Path(r"C:\Modlists\NuclearSunset\mods\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)\ThePitt.esm")
def scan(path,master_idx=8):
    d={}
    with path.open("rb") as f:
        f.seek(24+struct.unpack_from("<I",f.read(8),4)[0])
        while True:
            pos=f.tell()
            head=f.read(24)
            if len(head)<24:break
            typ=head[:4]
            n=struct.unpack_from("<I",head,4)[0]
            if typ==b"GRUP":continue
            fid=struct.unpack_from("<I",head,12)[0]
            if (fid>>24)==master_idx:
                payload=f.read(n)
                if struct.unpack_from("<I",head,8)[0] & 0x00040000:
                    try: payload=zlib.decompress(payload[4:])
                    except Exception:pass
                d[fid]=(typ.decode("ascii","replace"),payload)
            else:f.seek(n,1)
    return d
k=scan(kr); o=scan(pitt)
hangul=re.compile("[\uac00-\ud7a3]")
counts=Counter();examples=[]
for fid,(sig,payload) in k.items():
    counts['kr_all']+=1
    if fid in o:
        counts['matched_original']+=1
        if sig==o[fid][0]:counts['signature_matched']+=1
    for encoding in ('utf-8','cp949'):
        s=payload.decode(encoding,errors="ignore")
        matches=hangul.findall(s)
        if matches:
            counts['contains_korean_'+encoding]+=1
            if len(examples)<7 and encoding=='utf-8':
                segs=re.findall(r'[\uac00-\ud7a3][\uac00-\ud7a3\u3130-\u318f\s,.!?~:;()\-]{2,}',s)
                examples.append({'fid':f'{fid:08X}','sig':sig,'text':segs[0][:90] if segs else '(한글 포함)'})
print(json.dumps({'FO3KR_thepitt':len(k),'ThePitt_master':len(o),'counts':dict(counts),'examples':examples},ensure_ascii=False,indent=2))
