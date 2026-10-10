"""Attach a VNV-tested tNVSE Korean font bundle to the UNRELEASED NS catalog.

Builds and readback-verifies the isolated MO2 mod, preserving user's installed
tNVSE files. Font binaries remain local and are not committed to GitHub.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nskr,nskr_fonts
SOURCE=Path(r"D:\Codex_Trans\비바 뉴 베가스\bundles\sst-release-20261006\font-payloads")
CATALOG=Path(r"D:\Codex_Trans\NuclearSunsetPatcherRepo\patcher\.local\ns-sst-with-nexus-quest-esp-v2")
MODLIST=Path(r"C:\Modlists\NuclearSunset")
MOD="Nuclear Sunset - Korean Fonts for tNVSE"
FONTS=("Pretendard-Bold.ttf","NanumSquareEB.ttf","NeoDunggeunmoPro-Regular.ttf","TmonMonsorI.ttf")
NOTICES=("FONT_SOURCES.txt","Pretendard-LICENSE.txt","NAVER-font-license.html",
         "NeoDunggeunmoPro-LICENSE.txt","TMON-author-license.html","TMON-license-notice.html")
def main():
    args=argparse.ArgumentParser()
    args.add_argument("--apply",action="store_true")
    opts=args.parse_args()
    cfile=CATALOG/"catalog.json"
    c=nskr.read_json(cfile)
    if c.get("translation_ready") is not False or c.get("target_modlist")!="nuclear-sunset-ttw":
        raise RuntimeError("This helper must not modify a released catalog")
    if c.get("font_bundle"):raise RuntimeError("Existing font bundle; no overwrite")
    items={"ini":"tnvse.ini","xml":"tnvse_fonts.xml"}
    files={**{name:name for name in FONTS},**{name:name for name in NOTICES},**items}
    spec={"default_mod":MOD,"provider_strategy":"separate_mod","title":"Nuclear Sunset Korean Fonts for tNVSE",
          "ini_overrides":{},"assets":[]}
    folder="nskr-tNVSE-korean-fonts"
    target=CATALOG/folder
    if target.exists():raise RuntimeError("Already staged font folder")
    target.mkdir()
    try:
        for filename in sorted(set(files.values())):
            src=SOURCE/filename
            if not src.is_file():raise FileNotFoundError(src)
            shutil.copy2(src,target/filename)
        for key,filename in items.items():
            p=target/filename
            spec[key]={"payload":f"{folder}/{filename}","payload_sha256":nskr.sha256(p)}
        for filename in FONTS+NOTICES:
            path=(f"NVSE/plugins/fonts/{filename}" if filename in FONTS else f"LICENSES/{filename}")
            spec["assets"].append({"path":path,"payload":f"{folder}/{filename}",
                                   "payload_sha256":nskr.sha256(target/filename)})
        inst=nskr.Installation(MODLIST)
        smoke=CATALOG/".font-bundle-validation"
        if smoke.exists():raise RuntimeError("Previous validation exists")
        smoke.mkdir()
        try:
            outputs,status=nskr_fonts.build_fonts(inst,CATALOG,spec,smoke,set())
            if status.get("mod")!=MOD or status.get("tnvse_installed") is not True:
                raise RuntimeError("Font bundle missing or tNVSE is not detected")
            expected_prefix=f"mods/{MOD}/"
            if any(not x["output_path"].startswith(expected_prefix) for x in outputs):
                raise RuntimeError("Font writer attempted to alter an existing MO2 mod")
            if len(outputs)!=13:raise RuntimeError("Unexpected emitted output files "+str(len(outputs)))
            for row in outputs:
                if nskr.sha256(smoke/row["output_path"])!=row["output_sha256"]:
                    raise RuntimeError("Readback SHA mismatch "+row["output_path"])
            summary={"mode":"staged_only","mod":MOD,"out_files":len(outputs),
                    "tnvse_installed":status["tnvse_installed"],
                    "slots":status["slots"],"all_paths_isolated":True}
            (CATALOG/".font-bundle-validation.json").write_text(
                json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        finally:
            shutil.rmtree(smoke,ignore_errors=True)
        if opts.apply:
            backup=CATALOG/"catalog.before-tNVSE-font-bundle.json"
            if backup.exists():raise RuntimeError("Previous snapshot exists; abort")
            shutil.copy2(cfile,backup)
            c["font_bundle"]=spec
            cfile.write_text(json.dumps(c,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            summary["mode"]="attached_to_unreleased_catalog"
        print(json.dumps(summary,ensure_ascii=False))
    except Exception:
        # Do not delete partial staging after failure; leave for diagnosis.
        raise
if __name__=="__main__":main()
