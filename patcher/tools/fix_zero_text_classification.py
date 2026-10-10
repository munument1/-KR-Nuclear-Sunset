"""Correct two stale zero-text audit classifications after re-extraction."""
from pathlib import Path
import csv,json,shutil,hashlib
WORK=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
TARGETS={"capital ruins for ttw.esp","neutralweathers_ttw.esp"}
DEST_CATEGORY="01_신규번역_전용SST없음"

def load(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(path,records,cols):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(records)

def main():
    file=WORK/"00_플러그인_대상목록.csv"
    recs=load(file)
    if len(recs)!=204:raise RuntimeError("Expected 204 pending translations")
    identified={r["plugin"].casefold():r for r in recs}
    if not TARGETS.issubset(identified):raise RuntimeError("Missing targets")
    for key in TARGETS:
        r=identified[key]
        if not r["category"].startswith("04_") or int(r["need_new_translation"])<1:
            raise RuntimeError("Not misclassified as zero-text "+key)
        for kind in ("copied_plugin","english_csv"):
            original=WORK/r[kind]
            destination=WORK/DEST_CATEGORY/Path(r[kind]).parent.name/Path(r[kind]).name
            if not original.is_file() or destination.exists():
                raise RuntimeError("Unsafe copy/move "+str(original))
    for key in TARGETS:
        r=identified[key]
        for kind in ("copied_plugin","english_csv"):
            original=WORK/r[kind]
            destination=WORK/DEST_CATEGORY/Path(r[kind]).parent.name/Path(r[kind]).name
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(original),str(destination))
            r[kind]=destination.relative_to(WORK).as_posix()
        r["category"]=DEST_CATEGORY
    columns=list(recs[0])
    write(file,recs,columns)
    priority=["plugin","need_new_translation","base_fallback_candidates","category","english_csv"]
    sorted_rows=sorted(recs,key=lambda r:int(r["need_new_translation"]),reverse=True)
    write(WORK/"00_번역우선순위_TOP50.csv",[{c:r[c] for c in priority} for r in sorted_rows[:50]],priority)
    path=WORK/"00_작업현황.json"
    summary=json.loads(path.read_text(encoding="utf-8"))
    summary["categories"][DEST_CATEGORY]=159
    summary["categories"]["04_표시영문없음_별도확인"]=0
    summary["misclassified_zero_visible_corrected"]=2
    path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    note=WORK/"00_먼저읽기.md"
    text=note.read_text(encoding="utf-8")
    text=text.replace("그 외 플러그인 214개의 승리 공급자 ESP/ESM과 각각의 영문 추출 CSV를 저장했습니다.",
                      "최초 214개를 수집했으며, 현재 204개는 일반 레코드 번역·검수 대기 대상입니다.")
    text+="\n표시 영문 0개로 잘못 분류됐던 Capital Ruins for TTW와 NeutralWeathers_TTW는 재검사에서 영문 원문 후보가 나와 01 그룹으로 재분류했습니다.\n"
    note.write_text(text,encoding="utf-8")
    if any(not (WORK/r["copied_plugin"]).is_file() or not (WORK/r["english_csv"]).is_file() for r in recs):
        raise RuntimeError("Broken source path")
    print(json.dumps({"remaining":len(recs),"new_translation_group":159,
                      "fallback_review_group":44,
                      "no_match_group":1,"zero_text_pending":0,
                      "exclusions":{"native_inherited":4,"no_display_text":6},
                      "corrected":[identified[x]["plugin"] for x in TARGETS]},ensure_ascii=False))
if __name__=="__main__":main()
