"""Attach VNV Korean tNVSE 71 fixed DLL to the UNRELEASED NS font bundle.

Preserves original NS tNVSE files/MO2 config and includes GPLv3 complete
corresponding source bundle. All binary/source payload stays local only.
Idempotent, with careful preflight and backup.
"""
from pathlib import Path
import hashlib,json,shutil,struct,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr,nskr_fonts
SOURCE=Path(r"C:\Modlists\VNV\mods\VNV Korean Fonts - tNVSE\NVSE\plugins")
CATALOG=ROOT/".local/ns-sst-with-nexus-quest-esp-v2"
STAGING=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\13_tNVSE_Korean_Fonts_Staging_20261010")
NS=Path(r"C:\Modlists\NuclearSunset")
MOD="Nuclear Sunset - Korean Fonts for tNVSE"
HASH="AD2A81F1440647919BA792F0216ED26A736D4C4A51777F875E85E270538B3D70"
FILES={
    "tnvse.dll":("NVSE/plugins/tnvse.dll",SOURCE/"tnvse.dll"),
    "tNVSE-GPL-3.0.txt":("NVSE/plugins/fonts/licenses/tNVSE-GPL-3.0.txt",SOURCE/"fonts/licenses/tNVSE-GPL-3.0.txt"),
    "tNVSE-KR-UI-fix.txt":("NVSE/plugins/fonts/licenses/tNVSE-KR-UI-fix.txt",SOURCE/"fonts/licenses/tNVSE-KR-UI-fix.txt"),
    "tNVSE-71-KR-UI-source.zip":("NVSE/plugins/fonts/licenses/tNVSE-71-KR-UI-source.zip",SOURCE/"fonts/licenses/tNVSE-71-KR-UI-source.zip"),
}
def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()
def main():
    dll=FILES["tnvse.dll"][1]
    if sha(dll).upper()!=HASH:raise RuntimeError("Source Korean tNVSE DLL SHA mismatch")
    current=NS/"mods/tNVSE/NVSE/plugins/tnvse.dll"
    if not current.is_file():raise RuntimeError("User's tNVSE baseline not installed")
    if sha(current).upper()==HASH:raise RuntimeError("Expected different original DLL; overlay is unnecessary")
    with dll.open("rb") as fp:
        data=fp.read(4096)
    if data[:2]!=b"MZ" or struct.unpack_from("<I",data,0x3c)[0]+6>len(data):
        raise RuntimeError("Invalid DLL header")
    pos=struct.unpack_from("<I",data,0x3c)[0]
    if data[pos:pos+4]!=b"PE\x00\x00" or struct.unpack_from("<H",data,pos+4)[0]!=0x014c:
        raise RuntimeError("Expected 32-bit Win32 DLL")
    src_archive=FILES["tNVSE-71-KR-UI-source.zip"][1]
    with zipfile.ZipFile(src_archive) as archive:
        if archive.testzip() is not None:raise RuntimeError("Modified source archive CRC invalid")
        if len(archive.namelist())<10:raise RuntimeError("Modified source ZIP unexpectedly empty")
    for rel,src in FILES.values():
        if not src.is_file():raise FileNotFoundError(str(src))
    file=CATALOG/"catalog.json"
    cat=json.loads(file.read_text(encoding="utf-8"))
    if cat.get("translation_ready") is not False:raise RuntimeError("Do not alter released catalog")
    bundle=cat.get("font_bundle")
    if bundle is None or bundle.get("default_mod")!=MOD or bundle.get("provider_strategy")!="separate_mod":
        raise RuntimeError("Missing separately staged Korean font bundle")
    if any(x["path"].casefold()=="nvse/plugins/tnvse.dll" for x in bundle["assets"]):
        print("ALREADY_REGISTERED");return
    directory=CATALOG/"nskr-tNVSE-korean-fonts"
    if not directory.is_dir():raise RuntimeError("Bundled font directory missing")
    local_staging=STAGING/"mods"/MOD
    if not local_staging.is_dir():raise RuntimeError("Local trial font mod missing")
    base="nskr-tNVSE-korean-fonts"
    assets=[]
    for name,(virtual,src) in FILES.items():
        target=directory/name
        if target.exists() and sha(target)!=sha(src):
            raise RuntimeError("Existing staged payload differs: "+name)
        if (local_staging/virtual).exists() and sha(local_staging/virtual)!=sha(src):
            raise RuntimeError("Existing staged trial payload differs: "+virtual)
        assets.append({"path":virtual,"payload":f"{base}/{name}","payload_sha256":sha(src)})
    # Stage copy before changing the manifest. Original installed NS tNVSE untouched.
    for name,(virtual,src) in FILES.items():
        dest=directory/name
        shutil.copy2(src,dest)
        if sha(dest)!=sha(src):raise RuntimeError("Staged payload checksum mismatch")
        runtime_file=local_staging/virtual
        runtime_file.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,runtime_file)
        if sha(runtime_file)!=sha(src):raise RuntimeError("Staged mod checksum mismatch")
    old_file=CATALOG/"catalog.before-KR-tNVSE-DLL.json"
    if old_file.exists():
        if sha(old_file)!=sha(file):
            raise RuntimeError("Previously backed-up catalog has diverged")
    else:
        shutil.copy2(file,old_file)
    bundle["assets"].extend(assets)
    # Re-verify actual Output emitter with every resulting asset including DLL+GPL source.
    install=nskr.Installation(NS)
    scratch=CATALOG/".font-dll-validation"
    if scratch.exists():raise RuntimeError("Previous smoke test folder exists")
    scratch.mkdir()
    try:
        emit,status=nskr_fonts.build_fonts(install,CATALOG,bundle,scratch,set())
        expected="mods/"+MOD+"/"
        if len(emit)!=17 or any(not row["output_path"].startswith(expected) for row in emit):
            raise RuntimeError("Output tree wrong or missing files")
        dll_rows=[row for row in emit if row["output_path"].casefold().endswith("nvse/plugins/tnvse.dll")]
        if len(dll_rows)!=1:raise RuntimeError("Korean tNVSE DLL missing from produced Output")
        if sha(scratch/dll_rows[0]["output_path"]).upper()!=HASH:
            raise RuntimeError("Final DLL checksum mismatch")
        for row in emit:
            if sha(scratch/row["output_path"])!=row["output_sha256"]:
                raise RuntimeError("Output file hash differs "+row["output_path"])
        if sha(current).upper()==HASH:raise RuntimeError("Original tNVSE was modified")
        report={"mod":MOD,"dll_sha256":HASH,"original_sha256":sha(current),
                "output_files":len(emit),"source_zip_included":True,
                "gpl_license_included":True,"original_mo2_unchanged":True,
                "translation_ready":cat["translation_ready"],"game_validation":"not_run"}
        (CATALOG/".font-dll-validation.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    finally:
        shutil.rmtree(scratch,ignore_errors=True)
    file.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Supplement trial mod inventory for the user.
    manifest_file=STAGING/"manifest.json"
    if manifest_file.is_file():
        record=json.loads(manifest_file.read_text(encoding="utf-8"))
        for name,(virtual,src) in FILES.items():
            record["files"].append({"file":virtual,"sha256":sha(src),"bytes":src.stat().st_size})
        record["tnvse_binary_included"]=True
        record["tnvse_korean_ui_fix_source_available"]=True
        manifest_file.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    readme=STAGING/"README_KO.md"
    if readme.is_file():
        before=readme.read_text(encoding="utf-8")
        readme.write_text(before+"\n- **IMPORTANT: VNV Korean tNVSE 71 DLL overrides upstream tNVSE in this mod.**\n"
            "- This is required to fix reported broken Korean interactive GMST/UI replacements.\n"
            "- GPL-3.0 license, fix note, and source ZIP are included alongside the DLL.\n"
            "- Enable this mod after both tNVSE and tNVSE Default Config in MO2; do not replace the originals.\n",
            encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
