"""Export TTW KOR radio/UI Korean texts as local-only review candidates.

No changes to original ESP, no game binary distribution, no script/condition copying.
All base catalogue conflicts go to review rather than overwriting existing SST.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.tes4_text_scan import masters,plugin_records,clean_text,HANGUL
DEFAULT_ESP=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\TTW KOR Radio + UI.esp")
DEFAULT_CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
DEFAULT_DEST=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\12_TTW_Radio_GMST_시험준비_20261010\donor_translation_candidates")
COLS=["owner_master","formid_original","local_formid","signature","field",
      "edid","korean_reference","source_kind","current_catalog_translation",
      "catalog_coverage","review_status","original_esp_sha256"]
def write(path,rows):
    fields=list(COLS)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--donor",type=Path,default=DEFAULT_ESP)
    ap.add_argument("--catalog",type=Path,default=DEFAULT_CATALOG)
    ap.add_argument("--output",type=Path,default=DEFAULT_DEST)
    args=ap.parse_args()
    if args.output.exists():raise RuntimeError("Refusing to overwrite local review candidates")
    donor=Path(args.donor)
    digest=hashlib.sha256(donor.read_bytes()).hexdigest()
    catalogue=json.loads(args.catalog.read_text(encoding="utf-8"))
    translated=defaultdict(set)
    for file in catalogue.get("files",[]):
        if file.get("kind")!="plugin-records":continue
        for m in file.get("mappings",[]):
            key=(m["owner"].casefold(),m["id"].casefold(),m["signature"],m["field"])
            translated[key].add(m["dest"])
    masterlist=masters(donor)
    candidates={"gmst":[],"info_conflicts":[],"mesg_conflicts":[]}
    stats=Counter()
    for fid,sig,entries in plugin_records(donor):
        if sig not in {"GMST","INFO","MESG"}:continue
        ix=fid>>24
        owner=masterlist[ix] if ix<len(masterlist) else donor.name if ix==len(masterlist) else None
        if owner is None:continue
        source_kind="MASTER_OVERRIDE" if ix<len(masterlist) else "NEW_IN_DONOR"
        edid=""
        for field,raw in entries:
            if field=="EDID":
                edid=clean_text(raw,"utf-8") or clean_text(raw,"cp1252") or ""
                break
        for field,raw in entries:
            if sig=="GMST" and field!="DATA":continue
            if sig=="INFO" and field!="NAM1":continue
            if sig=="MESG" and field not in {"DESC","FULL","ITXT"}:continue
            text=clean_text(raw,"utf-8")
            if not text or not HANGUL.search(text):continue
            stats[f"{sig}_korean_fields"]+=1
            key=(owner.casefold(),f"{fid&0xffffff:06x}",sig,field)
            versions=translated.get(key,set()) if source_kind=="MASTER_OVERRIDE" else set()
            if source_kind=="NEW_IN_DONOR":
                coverage="NEW_RECORD_NOT_MASTER_MATCHABLE"
            elif not versions:
                coverage="NO_EXISTING_SST_TRANSLATION"
            elif text in versions:
                coverage="SAME_AS_EXISTING_SST"
            else:
                coverage="DIFFERS_FROM_EXISTING_SST"
            item={"owner_master":owner,"formid_original":f"{fid:08X}",
                "local_formid":f"{fid&0xffffff:06x}","signature":sig,"field":field,
                "edid":edid,"korean_reference":text,"source_kind":source_kind,
                "current_catalog_translation":" | ".join(sorted(versions)) if len(versions)<=2 else f"{len(versions)} variants",
                "catalog_coverage":coverage,"original_esp_sha256":digest,
                "review_status":"GMST_EDID_AND_RUNTIME_QA_REQUIRED" if sig=="GMST" else
                      "NO_SCRIPT_COPY_ONLY_REVIEW" if sig=="INFO" else "MESSAGE_MAPPING_REVIEW"}
            if sig=="GMST":
                candidates["gmst"].append(item)
            elif sig=="INFO" and coverage!="SAME_AS_EXISTING_SST" and source_kind=="MASTER_OVERRIDE":
                candidates["info_conflicts"].append(item)
            elif sig=="MESG" and coverage!="SAME_AS_EXISTING_SST" and source_kind=="MASTER_OVERRIDE":
                candidates["mesg_conflicts"].append(item)
            stats[f"{sig}_{coverage}"]+=1
    folder=args.output
    folder.mkdir(parents=True)
    for group,file in (("gmst","01_TTW_GMST_한국어_검수.csv"),
                       ("info_conflicts","02_라디오_기존SST_차이_검수.csv"),
                       ("mesg_conflicts","03_메시지_기존SST_차이_검수.csv")):
        write(folder/file,candidates[group])
    summary={"donor_sha256":digest,"GMST_reference_rows":len(candidates["gmst"]),
             "INFO_non_matching_existing_rows":len(candidates["info_conflicts"]),
             "MESG_non_matching_existing_rows":len(candidates["mesg_conflicts"]),
             "catalog_comparison":dict(stats),"not_for_public_upload":True,
             "compiled_scripts_copied":False,"new_ttw_plugin_created":False}
    (folder/"00_검수대상_현황.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"gmst_candidates":len(candidates["gmst"]),
                      "info_review":len(candidates["info_conflicts"]),
                      "message_review":len(candidates["mesg_conflicts"]),
                      "compiled_script_copies":0},ensure_ascii=False))
if __name__=="__main__":main()
