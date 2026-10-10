"""Stage an OPTIONAL MIT-licensed xNVSE radio caption mod for Nuclear Sunset.

Copies only a safe allowlisted VNV preview payload and notices.
Never touches TTW ESP, installed MO2 mods, game files, or profiles.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, struct
APP=Path(r"D:\Codex_Trans\비바 뉴 베가스")
DEFAULT_SOURCE=APP/"Output-Release-20261004"/"mods"/"VNV Korean Radio Captions"
DEFAULT_OUTPUT=APP/"뉴클리어 선셋"/"12_TTW_Radio_GMST_시험준비_20261010"
MOD_NAME="Nuclear Sunset - Radio Captions (Experimental)"
ALLOWLIST=(
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "NVSE/Plugins/MojaveRadioCaptions.dll",
    "NVSE/Plugins/MojaveRadioCaptions.ini",
    "uio/public/MojaveRadioCaptions.txt",
    "menus/prefabs/MojaveRadioCaptions/MojaveRadioCaptions.xml",
)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def pe_machine(file):
    with file.open("rb") as fp:
        buf=fp.read(512)
    if len(buf)<64 or buf[:2]!=b"MZ":
        raise ValueError("Unexpected executable format")
    offset=struct.unpack_from("<I",buf,0x3C)[0]
    if offset+6>len(buf) or buf[offset:offset+4]!=b"PE\x00\x00":
        raise ValueError("Unexpected PE headers")
    return struct.unpack_from("<H",buf,offset+4)[0]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    source=args.source.resolve()
    out=args.output.resolve()
    if out.exists():
        raise SystemExit("Refusing to overwrite prepared local output: "+str(out))
    if out.is_relative_to(source) or source.is_relative_to(out):
        raise SystemExit("Refusing to overlap source tree")
    if str(out).lower().startswith("c:\\modlists\\nuclearsunset"):
        raise SystemExit("MO2 or game directory must not be modified")
    if not (source/"LICENSE").read_text(encoding="utf-8").startswith("MIT License"):
        raise RuntimeError("Unexpected license; do not redistribute blindly")
    if pe_machine(source/"NVSE/Plugins/MojaveRadioCaptions.dll") != 0x14c:
        raise RuntimeError("xNVSE requires a 32-bit x86 DLL")
    snapshots=[]
    for relative in ALLOWLIST:
        f=source/relative
        if not f.is_file():raise FileNotFoundError(str(f))
        snapshots.append({"path":relative,"sha256":sha(f),"bytes":f.stat().st_size})
    dest=out/"mods"/MOD_NAME
    for r in snapshots:
        original=source/r["path"]
        target=dest/r["path"]
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(original,target)
        if sha(target)!=r["sha256"]:raise RuntimeError("Checksum mismatch "+r["path"])
    note=(
        "# Nuclear Sunset — radio caption EXPERIMENTAL OPTIONAL MOD\n\n"
        "This is a local offline staging copy of the VNV Mojave Radio Captions 0.4.2 technical preview.\n"
        "It is NOT installed automatically and TTW in-game behavior has NOT been tested.\n\n"
        "MO2 test procedure: copy only the mods/Nuclear Sunset - Radio Captions (Experimental) folder "
        "into the target MO2 mods folder, enable it after existing UI mods, and confirm "
        "UIO, xNVSE, JIP LN, JohnnyGuitar, ShowOff and other installed requirements.\n"
        "Use the original NVSE/Plugins/MojaveRadioCaptions.ini and default WorldRadioCaptions=false. "
        "Keep shared HUD XML files unchanged; UIO registers the prefab.\n"
        "The plugin reads the currently loaded INFO response text. "
        "For Korean speech captions, the underlying TTW and mod radio INFO records must already be Korean.\n"
        "External radio stations, FO3/TTW voice paths and songs may need separate runtime checks. "
        "It is not a full lyrics localization tool.\n"
        "Do not combine or redistribute the user-provided TTW KOR Radio + UI.esp with this preview "
        "without isolating game settings and scripts; that ESP contains thousands of unrelated records.\n"
        "When distributing under MIT, preserve LICENSE and THIRD_PARTY_NOTICES.md.\n"
    )
    (out/"README_OPTIONAL_RADIO.txt").write_text(note,encoding="utf-8")
    (out/"snapshot.json").write_text(json.dumps({"version":"0.4.2","mod":MOD_NAME,
        "installed":False,"technical_preview":True,"files":snapshots},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(out),"copied_files":len(snapshots),"dll_x86":True,
                      "source_data_included":False,"installed":False},ensure_ascii=False))
if __name__=="__main__":main()
