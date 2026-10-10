"""Native XEditLib pre-release validation for two imported Nexus translation SSTs.

Works only on a user-owned Windows MO2 instance. Copies required files to .local
isolated temporary game roots; never writes to the installed modlist.
"""
from pathlib import Path
import sys,json,shutil,hashlib,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
import nskr_xedit
SOURCE_RUNTIME=Path(r"D:\Codex_Trans\비바 뉴 베가스\.tools")
OUT=ROOT/".local"/"native-validation-20261010-v2"
INPUT=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
def bootstrap():
    binaries={
        "vnvkr-xedit-worker/VNVKRXEditWorker.exe":"nskr-xedit-worker/NSKRXEditWorker.exe",
        "xeditlib-native/XEditLib.dll":"xeditlib-native/XEditLib.dll",
        "xeditlib-native/FalloutNV.Hardcoded.dat":"xeditlib-native/FalloutNV.Hardcoded.dat",
        "xeditlib-native/icudtl.dat":"xeditlib-native/icudtl.dat",
    }
    for origin,dest in binaries.items():
        src=SOURCE_RUNTIME/origin; target=ROOT/".tools"/dest
        if not src.is_file():raise FileNotFoundError(src)
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(src.read_bytes()).digest():
            shutil.copy2(src,target)
    # The frozen VNV worker resolves its native DLL next to its executable,
    # rather than consulting the Python runner's environment variable.
    backend=ROOT/".tools"/"nskr-xedit-worker"/"Backend"
    backend.mkdir(parents=True,exist_ok=True)
    for name in ("XEditLib.dll","FalloutNV.Hardcoded.dat","icudtl.dat"):
        origin=SOURCE_RUNTIME/"xeditlib-native"/name
        target=backend/name
        if not target.exists() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(origin.read_bytes()).digest():
            shutil.copy2(origin,target)
    return nskr_xedit.runtime()
class MinimalInstall:
    def __init__(self,actual,plugins):
        self.actual=actual
        self.active=list(plugins)
    def source(self,plugin):return self.actual.source(plugin)
def main():
    if OUT.exists():raise SystemExit(f"Output directory already exists, not overwriting: {OUT}")
    bootstrap()
    catalog=nskr.read_json(INPUT)
    if catalog.get("translation_ready") is not False:
        raise RuntimeError("Refusing pre-release without readiness gate")
    actual=nskr.Installation(Path(r"C:\Modlists\NuclearSunset"))
    targets={
      "AutumnLeaves.esp":["FalloutNV.esm","AutumnLeaves.esp"],
      "ZionTrail.esm":["FalloutNV.esm","DeadMoney.esm","HonestHearts.esm","OldWorldBlues.esm","LonesomeRoad.esm","ZionTrail.esm"]
    }
    OUT.mkdir(parents=True)
    summary=[]
    for plugin,seq in targets.items():
        entry=next(x for x in catalog["files"] if x["path"].casefold()==plugin.casefold())
        result={"plugin":plugin,"candidate_rows":len(entry["mappings"]),"masters_loaded":seq}
        job=OUT/plugin.rsplit(".",1)[0]
        print("NATIVE_START",plugin,"rows",result["candidate_rows"],flush=True)
        t0=time.monotonic()
        try:
            _,stats=nskr_xedit.merge_plugins(
                MinimalInstall(actual,seq),[entry],catalog,job,
                progress=lambda msg:print(plugin,"PROGRESS",msg.encode("unicode_escape").decode("ascii")[:130],flush=True)
            )
            result["status"]="native_apply_and_readback_passed"
            result["stats"]={k:v for k,v in stats[plugin].items() if k!="unmatched_entries"}
            result["unmatched_reason_counts"]={}
            from collections import Counter
            result["unmatched_reason_counts"]=dict(Counter(x["reason"] for x in stats[plugin].get("unmatched_entries",[])))
            print("NATIVE_SUCCESS",json.dumps(result,ensure_ascii=False),flush=True)
        except Exception as exc:
            result["status"]="native_validation_failed"
            result["error"]=repr(exc)
            (job.parent/(job.name+".traceback.txt")).write_text(traceback.format_exc(),encoding="utf-8")
            print("NATIVE_FAILED",plugin,repr(exc),flush=True)
        result["elapsed_seconds"]=round(time.monotonic()-t0,1)
        summary.append(result)
        (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FINAL",json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
