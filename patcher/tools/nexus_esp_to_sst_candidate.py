"""Read-only extraction of Korean SST candidates from Nexus translation ESP/ESM.

Only pairs structurally equivalent record subrecords, checking base English source,
real Hangul destination and protected format tokens. All output stays under .local.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.tes4_text_scan import plugin_records,masters,clean_text,HANGUL,ENGLISH,DISPLAY_FIELDS
from tools.extract_thepitt_sst import write_sst
import nskr_xedit

def record_index(file:Path):
    result={}
    duplicates=0
    for fid,sig,subrecords in plugin_records(file):
        if fid in result:
            duplicates+=1
        result[fid]=(sig,subrecords)
    return result,duplicates

def derive(original:Path,korean:Path,output:Path):
    original_masters=masters(original); korean_masters=masters(korean)
    if original.name.casefold()!=korean.name.casefold():
        raise ValueError("Input ESP/ESM names do not match")
    if [x.casefold() for x in original_masters]!=[x.casefold() for x in korean_masters]:
        raise ValueError("Master list mismatch; automatic record identity is unsafe")
    old,old_dups=record_index(original)
    target,target_dups=record_index(korean)
    stats=collections.Counter(); fields=collections.Counter(); signatures=collections.Counter()
    samples=[]; rows=[]; review=[]
    for fid,(sig,old_values) in old.items():
        stats["original_records"]+=1
        trans=target.get(fid)
        if not trans:
            stats["missing_in_translation"]+=1;continue
        target_sig,target_values=trans
        if target_sig!=sig:
            stats["signature_mismatch"]+=1;continue
        stats["matching_record_ids_and_signatures"]+=1
        if len(old_values)!=len(target_values):
            stats["different_field_counts"]+=1;continue
        if [x[0] for x in old_values]!=[x[0] for x in target_values]:
            stats["different_field_layouts"]+=1;continue
        # Only import records where all changed subrecords are safe textual
        # and all unrelated binary/structural data are unchanged.
        changed=[]
        hard_changes=[]
        for index,((field,raw),(after_field,converted)) in enumerate(zip(old_values,target_values)):
            if raw==converted:continue
            if field not in DISPLAY_FIELDS:
                hard_changes.append(field);continue
            src=clean_text(raw,"utf-8") or clean_text(raw,"cp1252")
            dst=clean_text(converted,"utf-8")
            if not src or not dst or not ENGLISH.search(src) or not HANGUL.search(dst):
                hard_changes.append(field);continue
            row={"owner":(original_masters[fid>>24] if fid>>24<len(original_masters) else original.name).casefold(),
                 "id":f"{fid&0xffffff:06x}","signature":sig,"field":field,"path":"",
                 "source":src,"dest":dst,"rec_id":sum(1 for f,_ in old_values[:index] if f==field),
                 "rec_id_max":sum(1 for f,_ in old_values if f==field),
                 "string_id":0,"origin":"nexus_translated_esp_exact_field_diff"}
            try:nskr_xedit.validate_mapping(row)
            except ValueError:
                hard_changes.append(field);stats["token_mismatch"]+=1;continue
            changed.append(row)
        if hard_changes:
            stats["records_with_nontext_or_unsafe_changes"]+=1
            if len(review)<20:
                review.append({"fid":f"{fid:08X}","sig":sig,"nontext":hard_changes[:15],
                               "safe_text_pairs":len(changed)})
            continue
        if not changed:
            stats["unchanged_or_no_eligible_text"]+=1;continue
        # Repeated same field mapped to different translations can be ambiguous
        slot=collections.defaultdict(set)
        for item in changed:
            slot[(item["field"],item["source"])].add(item["dest"])
        if any(len(v)>1 for v in slot.values()):
            stats["ambiguous_repeated_fields"]+=1
            continue
        rows.extend(changed)
        stats["records_with_safe_translation"]+=1
        for r in changed:
            fields[r["field"]]+=1
            signatures[r["signature"]]+=1
            if len(samples)<10:samples.append({"fid":f"{fid:08X}","signature":sig,
                                                "field":r["field"],"source":r["source"][:130],
                                                "dest":r["dest"][:130]})
    stats["translation_only_records"]=len(set(target)-set(old))
    stats["translated_text_candidate_rows"]=len(rows)
    stats["original_duplicate_ids"]=old_dups
    stats["translated_duplicate_ids"]=target_dups
    # Unambiguous field paths, when likely single flat field.
    from tools.build_sst_catalog import _derive_path
    for r in rows:
        r["path"]=_derive_path(r["signature"],r["field"]) or ""
    if not rows:
        raise RuntimeError("No safe translation pairs; no output created")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True,exist_ok=False)
    (output/"candidate_mappings.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_sst(output/(original.stem+"_en_ko.sst"),original_masters,rows,target_name=original.name)
    report={"plugin":original.name,
            "origin_file_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
            "korean_file_sha256":hashlib.sha256(korean.read_bytes()).hexdigest(),
            "source_file_size":original.stat().st_size,
            "translated_file_size":korean.stat().st_size,
            "master_names":original_masters,
            "counts":dict(stats),
            "field_counts":dict(fields.most_common()),
            "signature_counts":dict(signatures.most_common()),
            "samples":samples,
            "excluded_record_samples":review,
            "status":"SST roundtrip verified; plugin source-text/path/readback NOT yet verified"}
    (output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--korean",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise SystemExit("Output already exists; no overwrite")
    report=derive(args.original.resolve(),args.korean.resolve(),args.output.resolve())
    print(json.dumps({k:v for k,v in report.items() if k not in ("samples","excluded_record_samples")},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
