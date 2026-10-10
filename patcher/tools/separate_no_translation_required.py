"""Separates safe exclusions from manual record-translation queue.

Local staged copies only, no MO2 mutation; scripts and external UI still need audit.
"""
from pathlib import Path
import csv,hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
EVIDENCE=ROOT/".local"/"native-full-fallback-candidates-20261010"/"summary.json"
INHERITED={
    "sstfevgrowths.esm","theplatinumvault.esm",
    "interiors improved - tops hotel.esp","sierra madre suite windows.esp"
}
NO_DISPLAY={
    "main and pause menus overhaul.esm","dsjipcccanims.esp",
    "vanilla ui plus.esp","immersivepickupsoundsremastered.esp",
    "illuminatedvillabuildingsonly.esp","uranium haze piplight.esp"
}
A="08_기존SST_상속완료_번역대기제외"
B="09_레코드표시문구없음_스크립트UI확인"

def load(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def save(path,rows,columns):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while block:=f.read(1048576):h.update(block)
    return h.hexdigest()

def main():
    approved={r["plugin"].casefold():r for r in json.loads(EVIDENCE.read_text(encoding="utf-8"))}
    if set(approved)!=INHERITED:raise RuntimeError("Missing full inherited validations")
    if any(r["status"]!="PASS" or r["applied"]!=r["fallback_candidate_rows"] for r in approved.values()):
        raise RuntimeError("One inherited candidate failed validation")
    manifest=WORK/"00_플러그인_대상목록.csv"
    rows=load(manifest)
    if len(rows)!=214:raise RuntimeError("Unexpected manifest; no changes made")
    ids={r["plugin"].casefold():r for r in rows}
    if not (INHERITED|NO_DISPLAY)<=set(ids):raise RuntimeError("Missing source plugin")
    if len(INHERITED|NO_DISPLAY)!=10:raise RuntimeError("Bad expected exclusion count")
    for name in INHERITED:
        item=ids[name]
        n=int(item["english_fields"])
        if n==0 or int(item["need_new_translation"])!=0 or n!=int(item["base_fallback_candidates"]) or n!=approved[name]["applied"]:
            raise RuntimeError("Uncovered inherited text "+name)
    for name in NO_DISPLAY:
        item=ids[name]
        if int(item["english_fields"])!=0 or int(item["need_new_translation"])!=0:
            raise RuntimeError("English display fields exist "+name)
        if int(item["total_records"])<=0:
            raise RuntimeError("Unexpected zero-record category "+name)
    moves=[]
    for name in sorted(INHERITED|NO_DISPLAY):
        item=ids[name]
        group=A if name in INHERITED else B
        for field in ("copied_plugin","english_csv"):
            source=WORK/item[field]
            target=WORK/group/Path(item[field]).name
            if not source.is_file() or target.exists():raise RuntimeError("Missing source or target collision: "+str(source))
            if field=="copied_plugin" and sha(source)!=item["sha256"]:
                raise RuntimeError("Source SHA mismatch "+name)
            moves.append((source,target))
    for source,target in moves:
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(source),str(target))
    remaining=[]
    by_type={A:[],B:[]}
    for row in rows:
        key=row["plugin"].casefold()
        if key not in INHERITED and key not in NO_DISPLAY:
            remaining.append(row);continue
        group=A if key in INHERITED else B
        row=row.copy()
        row["category"]=group
        for field in ("copied_plugin","english_csv"):
            row[field]=(Path(group)/Path(row[field]).name).as_posix()
        by_type[group].append(row)
    cols=list(rows[0])
    save(manifest,remaining,cols)
    save(WORK/"00_기존SST상속완료_검증목록.csv",by_type[A],cols)
    save(WORK/"00_표시문구없음_UI스크립트확인목록.csv",by_type[B],cols)
    topcols=["plugin","need_new_translation","base_fallback_candidates","category","english_csv"]
    sorted_rows=sorted(remaining,key=lambda r:int(r["need_new_translation"]),reverse=True)
    save(WORK/"00_번역우선순위_TOP50.csv",[{x:r[x] for x in topcols} for r in sorted_rows[:50]],topcols)
    p=WORK/"00_작업현황.json"
    summary=json.loads(p.read_text(encoding="utf-8"))
    summary.update({
        "initial_staged_plugin_sources":214,
        "staged_untranslated_plugin_sources":len(remaining),
        "excluded_full_fallback_native_verified":4,
        "excluded_no_plugin_display_string":6,
        "excluded_full_fallback_applied_fields":sum(int(r["applied"]) for r in approved.values()),
        "english_source_fields":sum(int(r["english_fields"]) for r in remaining),
        "need_new_translation":sum(int(r["need_new_translation"]) for r in remaining),
        "base_fallback_candidates":sum(int(r["base_fallback_candidates"]) for r in remaining),
        "copied_plugin_total_MB":round(sum(int(r["bytes"]) for r in remaining)/1048576,1)
    })
    summary["categories"]["02_기본번역_상속검수"]=44
    summary["categories"]["04_표시영문없음_별도확인"]=2
    summary["categories"][A]=4
    summary["categories"][B]=6
    summary["warning"]+=" 09 group may have script/MCM/UI strings; only ordinary ESP record translation excluded."
    p.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    readme=WORK/"00_먼저읽기.md"
    with readme.open("a",encoding="utf-8") as f:
        f.write("\n\n## 레코드 번역 제외 파일\n")
        f.write("08: 전용 SST 없이 기존 FalloutNV/FO3/DLC 번역 상속으로 감지한 표시 원문 8건이 전부 적용/재로드 검증된 4개 파일. 다른 UI나 스크립트 문자열은 별도 확인.\n")
        f.write("09: 6개 플러그인에 레코드가 있으나 추출 가능한 영문 표시 문자열이 없어 일반 ESP 레코드 번역 대상에서 분리. 스크립트와 외부 UI는 별도 확인.\n")
        f.write("04에 남은 2개는 재검사상 영문 후보가 있으므로 작업 대기에 유지.\n")
    for item in remaining+by_type[A]+by_type[B]:
        if not (WORK/item["copied_plugin"]).is_file() or not (WORK/item["english_csv"]).is_file():
            raise RuntimeError("File missing after move "+item["plugin"])
    print(json.dumps({
        "pending_manual_record_review":len(remaining),
        "native_full_inheritance_excluded":4,
        "no_detected_display_text_excluded":6,
        "excluded_for_record_translation":10,
        "remaining_new_text_candidates":summary["need_new_translation"],
        "remaining_inherited_candidates":summary["base_fallback_candidates"],
        "excluded_names":{A:[r["plugin"] for r in by_type[A]],B:[r["plugin"] for r in by_type[B]]}
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
