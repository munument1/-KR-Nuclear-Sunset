"""Prepare a portable optional Nuclear Sunset tNVSE Korean font mod locally.

Do not install to MO2 or game. Includes the VNV Korean UI-fixed tNVSE DLL as an overlay;
the user's separately installed original tNVSE must remain unchanged.
"""
from pathlib import Path
import hashlib,json,shutil,re,xml.etree.ElementTree as ET
SOURCE=Path(r"D:\Codex_Trans\비바 뉴 베가스\bundles\sst-release-20261006\font-payloads")
OUT=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\13_tNVSE_Korean_Fonts_Staging_20261010")
MOD="Nuclear Sunset - Korean Fonts for tNVSE"
VNV_KOREAN_PLUGIN=Path(r"C:\Modlists\VNV\mods\VNV Korean Fonts - tNVSE\NVSE\plugins")
VNV_FIXED_DLL_SHA256="AD2A81F1440647919BA792F0216ED26A736D4C4A51777F875E85E270538B3D70"
VNV_DLL_EXTRA=(
    ("tnvse.dll","NVSE/plugins/tnvse.dll"),
    ("fonts/licenses/tNVSE-GPL-3.0.txt","NVSE/plugins/fonts/licenses/tNVSE-GPL-3.0.txt"),
    ("fonts/licenses/tNVSE-KR-UI-fix.txt","NVSE/plugins/fonts/licenses/tNVSE-KR-UI-fix.txt"),
    ("fonts/licenses/tNVSE-71-KR-UI-source.zip","NVSE/plugins/fonts/licenses/tNVSE-71-KR-UI-source.zip"),
)
FONTS=("Pretendard-Bold.ttf","NanumSquareEB.ttf","NeoDunggeunmoPro-Regular.ttf","TmonMonsorI.ttf")
NOTICES=("FONT_SOURCES.txt","Pretendard-LICENSE.txt","NAVER-font-license.html",
         "NeoDunggeunmoPro-LICENSE.txt","TMON-author-license.html","TMON-license-notice.html")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if OUT.exists():raise RuntimeError("Output already exists")
    files=("tnvse.ini","tnvse_fonts.xml")+FONTS+NOTICES
    for name in files:
        if not (SOURCE/name).is_file():raise FileNotFoundError(SOURCE/name)
    root=ET.parse(SOURCE/"tnvse_fonts.xml").getroot()
    fonts=root.findall(".//fonts/font")
    slots=[int(x.attrib["id"]) for x in fonts]
    if len(slots)!=len(set(slots)) or set(slots)!={1,2,3,4,5,6,7,8,42}:
        raise RuntimeError("Unexpected VNV font slots")
    face_paths=set()
    for elem in root.iter():
        if elem.tag not in ("face","fallback"):continue
        p=(elem.attrib.get("path") or "").replace("\\","/")
        prefix="Data/NVSE/plugins/fonts/"
        if not p.startswith(prefix):raise RuntimeError("Unexpected path "+p)
        face_paths.add(p[len(prefix):])
    if face_paths!=set(FONTS):raise RuntimeError("Font file references differ")
    ini=(SOURCE/"tnvse.ini").read_text(encoding="utf-8-sig")
    for key,value in {"bEnableFreeTypeFontRendering":"1","bEnableMultibyteFontHook":"1",
                      "uiEncoding":"4","bUTF8":"1","bEnableDictionaryTranslation":"0"}.items():
        match=re.search(r"(?m)^\s*"+re.escape(key)+r"\s*=\s*(\S+)",ini)
        if not match or match.group(1)!=value:raise RuntimeError("Unexpected INI "+key)
    output=OUT/"mods"/MOD
    manifest=[]
    for name in files:
        dest=(Path("NVSE/plugins/fonts")/name if name in FONTS else
              Path("NVSE/plugins")/name if name in {"tnvse.ini","tnvse_fonts.xml"} else
              Path("LICENSES")/name)
        p=output/dest
        p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(SOURCE/name,p)
        if sha(p)!=sha(SOURCE/name):raise RuntimeError("SHA check failed "+name)
        manifest.append({"file":dest.as_posix(),"sha256":sha(p),"bytes":p.stat().st_size})
    for src_relative,dest_relative in VNV_DLL_EXTRA:
        original=VNV_KOREAN_PLUGIN/src_relative
        if not original.is_file():raise FileNotFoundError(original)
        if src_relative=="tnvse.dll" and sha(original).upper()!=VNV_FIXED_DLL_SHA256:
            raise RuntimeError("VNV tNVSE KR fix DLL version mismatch")
        dest=output/dest_relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(original,dest)
        if sha(dest)!=sha(original):raise RuntimeError("DLL/notice copy mismatch")
        manifest.append({"file":dest_relative,"sha256":sha(dest),"bytes":dest.stat().st_size})
    (OUT/"manifest.json").write_text(json.dumps({
        "mod":MOD,"source":"VNV sst-release-20261006",
        "slots":slots,"font_files":len(FONTS),"tnvse_binary_included":True,"corresponding_source_included":True,
        "installed":False,"files":manifest},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"README_KO.md").write_text(
        "# Nuclear Sunset: tNVSE Korean Fonts (test mod)\n\n"
        "- Upstream tNVSE is expected; VNV Korean UI fixed DLL is INCLUDED to override its DLL by MO2 priority.\n"
        "- The mod holds VNV tuned tnvse.ini (UTF-8 + FreeType + multibyte), tnvse_fonts.xml, and four fonts.\n"
        "- Install as a regular MO2 mod with priority AFTER existing tNVSE Default Config, if testing manually.\n"
        "- Existing tnvse_dictionary.xml and tNVSE binary are not modified.\n"
        "- Font notices are in LICENSES; GPL-3.0 license and corresponding modified tNVSE source ZIP accompany the fixed DLL.\n"
        "- The default font settings change UI slots 1-8,42; TTW and Nuclear Sunset UI need runtime tests.\n"
        "- Do not publish or enable by default until confirmed in game; check third-party redistribution terms.\n",
        encoding="utf-8")
    print(json.dumps({"staged_mod":MOD,"files":len(manifest),"slots":slots,
                      "installed":False,"tnvse_binary_included":True},ensure_ascii=False))
if __name__=="__main__":main()
