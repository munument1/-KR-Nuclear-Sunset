"""Conservative native fallback smoke test for Nuclear Sunset plugins without direct SST.

Select existing base/DLC translations ONLY when owner, local FormID, record
signature, field, and English source all match local plugin records. Then the
XEditLib worker further requires the exact hierarchical field path.
Never edits the installed MO2 mods. No translation-ready flag changes.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,shutil,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr,nskr_xedit
from nskr_output import base_translation_memory
from tools.tes4_text_scan import plugin_records,masters,clean_text
from tools.validate_direct_sst_batch import dependency_order,bootstrap_runtime,SubsetInstall

CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
MODLIST=Path(r"C:\Modlists\NuclearSunset")
OUT=ROOT/".local"/"native-fallback-smoke-20261010-v2"
TARGETS=["NS.esm","NS.esp","BraveNewWorld.esm","TTW Dialogue and Interactions Expansion Overhaul.esp"]

def fingerprints(file:Path):
    masterlist=masters(file)
    found=set()
    for fid,sig,fields in plugin_records(file):
        index=fid>>24
        owner=(masterlist[index] if index<len(masterlist) else file.name) if index<=len(masterlist) else None
        if not owner:continue
        for field,raw in fields:
            if field in {"NAM1","NAM2","FULL","DESC","NNAM","RNAM","CNAM","ITXT","TNAM","SNAM","XNAM"}:
                val=clean_text(raw,"utf-8") or clean_text(raw,"cp1252")
                if val:found.add((owner.casefold(),f"{fid&0xffffff:06x}",sig,field,val))
    return found
def main():
    if OUT.exists():raise SystemExit("Refusing to overwrite prior fallback snapshot")
    bootstrap_runtime()
    catalog=nskr.read_json(CATALOG)
    if catalog.get("translation_ready") is not False:raise RuntimeError("Unexpected released catalog")
    install=nskr.Installation(MODLIST)
    print("BUILD_BASE_TRANSLATION_MEMORY",flush=True)
    memory=base_translation_memory(catalog)
    print("BASE_MEMORY",len(memory),"PATH_DEFINED",sum(bool(x["path"]) for x in memory),flush=True)
    lookup=defaultdict(list)
    for row in memory:
        if row.get("path"):
            key=(row["owner"].casefold(),row["id"],row["signature"],row["field"],row["source"])
            lookup[key].append(row)
    OUT.mkdir(parents=True,exist_ok=False)
    stats=[]
    for target in TARGETS:
        job=OUT/(target.lower().replace(".","_").replace(" ","_"))
        result={"plugin":target}
        t0=time.monotonic()
        try:
            source=install.source(target)
            exact=fingerprints(source)
            selected=[r for k in exact for r in lookup.get(k,[])]
            result["record_source_fingerprints"]=len(exact)
            result["fallback_candidate_rows"]=len(selected)
            result["fallback_candidate_records"]=len({(r["owner"],r["id"],r["signature"]) for r in selected})
            print("FALLBACK_START",target,"EXACT_PATH_CANDIDATES",len(selected),flush=True)
            if not selected:
                result["status"]="NO_EXACT_PATH_CANDIDATES"
            else:
                loadorder=dependency_order(install,target)
                entry={"path":target,"kind":"plugin-records","mappings":[]}
                _,out=nskr_xedit.merge_plugins(
                    SubsetInstall(install,loadorder),[entry],catalog,job,
                    fallback_mappings=selected,fallback_targets={target})
                res=out[target]
                result["status"]="PASS" if res["translated"]>0 else "PASS_NO_APPLIED"
                result["applied"]=res["translated"]
                result["records_verified"]=res["records_verified"]
                result["unmatched_observed_fields"]=res["unmatched"]
                print("FALLBACK_RESULT",target,result["status"],res["translated"],flush=True)
                shutil.rmtree(job/"Game",ignore_errors=True)
        except Exception as exc:
            result["status"]="FAIL";result["error"]=repr(exc)[-2500:]
            if job.is_dir():(job/"failure.traceback.txt").write_text(traceback.format_exc(),encoding="utf-8")
            print("FALLBACK_FAIL",target,result["error"][-400:],flush=True)
        result["elapsed_seconds"]=round(time.monotonic()-t0,1)
        stats.append(result)
        (OUT/"summary.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FALLBACK_FINAL",json.dumps(stats,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
