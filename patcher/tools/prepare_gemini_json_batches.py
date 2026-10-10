"""Prepare safe 4-lane JSON AI Translator batches from new-translation CSVs.

Never invokes a paid API or reads a credential. Original records/MO2 unchanged.
Inputs: staged 10_/01_신규번역_필요 CSVs. Outputs: 11_Gemini_JSON_번역대기
with JSON dictionaries and immutable per-key provenance.
"""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
W=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
SOURCE=W/"10_번역분리_신규와_기존상속"/"01_신규번역_필요"
OUT=W/"11_Gemini_JSON_번역대기"
LIMIT_STRINGS=60
LIMIT_CHARS=6500

def source_rows(file):
    with file.open(encoding="utf-8-sig",newline="") as fp:return list(csv.DictReader(fp))
def sanitized(name):return "".join(x if x.isalnum() or x in "-_." else "_" for x in name)
def checksum(string):return hashlib.sha256(string.encode("utf-8")).hexdigest()
def serialize(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def batches(rows):
    batch=[]; chars=0
    for item in rows:
        size=len(item["english_source"])
        if batch and (len(batch)>=LIMIT_STRINGS or chars+size>LIMIT_CHARS):
            yield batch
            batch=[];chars=0
        batch.append(item);chars+=size
    if batch:yield batch
def main():
    if OUT.exists():raise SystemExit("Destination exists; no overwrite: "+str(OUT))
    files=sorted(SOURCE.glob("*.csv"),key=lambda p:p.name.casefold())
    if len(files)!=204:raise RuntimeError("Expected 204 new-translation CSVs, found "+str(len(files)))
    manifest=[]
    items=0
    lane_load=[0,0,0,0]
    OUT.mkdir(parents=True)
    for f in files:
        rows=source_rows(f)
        source_name=f.name.removesuffix(".csv")
        for i,group in enumerate(batches(rows),1):
            lane=min(range(4),key=lambda n:(lane_load[n],n))
            lane_load[lane]+=sum(len(r["english_source"]) for r in group)
            base=f"{sanitized(source_name)}__{i:04d}"
            rel=f"project_{lane+1}/{base}.json"
            target=OUT/rel
            # No metadata in the translatable input JSON. Only values translated.
            document={}
            entries={}
            for j,row in enumerate(group):
                key=f"t{j+1:03d}"
                source=row["english_source"]
                if not source:raise RuntimeError("Empty source "+source_name)
                document[key]=source
                entries[key]={
                    "plugin":source_name,
                    "source_csv":f.relative_to(W).as_posix(),
                    "formid":row["formid"],
                    "origin_master":row["origin_master"],
                    "signature":row["signature"],
                    "field":row["field"],
                    "occurrence":row["occurrence"],
                    "english_sha256":checksum(source),
                    "english_text":source
                }
            serialize(target,document)
            serialize(OUT/"00_index"/(base+".index.json"),{"source_file":rel,"entries":entries})
            manifest.append({"source_file":rel,"index_file":"00_index/"+base+".index.json",
                             "project_lane":lane+1,"plugin":source_name,"rows":len(group),
                             "chars":sum(len(x) for x in document.values()),
                             "state":"INPUT_PREPARED_NOT_TRANSLATED"})
            items+=len(group)
    if items!=42021:raise RuntimeError("Expected 42021; actual "+str(items))
    serialize(OUT/"00_manifest.json",{"records":items,"batches":len(manifest),
                                     "project_lanes":4,"project_character_loads":lane_load,
                                     "files":manifest,"ready_for_release":False})
    prompt="""# Nuclear Sunset / Tale of Two Wastelands 번역 시스템 프롬프트 초안

기존에 사용하던 JSON AI Translator의 시스템 프롬프트가 있다면 그 프롬프트를 우선 사용하고, 아래 필수 보존 규칙만 추가한다.
영어 원문을 한국어로 한 번만 번역한다. 출력은 원본 JSON과 같은 key를 가진 JSON이어야 한다. 모든 key와 순서, 항목 수를 유지한다.
게임: Fallout: New Vegas + Fallout 3 (Tale of Two Wastelands), Nuclear Sunset 모드팩.
번역은 공식 세계관에 어울리는 자연스러운 한국어를 쓰고, UI/퀘스트/대사/아이템/스킬 등 용도에 맞춰 문체를 구분한다.
기존 번역 사전과 검수된 고유명사를 우선하며, 근거가 없는 임의의 신규 고유명사는 지양한다.
토큰과 제어문자(예: %s, %d, %1, {variable}, <br>, \\n, \\t), Script 명령·INI 키·FormID는 원문 그대로 보존한다.
영어 원문에 없는 설정이나 대사, 주어/성별/관계를 임의로 추가하지 않는다. 번역문 외의 해설·주석·마크다운은 쓰지 않는다.
단일 문장이라 문맥을 알 수 없을 때는 과도하게 의역하지 않는다. 모호성은 추후 문맥 검수에서 해결한다.
한국어 번역임에도 UI에 그대로 보여야 하는 태그, 플레이스홀더 및 수치 표기는 변경하지 않는다.
JSON의 키 이름을 한글화하지 않는다.
"""
    (OUT/"00_system_prompt_draft.md").write_text(prompt,encoding="utf-8")
    (OUT/"00_README.md").write_text(
        "# JSON AI Translator 번역 입력\n\n"
        "project_1~project_4: 4개 프로젝트로 번역량을 배분한 입력 JSON. 각자 등록된 Gemini 프로젝트에서 파일 값을 번역할 수 있음. "
        "**API 키는 이 폴더에 저장하거나 GitHub에 올리지 말 것.**\n\n"
        "00_index: FormID/필드/원문 SHA-256과 입력 키를 보관. 여기는 번역하지 말 것.\n\n"
        "00_manifest.json: 파일별 레코드 건수와 출처 및 예상 작업량. 모든 state는 미번역.\n\n"
        "00_system_prompt_draft.md: 임시 시스템 프롬프트. 사용 중인 JSON AI Translator의 원래 사용자 프롬프트에 보존 규칙만 추가하면 됨.\n\n"
        "번역 결과물은 각 원본 JSON과 key가 완전히 같아야 하며, 원본 source 값은 절대 덮어쓰지 말 것.\n\n"
        "AI 출력은 자동 승인하지 말고 기존 SST 용어·포맷 토큰·필드 구조·대사 문맥을 검수한 뒤에만 패쳐에 투입.\n",
        encoding="utf-8")
    print(json.dumps({"source_plugins":len(files),"translation_rows":items,
                      "json_batches":len(manifest),"project_character_loads":lane_load,
                      "output":str(OUT)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
