"""Stage untranslated Nuclear Sunset MO2 plugins and source-text CSVs in one local folder.

Do NOT commit the generated work folder: it contains copyrighted mod/game records.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
from nskr_output import base_translation_memory
from tools.tes4_text_scan import plugin_records,masters,clean_text,HANGUL,ENGLISH,DISPLAY_FIELDS

MO2=Path(r"C:\Modlists\NuclearSunset")
DEST=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
AUDIT=ROOT/".local"/"plugin-audit"/"full-audit.json"
CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
CATS={
    "own_text_without_sst":"01_신규번역_전용SST없음",
    "override_fallback_candidates":"02_기본번역_상속검수",
    "no_sst_no_identified_translation":"03_사전매칭없음_검토",
    "no_detected_english_text":"04_표시영문없음_별도확인"
}
CSV_COLS=["formid","origin_master","signature","field","occurrence","english_source",
          "status","existing_korean_candidate","korean_translation","context_note"]
MANIFEST_COLS=["plugin","category","mo2_provider","original_path","copied_plugin",
               "english_csv","sha256","bytes","english_fields",
               "need_new_translation","base_fallback_candidates","total_records"]

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while chunk:=f.read(1<<20):h.update(chunk)
    return h.hexdigest()

def writer(path,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    f=path.open("w",encoding="utf-8-sig",newline="")
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    return f,w

def relative(path):
    return path.relative_to(DEST).as_posix()

def dictionary(catalog):
    found=defaultdict(set)
    for row in base_translation_memory(catalog):
        if not row.get("path"):continue
        key=(row["owner"].casefold(),row["id"].casefold(),row["signature"],row["field"],row["source"])
        found[key].add(row["dest"])
    return {k:next(iter(values)) for k,values in found.items() if len(values)==1}

def write_plugin_csv(file,plugin,output,memory):
    names=masters(file)
    counts=Counter()
    f,w=writer(output,CSV_COLS)
    with f:
        for fid,sig,fields in plugin_records(file):
            counts["total_records"]+=1
            ix=fid>>24
            if ix>len(names):
                counts["owner_missing"]+=1
                continue
            owner=(names[ix] if ix<len(names) else plugin).casefold()
            repeated=Counter()
            for field,raw in fields:
                occurrence=repeated[field]
                repeated[field]+=1
                if field not in DISPLAY_FIELDS:continue
                value=clean_text(raw,"utf-8") or clean_text(raw,"cp1252")
                if not value or HANGUL.search(value) or not ENGLISH.search(value):continue
                match=memory.get((owner,f"{fid&0xffffff:06x}",sig,field,value),"")
                status="기존번역_상속후보_경로검증필요" if match else "신규번역_필요"
                w.writerow({"formid":f"{fid:08X}","origin_master":owner,
                             "signature":sig,"field":field,"occurrence":occurrence,
                             "english_source":value,"status":status,
                             "existing_korean_candidate":match,
                             "korean_translation":"","context_note":""})
                counts["english_fields"]+=1
                counts["base_fallback_candidates" if match else "need_new_translation"]+=1
    return counts

def main():
    if DEST.exists():raise SystemExit("Destination exists. Refusing overwrite: "+str(DEST))
    installation=nskr.Installation(MO2)
    old=nskr.read_json(AUDIT)
    cat=nskr.read_json(CATALOG)
    direct={e["path"].casefold() for e in cat["files"] if e.get("kind")=="plugin-records"}
    assert len(installation.active)==252 and len(old["plugins"])==252 and len(direct)==38
    assert cat.get("translation_ready") is False
    print("PREPARING_BASE_MEMORY",flush=True)
    memory=dictionary(cat)
    print("MATCH_KEYS",len(memory),flush=True)
    DEST.mkdir(parents=True)
    written=[];grouped=Counter()
    for data in old["plugins"]:
        name=data["plugin"]
        if name.casefold() in direct:continue
        group=CATS[data["category"]]
        source=installation.source(name)
        copied=DEST/group/"원본_ESP_ESM"/name
        copied.parent.mkdir(parents=True,exist_ok=True)
        if copied.exists():raise RuntimeError("Collision: "+name)
        shutil.copy2(source,copied)
        original_hash=sha(source)
        if sha(copied)!=original_hash:raise RuntimeError("Copy corrupted: "+name)
        csvfile=DEST/group/"번역용_원문_CSV"/(name+".csv")
        values=write_plugin_csv(source,name,csvfile,memory)
        grouped[group]+=1
        written.append({"plugin":name,"category":group,
                        "mo2_provider":installation.providers[name.casefold()][-1]["provider"],
                        "original_path":str(source),"copied_plugin":relative(copied),
                        "english_csv":relative(csvfile),"sha256":original_hash,
                        "bytes":source.stat().st_size,
                        "english_fields":values["english_fields"],
                        "need_new_translation":values["need_new_translation"],
                        "base_fallback_candidates":values["base_fallback_candidates"],
                        "total_records":values["total_records"]})
        if len(written)%30==0:print("COLLECTED",len(written),"/",252-len(direct),flush=True)
    ui=[]
    for key,providers in installation.providers.items():
        mcm=key.startswith("mcm/") and key.endswith(".json")
        trans_ini=(key.endswith(".ini") and
                   (key.startswith("mcm/translations/") or key.startswith("interface/translations/") or
                    key.startswith("config/") and "translation" in Path(key).name))
        if not (mcm or trans_ini):continue
        chosen=providers[-1]
        source=Path(chosen["physical"])
        dest=DEST/("05_MCM_JSON" if mcm else "06_Translations_INI")/Path(chosen["path"])
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest)
        if sha(source)!=sha(dest):raise RuntimeError("UI asset corrupted: "+key)
        ui.append({"kind":"MCM JSON" if mcm else "Translations INI",
                   "virtual_path":chosen["path"],"provider":chosen["provider"],
                   "copied_file":relative(dest)})
    f,w=writer(DEST/"00_플러그인_대상목록.csv",MANIFEST_COLS)
    with f:w.writerows(written)
    f,w=writer(DEST/"00_MCM_번역대상목록.csv",["kind","virtual_path","provider","copied_file"])
    with f:w.writerows(ui)
    summary={
       "active_plugins":252,"direct_sst_plugin_sources_not_duplicated":len(direct),
       "staged_untranslated_plugin_sources":len(written),
       "categories":dict(grouped),
       "english_source_fields":sum(x["english_fields"] for x in written),
       "need_new_translation":sum(x["need_new_translation"] for x in written),
       "base_fallback_candidates":sum(x["base_fallback_candidates"] for x in written),
       "MCM_JSON":sum(x["kind"]=="MCM JSON" for x in ui),
       "Translations_INI":sum(x["kind"]=="Translations INI" for x in ui),
       "copied_plugin_total_MB":round(sum(x["bytes"] for x in written)/1048576,1),
       "workspace":str(DEST),
       "warning":"LOCAL ONLY; source game/mod plugins are NOT for redistribution or automatic game installation"
    }
    (DEST/"00_작업현황.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    notes=[
      "# Nuclear Sunset 미번역/검수 작업 묶음","",
      "이 폴더는 번역 작업을 위한 안전한 로컬 사본입니다. 게임에 바로 설치하지 마세요.","",
      "게임에 설치된 MO2 원본 파일은 수정하지 않았습니다.",
      "전용 SST가 이미 있는 38개 플러그인은 기존 번역 프로젝트에 있으므로 중복 복사하지 않았습니다.",
      "그 외 플러그인 214개의 승리 공급자 ESP/ESM과 각각의 영문 추출 CSV를 저장했습니다.","",
      "01: 신규 번역 필요 / 전용 SST 없음.",
      "02: 본편/DLC 번역 상속 가능성이 있어 추가 검수 필요.",
      "03: 사전이 매칭되지 않은 원문 검토.",
      "04: 플러그인 내부 표시 영문 미탐지, 별도 UI/스크립트 확인.",
      "05: MCM JSON (실제 상대경로 보존).",
      "06: Translations INI (실제 상대경로 보존).","",
      "각 폴더의 번역용_원문_CSV에서 english_source를 보고 korean_translation에 번역을 작성하세요.",
      "existing_korean_candidate는 이미 존재하는 번역 사전에서 유일하게 매칭된 값이며, 실제 플러그인 경로 검증 전에는 참고로만 사용해야 합니다.",
      "번역 CSV는 원문 필드 후보 목록입니다. 즉 영문 후보 전체가 게임에 표시되는 텍스트는 아닙니다.",
      "사전이 없는 파일에도 본편 번역이 상속 가능한 필드가 있으므로 해당 항목을 무턱대고 전부 재번역하지 마세요.",
      "기존 SST가 있는 38개 플러그인에서 일부 적용되지 않은 텍스트는 별도 검수 대상입니다.","",
      "저작권과 원본 모드 라이선스를 고려해 ESP/ESM, 추출 원문, 번역 데이터 자체는 GitHub에 업로드하지 않습니다.",
      "최종 적용은 원문 매칭 및 xEditLib 검증 후 Nuclear Sunset 패쳐에서 진행해야 합니다.",""
    ]
    (DEST/"00_먼저읽기.md").write_text("\n".join(notes),encoding="utf-8")
    print("FINISHED",json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
