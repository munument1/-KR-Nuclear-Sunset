"""Split local 204-plugin English source CSVs into actionable translation queues.

1) brand-new text with NO dictionary match
2) SST inheritance awaiting native proof (never blindly fill as translated)
3) native-verified inherited fields from isolated XEditLib apply logs

No original CSVs, plugins, or MO2 installations are modified.
"""
import csv,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
OLD=ROOT/".local"/"native-fallback-smoke-20261010-v2"
NEW=ROOT/".local"/"inherited-manual-batch-20261010"
DEST=WORK/"10_번역분리_신규와_기존상속"
COLS=["plugin","formid","origin_master","signature","field","occurrence",
      "english_source","existing_korean_candidate","korean_translation",
      "verification_status","source_csv","notes"]
STATS=["plugin","total_english_fields","new_translation","inherited_verified",
       "inherited_awaiting_native_test","ambiguous_duplicate_source_fields",
       "native_apply_tested"]
def loadcsv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def writecsv(path,rows,cols):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(rows)
def evidence_path(name):
    k=name.casefold()
    previous={x.casefold() for x in (
       "NS.esm","NS.esp","BraveNewWorld.esm",
       "TTW Dialogue and Interactions Expansion Overhaul.esp")}
    if k in previous:
        return OLD/(k.replace(".","_").replace(" ","_"))/"apply.json"
    return NEW/(k.replace(".","_").replace(" ","_").replace("/","_"))/"apply.json"
def changed_keys(name):
    path=evidence_path(name)
    if not path.is_file():return None
    obj=json.loads(path.read_text(encoding="utf-8"))
    files=obj.get("files",[])
    if len(files)!=1 or files[0].get("plugin","").casefold()!=name.casefold():
        raise RuntimeError("Wrong apply proof for "+name)
    changed=defaultdict(set)
    for r in files[0].get("changed",[]):
        if r.get("mappingOrigin")!="base_dlc_sst_fallback":continue
        k=(r["owner"].casefold(),r["id"].casefold(),
           r["signature"],r["field"],r["source"])
        changed[k].add(r["dest"])
    return changed
def field_key(r):
    return (r["origin_master"].casefold(),r["formid"][-6:].casefold(),
            r["signature"],r["field"],r["english_source"])
def main():
    manifest=loadcsv(WORK/"00_플러그인_대상목록.csv")
    if len(manifest)!=204:raise RuntimeError("Expected 204 pending")
    if DEST.exists():raise SystemExit("Destination exists, do not overwrite")
    # Examine every source before creating any output.
    work=[]
    for row in manifest:
        csvfile=WORK/row["english_csv"]
        if not csvfile.is_file():raise RuntimeError("Missing source CSV "+str(csvfile))
        raw=loadcsv(csvfile)
        if len(raw)!=int(row["english_fields"]):raise RuntimeError("CSV source count changed "+row["plugin"])
        work.append((row,csvfile,raw))
    DEST.mkdir(parents=True)
    allsummary=[]
    totals=Counter()
    for info,source,records in work:
        name=info["plugin"]
        changed=changed_keys(name)
        freq=Counter(field_key(r) for r in records)
        outputs=defaultdict(list)
        counts=Counter()
        for row in records:
            rec={**row,"plugin":name,
                 "source_csv":source.relative_to(WORK).as_posix()}
            if not row.get("existing_korean_candidate"):
                bucket="01_신규번역_필요"
                rec["verification_status"]="NO_KNOWN_SST_MATCH"
                counts["new_translation"]+=1
            else:
                key=field_key(row)
                candidates=changed.get(key,set()) if changed is not None else set()
                if len(candidates)==1 and row["existing_korean_candidate"] in candidates and freq[key]==1:
                    bucket="03_상속번역_적용검증완료"
                    rec["verification_status"]="NATIVE_APPLY_AND_READBACK_PASS"
                    counts["inherited_verified"]+=1
                else:
                    bucket="02_상속번역_검증대기"
                    rec["verification_status"]="NEEDS_NATIVE_PROOF_OR_FIELD_PATH_REVIEW"
                    if freq[key]>1:
                        rec["verification_status"]="REPEATED_SUBRECORD_NEEDS_PATH_REVIEW"
                        counts["ambiguous_duplicate_source_fields"]+=1
                    counts["inherited_awaiting_native_test"]+=1
                # Never treat a candidate as accepted final translation text
                rec["korean_translation"]=""
            outputs[bucket].append(rec)
        for bucket,entries in outputs.items():
            if not entries:continue
            f=DEST/bucket/(name+".csv")
            writecsv(f,entries,COLS)
        stat={"plugin":name,"total_english_fields":len(records),
              "new_translation":counts["new_translation"],
              "inherited_verified":counts["inherited_verified"],
              "inherited_awaiting_native_test":counts["inherited_awaiting_native_test"],
              "ambiguous_duplicate_source_fields":counts["ambiguous_duplicate_source_fields"],
              "native_apply_tested":changed is not None}
        if sum(stat[k] for k in ["new_translation","inherited_verified","inherited_awaiting_native_test"])!=len(records):
            raise RuntimeError("Broken partition "+name)
        totals.update({k:stat[k] for k in ["new_translation","inherited_verified",
                                           "inherited_awaiting_native_test"]})
        allsummary.append(stat)
    writecsv(DEST/"00_플러그인별_분류결과.csv",allsummary,STATS)
    full={"pending_plugins":len(manifest),
          "total_english_source_fields":sum(r["total_english_fields"] for r in allsummary),
          "new_translation":totals["new_translation"],
          "inherited_native_verified":totals["inherited_verified"],
          "inherited_waiting_validation":totals["inherited_awaiting_native_test"],
          "native_tested_plugins":sum(r["native_apply_tested"] for r in allsummary),
          "guide":"New text is 01. Native unverified inheritance remains 02. Only 03 has actual apply/reload evidence."}
    (DEST/"00_분류현황.json").write_text(json.dumps(full,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (DEST/"00_읽어주세요.md").write_text(
        "# Nuclear Sunset translation queue\n\n"
        "01: Existing SST has no exact source identity. Translate this column in context.\n\n"
        "02: Existing SST candidate exists but has no safe native apply/reload proof, or repeated field ambiguity. Verify first; do not blindly retranslate or count as done.\n\n"
        "03: Saved staging ESP/ESM changed text was verified via native xEditLib fresh readback. Original MO2 plugins were not changed.\n\n"
        "Only the first queue is direct human translation priority. The counts are scanned record fields, not in-game visible coverage. Source CSV originals were retained.\n",
        encoding="utf-8")
    print("PARTITION",json.dumps(full,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
