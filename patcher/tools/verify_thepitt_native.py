"""Verify imported local The Pitt SST using native XEditLib in an isolated staging directory."""
from pathlib import Path
import json,sys,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.verify_nexus_sst_native import bootstrap,MinimalInstall
import nskr,nskr_xedit
PLUGIN="ThePitt.esm"
CHAIN=[
    "FalloutNV.esm","DeadMoney.esm","HonestHearts.esm","OldWorldBlues.esm",
    "LonesomeRoad.esm","GunRunnersArsenal.esm","Fallout3.esm","Anchorage.esm","ThePitt.esm"
]
OUT=ROOT/".local"/"native-validation-thepitt-20261010"
def main():
    if OUT.exists(): raise SystemExit("Refusing overwrite")
    bootstrap()
    catalog=nskr.read_json(ROOT/".local"/"ns-sst-expanded"/"catalog.json")
    entry=next(e for e in catalog["files"] if e.get("path","").lower()==PLUGIN.lower())
    actual=nskr.Installation(Path(r"C:\Modlists\NuclearSunset"))
    OUT.mkdir(parents=True,exist_ok=False)
    print("THEPITT_START",len(entry["mappings"]),flush=True)
    try:
        _,res=nskr_xedit.merge_plugins(
            MinimalInstall(actual,CHAIN),[entry],catalog,OUT/"thepitt",
            progress=lambda msg:print("PITT_PROGRESS",str(msg).encode("unicode_escape").decode()[:120],flush=True))
        data={k:v for k,v in res[PLUGIN].items() if k!="unmatched_entries"}
        data["candidate_sst_rows"]=len(entry["mappings"])
        data["status"]="apply_and_fresh_readback_passed"
        (OUT/"result_summary.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        print("PITT_SUCCESS",json.dumps(data,ensure_ascii=False),flush=True)
    except Exception as e:
        print("PITT_FAILED",repr(e),flush=True)
        if OUT.exists(): (OUT/"failure.txt").write_text(traceback.format_exc(),encoding="utf-8")
if __name__=="__main__":main()
