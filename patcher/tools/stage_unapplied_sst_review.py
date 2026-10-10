"""Add direct-SST not-applied candidate review worksheets to local translation workspace.

This does not claim every unused SST row is actually untranslated in game.
It compares exact row identity with native XEditLib changed field records.
"""
from pathlib import Path
from collections import Counter
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
DEST=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
EVIDENCE=ROOT/".local"

def key(r):
    return tuple(str(r.get(k,"")).casefold() for k in
                 ("owner","id","signature","field","source","dest"))

def apply_for(plugin):
    lc=plugin.casefold()
    if lc in ("autumnleaves.esp","ziontrail.esm"):
        root=EVIDENCE/"native-validation-20261010-v2"/Path(plugin).stem
    elif lc=="thepitt.esm":
        root=EVIDENCE/"native-validation-thepitt-20261010"/"thepitt"
    else:
        root=EVIDENCE/"native-plugin-batch-20261010"/plugin.lower().replace(".esm","").replace(".esp","").replace(" ","_")
    path=root/"apply.json"
    if not path.is_file():raise FileNotFoundError(path)
    data=json.loads(path.read_text(encoding="utf-8"))
    files=data["files"]
    if len(files)!=1 or files[0]["plugin"].casefold()!=lc:
        raise RuntimeError("Wrong native evidence target "+plugin)
    return files[0]

def main():
    if not DEST.is_dir():raise SystemExit("Workspace not staged yet")
    entries=nskr.read_json(CATALOG)["files"]
    direct=[e for e in entries if e.get("kind")=="plugin-records"]
    if len(direct)!=38:raise RuntimeError("Expected 38 direct SST entries")
    out=DEST/"07_기존SST_미적용후보_추가검수"
    if out.exists():raise SystemExit("Output exists, will not overwrite")
    out.mkdir()
    cols=["owner","id","signature","field","path","english_source","current_korean_candidate",
          "status","replacement_translation","notes"]
    totals=Counter()
    manifest=[]
    for e in direct:
        name=e["path"]
        applied=apply_for(name)
        mapped={key(r) for r in applied["changed"]}
        unused=[r for r in e["mappings"] if key(r) not in mapped]
        path=out/(name+".csv")
        with path.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
            for r in unused:
                w.writerow({
                    "owner":r["owner"],"id":r["id"],"signature":r["signature"],
                    "field":r["field"],"path":r["path"],
                    "english_source":r["source"],
                    "current_korean_candidate":r["dest"],
                    "status":"미적용_후보_필드경로원문대조필요",
                    "replacement_translation":"","notes":""})
        manifest.append({"plugin":name,"sst_candidate_rows":len(e["mappings"]),
                         "applied_field_instances":len(applied["changed"]),
                         "unique_changed_keys":len(mapped),
                         "not_applied_candidate_rows":len(unused),
                         "csv":path.relative_to(DEST).as_posix()})
        totals["not_applied_rows"]+=len(unused)
        totals["applied_native_field_instances"]+=len(applied["changed"])
    with (DEST/"00_기존SST_추가검수_목록.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=manifest[0]);w.writeheader();w.writerows(manifest)
    # Prioritize new-translation records (per-source subrecords; not confirmed visible).
    with (DEST/"00_플러그인_대상목록.csv").open("r",encoding="utf-8-sig",newline="") as f:
        staging=list(csv.DictReader(f))
    priority=sorted(staging,key=lambda r:int(r["need_new_translation"]),reverse=True)
    with (DEST/"00_번역우선순위_TOP50.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["plugin","need_new_translation","base_fallback_candidates","category","english_csv"])
        w.writeheader()
        w.writerows({k:row[k] for k in w.fieldnames} for row in priority[:50])
    more={"direct_sst_unapplied_candidates":totals["not_applied_rows"],
          "direct_sst_applied_fields":totals["applied_native_field_instances"],
          "direct_sst_plugins_with_review_worksheets":len(manifest),
          "note":"Unused mapping candidates are NOT equal to game-visible untranslated strings."}
    (out/"검수현황.json").write_text(json.dumps({"summary":more,"files":manifest},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    p=DEST/"00_먼저읽기.md"
    existing=p.read_text(encoding="utf-8")
    existing+=("\n## 기존 SST 적용 누락 후보\n\n"
               "07_기존SST_미적용후보_추가검수 폴더에는 실제 native apply.json과 SST 매핑을 비교하여 "
               "적용 기록에 없던 후보 원문과 기존 한국어 번역을 CSV로 모았습니다.\n"
               "이 후보는 필드 경로/원문 변경이나 중복으로 실제 재검토가 필요하지만, "
               "반드시 게임에서 영문으로 노출되는 항목과 1:1로 대응하지 않습니다.\n"
               "00_번역우선순위_TOP50.csv에 신규 번역 필요 후보가 많은 플러그인을 따로 정리했습니다.\n")
    p.write_text(existing,encoding="utf-8")
    print(json.dumps(more,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
