"""Isolated native validation of the next direct-SST Nuclear Sunset plugins.

Never modifies installed MO2 mods. Uses actual active plugin provider and
all recursively required original masters, in the installed load order.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr,nskr_xedit
from tools.tes4_text_scan import masters
SOURCE_RUNTIME=Path(r"D:\Codex_Trans\비바 뉴 베가스\.tools")
INPUT=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
MODLIST=Path(r"C:\Modlists\NuclearSunset")
DEST=ROOT/".local"/"native-plugin-batch-20261010"
TARGETS=[
 "Placement Fixes.esm","DLC Enhancements.esp","Functional Post Game Ending.esm",
 "Goodies.esp","TLD_Travelers.esm","NewVegasBounties.esm",
 "NewVegasKiller.esm","A World of Pain Revised.esm",
 "Better Brotherhood.esm","The Mod Configuration Menu.esp",
 "JustAssortedMods.esp","Enhanced Movement.esp",
 "DryWellsReloaded.esm","Long15Reloaded.esm","3DNPCFNVBundle.esm",
 "Bad Touch.esm","DMT _Dead Money Tweaks_.esp","DMT TTW Patch.esp",
 "CaravanPack.esm","ClassicPack.esm","MercenaryPack.esm","TribalPack.esm",
 "GunRunnersArsenal.esm","Anchorage.esm","BrokenSteel.esm","PointLookout.esm","Zeta.esm",
 "DeadMoney.esm","HonestHearts.esm","OldWorldBlues.esm","LonesomeRoad.esm",
 "FalloutNV.esm","Fallout3.esm","TaleOfTwoWastelands.esm","YUPTTW.esm",
]
def bootstrap_runtime():
    root=ROOT/".tools"
    files={
      "vnvkr-xedit-worker/VNVKRXEditWorker.exe":"nskr-xedit-worker/NSKRXEditWorker.exe",
      "xeditlib-native/XEditLib.dll":"xeditlib-native/XEditLib.dll",
      "xeditlib-native/FalloutNV.Hardcoded.dat":"xeditlib-native/FalloutNV.Hardcoded.dat",
      "xeditlib-native/icudtl.dat":"xeditlib-native/icudtl.dat",
      "xeditlib-native/XEditLib.dll":"nskr-xedit-worker/Backend/XEditLib.dll",
      "xeditlib-native/FalloutNV.Hardcoded.dat":"nskr-xedit-worker/Backend/FalloutNV.Hardcoded.dat",
      "xeditlib-native/icudtl.dat":"nskr-xedit-worker/Backend/icudtl.dat",
    }
    # Dictionary above can't repeat keys: also copy all Backend sibling dependencies.
    for item in ("XEditLib.dll","FalloutNV.Hardcoded.dat","icudtl.dat"):
        source=SOURCE_RUNTIME/"xeditlib-native"/item
        for p in (root/"xeditlib-native"/item,root/"nskr-xedit-worker"/"Backend"/item):
            p.parent.mkdir(parents=True,exist_ok=True)
            if not p.is_file() or p.stat().st_size != source.stat().st_size:shutil.copy2(source,p)
    worker=root/"nskr-xedit-worker"/"NSKRXEditWorker.exe"
    if not worker.is_file():
        worker.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(SOURCE_RUNTIME/"vnvkr-xedit-worker"/"VNVKRXEditWorker.exe",worker)
    nskr_xedit.runtime()
class SubsetInstall:
    def __init__(self,original,loadorder):
        self.original=original;self.active=loadorder
    def source(self,name):return self.original.source(name)
def dependency_order(inst,plugin):
    active={x.casefold():x for x in inst.active}
    required=set()
    def visit(name):
        key=name.casefold()
        if key in required:return
        if key not in active:raise ValueError("Not active: "+name)
        required.add(key)
        p=inst.source(active[key])
        for parent in masters(p):visit(parent)
    visit(plugin)
    ordered=[name for name in inst.active if name.casefold() in required]
    if ordered[-1].casefold()!=plugin.casefold():raise RuntimeError("Target must load last in dependency closure")
    return ordered
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--first",type=int,default=0)
    parser.add_argument("--limit",type=int,default=len(TARGETS))
    args=parser.parse_args()
    bootstrap_runtime()
    install=nskr.Installation(MODLIST)
    catalog=nskr.read_json(INPUT)
    assert catalog["translation_ready"] is False
    entries={e["path"].casefold():e for e in catalog["files"] if e["kind"]=="plugin-records"}
    DEST.mkdir(parents=True,exist_ok=True)
    reportfile=DEST/"summary.json"
    existing=json.loads(reportfile.read_text(encoding="utf-8")) if reportfile.is_file() else []
    finished={x["plugin"].casefold() for x in existing}
    for name in TARGETS[args.first:args.first+args.limit]:
        if name.casefold() in finished:print("ALREADY",name,flush=True);continue
        item=entries.get(name.casefold())
        if item is None:print("NO_MAPPING",name,flush=True);continue
        job=DEST/(name.lower().replace(".esm","").replace(".esp","").replace(" ","_"))
        result={"plugin":name,"candidate_rows":len(item["mappings"]),"status":"not_run"}
        stamp=time.monotonic()
        print("START",name,"CANDIDATES",result["candidate_rows"],flush=True)
        try:
            loadorder=dependency_order(install,name)
            result["dependency_count"]=len(loadorder)
            result["masters_loaded"]=loadorder
            translated,stats=nskr_xedit.merge_plugins(SubsetInstall(install,loadorder),[item],catalog,job)
            r=stats[name]
            result["status"]="PASS" if r["translated"]>0 else "PASS_NO_MATCHED_TRANSLATIONS"
            result["applied"]=r["translated"]
            result["records_verified"]=r["records_verified"]
            result["records_indexed"]=r["records_indexed"]
            result["unmatched_observed_fields"]=r["unmatched"]
            result["unmatched_reasons"]=dict(collections.Counter(x.get("reason") for x in r.get("unmatched_entries",[])))
            result["verification"]=r.get("verification","")
            print("SUCCESS",name,result["status"],result["applied"],"VERIFIED_RECORDS",result["records_verified"],flush=True)
            # Keep proof copies and XEdit apply/readback evidence, but drop the huge copied game masters.
            shutil.rmtree(job/"Game",ignore_errors=True)
        except Exception as err:
            result["status"]="FAIL"
            result["error"]=repr(err)[-3000:]
            if job.exists(): (job/"failure.traceback.txt").write_text(traceback.format_exc(),encoding="utf-8")
            print("FAILED",name,result["error"][-400:],flush=True)
        result["elapsed_seconds"]=round(time.monotonic()-stamp,1)
        existing.append(result)
        reportfile.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SUMMARY",json.dumps([{"plugin":x["plugin"],"status":x["status"],"applied":x.get("applied",0)} for x in existing],ensure_ascii=False),flush=True)
if __name__=="__main__":main()
