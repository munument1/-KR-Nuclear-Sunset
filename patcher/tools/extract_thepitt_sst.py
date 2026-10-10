"""Extract The Pitt Korean translation SST candidates from FO3 KR.esm, read only.

Writes only into patcher/.local/thepitt. All candidate translations are still
subject to xEdit readback, manual review, and redistribution permissions.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,struct,zlib,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from nskr_sst import read_sst
import nskr_xedit
from tes4_text_scan import plugin_records, masters, clean_text, HANGUL, ENGLISH, DISPLAY_FIELDS,field_occurrences

ROOT=Path(__file__).resolve().parents[1]
TTW=Path(r"C:\Modlists\NuclearSunset\mods\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)")
ORIGINAL=TTW/"ThePitt.esm"
KOREAN=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm")
OUT=ROOT/".local"/"thepitt"

def get_data():
    km=masters(KOREAN); srcm=masters(ORIGINAL)
    if "ThePitt.esm" not in km or not srcm:
        raise ValueError("Missing required TTW master names")
    idx=km.index("ThePitt.esm")
    ori_idx=len(srcm)
    ko={fid:(sig,rows) for fid,sig,rows in plugin_records(KOREAN) if fid>>24==idx}
    original_ids={((fid&0x00ffffff)|(ori_idx<<24)) for fid in ko}
    origin={fid:(sig,rows) for fid,sig,rows in plugin_records(ORIGINAL,original_ids)}
    return km,srcm,idx,ko,origin

def diff(km,srcm,idx,kr,orig):
    total=Counter(); kinds=Counter(); rows=[]; skipped=Counter(); sig_count=Counter()
    # original and target FormIDs have aligned master indexes in this TTW build.
    for fid,(sig,ko_fields) in kr.items():
        total["kr_owned_records"]+=1
        old=orig.get(fid)
        if not old or old[0]!=sig:
            skipped["unmatched_record"]+=1
            continue
        total["matched_signatures"]+=1
        if sig not in {
            "INFO","DIAL","QUST","BOOK","NOTE","GMST","NPC_","CREA","ARMO",
            "WEAP","MISC","ACTI","DOOR","CELL","WRLD","RACE","MGEF","ENCH",
            "SPEL","ALCH","INGR","LSCR","CONT","FURN","FACT","KEYM",
            "MESG","PERK","TERM","REPU","CHAL","IMOD","AMMO","LIGH","MSTT"
        }:continue
        old_fields=list(field_occurrences(old[1]))
        oldlookup={(field,index):raw for field,index,raw in old_fields}
        for field,index,kraw in field_occurrences(ko_fields):
            if field not in DISPLAY_FIELDS:continue
            base=oldlookup.get((field,index))
            if base is None or base==kraw:continue
            source=clean_text(base,"utf-8") or clean_text(base,"cp1252")
            dest=clean_text(kraw,"utf-8")
            if not (source and dest and source!=dest and HANGUL.search(dest)):
                skipped["not_clean_english_korean_pair"]+=1;continue
            if "\ufffd" in (source+dest):
                skipped["replacement_character"]+=1;continue
            row={
                "owner":"thepitt.esm",
                "id":f"{fid & 0x00ffffff:06x}",
                "signature":sig,
                "field":field,
                "path":field if sig in {"BOOK","NOTE","NPC_","RACE","WEAP","ARMO","MISC","ACTI","DOOR","CELL","WRLD","CREA","PERK","SPEL","ALCH","INGR","LSCR","FACT","KEYM","ENCH","AMMO","LIGH","MSTT"} else "",
                "source":source,
                "dest":dest,
                "rec_id":index,
                "rec_id_max":index,
                "string_id":zlib.crc32(base),
                "origin":"fo3_kr_esm_thepitt",
            }
            try:nskr_xedit.validate_mapping(row)
            except ValueError:
                skipped["unsafe_control_tokens"]+=1;continue
            rows.append(row)
            kinds[field]+=1
            sig_count[sig]+=1
    # A destination conflicting for same record/field/source is unsafe.
    kdest=defaultdict(set)
    for r in rows:
        k=(r["owner"],r["id"],r["signature"],r["field"],r["source"])
        kdest[k].add(r["dest"])
    conflicts={k for k,v in kdest.items() if len(v)>1}
    if conflicts:
        skipped["ambiguous_pairs"]+=len(conflicts)
        rows=[r for r in rows if (r["owner"],r["id"],r["signature"],r["field"],r["source"]) not in conflicts]
    total["validated_candidate_pairs"]=len(rows)
    total["records_with_candidate"]=len({(r["id"],r["signature"]) for r in rows})
    return rows,{"counts":dict(total),"field_kinds":dict(kinds.most_common()),
                 "signature_counts":dict(sig_count.most_common()),
                 "skipped":dict(skipped),"master_index":idx}

def write_sst(dest:Path,plugin_masters:list[str],rows:list[dict]):
    # SSU9-format export, parsed back to verify structural integrity; needs xTranslator GUI compatibility check.
    plugins=plugin_masters+["ThePitt.esm"]
    data=bytearray(b"SSU9\x00"+struct.pack("<I",len(plugins)))
    for p in plugins:
        b=p.encode("utf-16le")
        data+=struct.pack("<I",len(b))+b
    for row in rows:
        fid=((len(plugins)-1)<<24)|int(row["id"],16)
        src=row["source"].encode("utf-16le")
        ko=row["dest"].encode("utf-16le")
        data+=struct.pack("<I",fid)
        data+=(row["signature"]+row["field"]).encode("ascii")
        data+=struct.pack("<HHIH",min(65535,row["rec_id"]),min(65535,row["rec_id_max"]),row["string_id"],0x100)
        data+=struct.pack("<I",len(src))+src+struct.pack("<I",len(ko))+ko
        data+=bytes(5)
    dest.write_bytes(data)
    reread=read_sst(dest)
    if len(reread.entries)!=len(rows) or reread.plugins!=plugins:
        raise RuntimeError("SST roundtrip structure differs")
    for i,item in enumerate(reread.entries):
        r=rows[i]
        if (item.form_id&0x00ffffff)!=int(r["id"],16) or item.source!=r["source"] or item.dest!=r["dest"]:
            raise RuntimeError(f"SST data roundtrip mismatch at index {i}")

def main():
    if OUT.exists():raise SystemExit("Output directory exists; do not overwrite translation snapshots")
    km,om,index,kr,original=get_data()
    rows,report=diff(km,om,index,kr,original)
    if not rows:raise SystemExit("No safe translation candidates found")
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/"thepitt_candidate_mappings.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_sst(OUT/"thepitt_en_ko.sst",om,rows)
    report.update({"source_plugin":str(KOREAN),"original_plugin":str(ORIGINAL),
                   "sst_generated_file":str(OUT/"thepitt_en_ko.sst"),
                   "status":"SST roundtrip verified; NOT YET validated against xEdit textual field paths / in-game output",
                   "source_sha256":hashlib.sha256(KOREAN.read_bytes()).hexdigest()})
    (OUT/"extraction_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
