"""Offline QA for JSON AI Translator returned batches.

No Gemini key, SDK, or API requests. Does not modify source batches.
Usage: python tools/check_gemini_json_results.py
Save translations under 11_Gemini_JSON_번역대기/results/project_N/{input_stem}.translated.json.
"""
from collections import Counter,defaultdict
from pathlib import Path
import csv,hashlib,json,re
from translation_field_policy import skip_reason
ROOT=Path(__file__).resolve().parents[1]
W=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
BASE=W/"11_Gemini_JSON_번역대기"
PROTECTED=re.compile(r"<[^<>]{1,100}>|%[-+#0-9.]*[A-Za-z]|\{[^{}\r\n]{1,100}\}|\\[nrt]|\\x[0-9a-fA-F]{2}")
KOREAN=re.compile("[가-힣]")
ENGLISH=re.compile("[A-Za-z]{4,}")
COLUMNS=["project_lane","source_file","key","plugin","formid","origin_master",
         "signature","field","occurrence","english_source","korean_candidate",
         "qa_status","qa_notes","reviewed_korean_translation"]
def sha(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def validate_batch(job):
    src=BASE/job["source_file"]
    index=BASE/job["index_file"]
    file=Path(job["source_file"])
    dest=BASE/"results"/file.parent/(file.stem+".translated.json")
    if not dest.is_file():return "not_returned",[],[]
    try:
        input_json=json.loads(src.read_text(encoding="utf-8-sig"))
        translated=json.loads(dest.read_text(encoding="utf-8-sig"))
        meta=json.loads(index.read_text(encoding="utf-8"))["entries"]
    except (ValueError,KeyError) as e:
        return "json_parse_error",[],[repr(e)]
    if not isinstance(input_json,dict) or not isinstance(translated,dict):
        return "invalid_json_shape",[],["Root must be key-value JSON object"]
    if list(translated)!=list(input_json):
        return "id_or_order_changed",[],["Input/output JSON key order and identity differ"]
    if set(meta)!=set(input_json):
        return "index_mismatch",[],["Manifest row ids mismatch"]
    if any(not isinstance(v,str) for v in translated.values()):
        return "wrong_value_type",[],["Translated values must be all strings"]
    rows=[]
    problems=[]
    for key,source in input_json.items():
        m=meta[key]
        if m["english_sha256"]!=sha(source) or m["english_text"]!=source:
            return "source_hash_mismatch",[],["Input source diverged from immutable index"]
        result=translated[key]
        problems_for_row=[]
        if result=="":problems_for_row.append("EMPTY_TRANSLATION")
        if result==source:problems_for_row.append("UNCHANGED_SOURCE")
        if sorted(PROTECTED.findall(source))!=sorted(PROTECTED.findall(result)):
            problems_for_row.append("PROTECTED_TOKEN_MISMATCH")
        if source.count("\n")!=result.count("\n"):
            problems_for_row.append("NEWLINE_COUNT_CHANGED")
        if ENGLISH.search(source) and not KOREAN.search(result):
            problems_for_row.append("NO_HANGUL_CHECK")
        if len(source)>100 and len(result)<max(5, len(source)//8):
            problems_for_row.append("SUSPICIOUSLY_SHORT")
        reason=skip_reason(m["signature"],m["field"],source)
        if reason:
            # Explicitly prevent accepting AI translations of engine metadata.
            status="SKIP_NON_DISPLAY"
            problems_for_row=[]
        else:
            status="REVIEW_REQUIRED" if problems_for_row else "READY_FOR_HUMAN_QA"
        if problems_for_row:problems.append({"key":key,"checks":problems_for_row})
        rows.append({"project_lane":job["project_lane"],"source_file":job["source_file"],
                     "key":key,"plugin":m["plugin"],"formid":m["formid"],
                     "origin_master":m["origin_master"],"signature":m["signature"],
                     "field":m["field"],"occurrence":m["occurrence"],
                     "english_source":source,"korean_candidate":"" if reason else result,
                     "qa_status":status,"qa_notes":reason if reason else ";".join(problems_for_row),
                     "reviewed_korean_translation":""})
    return "verified_structure",rows,problems
def main():
    info=json.loads((BASE/"00_manifest.json").read_text(encoding="utf-8"))
    reports=[]
    reviewed=[]
    stats=Counter()
    for job in info["files"]:
        state,rows,issues=validate_batch(job)
        stats[state]+=1
        stats["output_rows"]+=len(rows)
        stats["skipped_non_display_rows"]+=sum(r["qa_status"]=="SKIP_NON_DISPLAY" for r in rows)
        stats["ready_human_review_rows"]+=sum(r["qa_status"]=="READY_FOR_HUMAN_QA" for r in rows)
        stats["flagged_rows"]+=len(issues)
        reports.append({"file":job["source_file"],"state":state,
                        "rows":len(rows),"review_flag_count":len(issues),
                        "issues":issues[:30]})
        reviewed.extend(rows)
    resultdir=BASE/"04_결과_검수"
    if resultdir.exists():
        for version in range(1,10000):
            candidate=BASE/("04_결과_검수_%03d"%version)
            if not candidate.exists():
                resultdir=candidate
                break
        else:raise SystemExit("Too many QA snapshots")
    resultdir.mkdir()
    with (resultdir/"검수대기_후보.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS)
        writer.writeheader();writer.writerows(reviewed)
    dump(resultdir/"배치검증현황.json",{"stats":dict(stats),"batches":reports})
    print(json.dumps({"total_input_batches":info["batches"],
                      "received_valid_batches":stats["verified_structure"],
                      "translated_value_rows":stats["output_rows"],
                      "needs_review":stats["flagged_rows"],
                      "unreturned_batches":stats["not_returned"],
                      "report":str(resultdir)},ensure_ascii=False))
if __name__=="__main__":main()
