"""Validate inherited SST on the highest-impact remaining manual review plugins.

Reads staged English CSVs and validated base/DLC SST memory. Exact owner,
local FormID, signature, subrecord field AND English source are required.
Native XEditLib further checks full path; original MO2 source is never edited.
"""
import argparse,csv,json,shutil,sys,time,traceback
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr,nskr_xedit
from nskr_output import base_translation_memory
from tools.validate_direct_sst_batch import bootstrap_runtime,dependency_order,SubsetInstall
WORK=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
OUT=ROOT/".local"/"inherited-manual-batch-20261010"
MODLIST=Path(r"C:\Modlists\NuclearSunset")
TARGETS=[
 "EDGE TTW.esp","STAR TTW 2.esp","Vanilla SWEEP.esp",
 "Dynamic World and TODD Patch.esp","Sweet Consumables.esp",
 "TTW NPC Overhaul.esm","Vanilla Enhancements.esm",
 "Goodies - TTW.esp","NSNPCs.esp","ATMOS Ambient Overhaul.esp",
 "[RWM]-Complete Added.esp","New Blood.esp",
 "NavmeshOverhaul.esm","Mojave Raiders.esp",
]
def load(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
def build_index(catalog):
    store=defaultdict(list)
    for item in base_translation_memory(catalog):
        if not item.get("path"):continue
        key=(item["owner"].casefold(),item["id"].casefold(),
             item["signature"],item["field"],item["source"])
        store[key].append(item)
    return store
def candidates(row,index):
    csvfile=WORK/row["english_csv"]
    if not csvfile.is_file():raise FileNotFoundError(csvfile)
    selected={}
    eligible=0
    for item in load(csvfile):
        if not item.get("existing_korean_candidate"):continue
        eligible+=1
        key=(item["origin_master"].casefold(),item["formid"][-6:].casefold(),
             item["signature"],item["field"],item["english_source"])
        for r in index.get(key,[]):
            token=(r["owner"],r["id"],r["signature"],r["field"],r["path"],r["source"],r["dest"])
            selected[token]=r
    return list(selected.values()),eligible
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--first",type=int,default=0)
    parser.add_argument("--limit",type=int,default=len(TARGETS))
    opts=parser.parse_args()
    bootstrap_runtime()
    catalog=nskr.read_json(CATALOG)
    assert catalog["translation_ready"] is False
    inst=nskr.Installation(MODLIST)
    manifest={r["plugin"].casefold():r for r in load(WORK/"00_플러그인_대상목록.csv")}
    for name in TARGETS:
        if name.casefold() not in manifest:raise RuntimeError("Not in manual workspace "+name)
    print("LOADING_MEMORY",flush=True)
    index=build_index(catalog)
    print("MEMORY_KEYS",len(index),flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    report=OUT/"summary.json"
    results=json.loads(report.read_text(encoding="utf-8")) if report.is_file() else []
    done={r["plugin"].casefold() for r in results}
    for name in TARGETS[opts.first:opts.first+opts.limit]:
        if name.casefold() in done:print("SKIP_ALREADY",name,flush=True);continue
        row=manifest[name.casefold()]
        case={"plugin":name,"csv_inherited_candidates":int(row["base_fallback_candidates"]),
              "new_translation_candidates":int(row["need_new_translation"])}
        started=time.monotonic()
        folder=OUT/(name.casefold().replace(".","_").replace(" ","_").replace("/","_"))
        try:
            selected,eligible=candidates(row,index)
            case["eligible_csv_rows"]=eligible
            case["exact_path_candidates"]=len(selected)
            print("START",name,"MATCHES",len(selected),flush=True)
            if not selected:
                case["status"]="NO_EXACT_PATH"
            else:
                order=dependency_order(inst,name)
                entry={"path":name,"kind":"plugin-records","mappings":[]}
                translated,stats=nskr_xedit.merge_plugins(
                    SubsetInstall(inst,order),[entry],catalog,folder,
                    fallback_mappings=selected,fallback_targets={name})
                actual=stats[name]
                case["status"]="PASS" if actual["translated"]>0 else "NO_APPLIED"
                case["applied"]=actual["translated"]
                case["verified_records"]=actual["records_verified"]
                case["unmatched_inspected_fields"]=actual["unmatched"]
                shutil.rmtree(folder/"Game",ignore_errors=True)
                print("PASS",name,case["applied"],"RECORDS",case["verified_records"],flush=True)
        except Exception as err:
            case["status"]="FAIL"
            case["error"]=repr(err)[-1700:]
            if folder.exists():(folder/"error.txt").write_text(traceback.format_exc(),encoding="utf-8")
            print("FAIL",name,case["error"][-300:],flush=True)
        case["seconds"]=round(time.monotonic()-started,1)
        results.append(case)
        report.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SUMMARY",json.dumps({"checked":len(results),"passed":sum(x["status"]=="PASS" for x in results),
             "applied":sum(x.get("applied",0) for x in results)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
