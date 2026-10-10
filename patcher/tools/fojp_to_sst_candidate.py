"""Conservative, offline FOJP -> xTranslator SST candidate converter.

Inputs must be extracted FOJP translation files legally provided by the user.
No automatic network downloading, no modification to original MO2 plugins.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.tes4_text_scan import plugin_records, masters, clean_text, HANGUL, DISPLAY_FIELDS
from tools.extract_thepitt_sst import write_sst
import nskr_xedit

def read_lines(path: Path):
    data=path.read_bytes()
    for encoding in ("utf-8-sig","utf-16","cp949","cp932"):
        try:
            text=data.decode(encoding)
            if "\ufffd" not in text and "\x00" not in text:
                return text.splitlines(),encoding
        except UnicodeError:pass
    raise ValueError(f"No supported text encoding: {path}")

def discover_fojp_pairs(source:Path):
    """Read XML en/jp entries, or auto-pair files named *_en.txt and *_ko/_jp.txt."""
    found=[]
    for xml in source.rglob("*.xml"):
        try: root=ET.parse(xml).getroot()
        except ET.ParseError:continue
        for item in root.iter():
            en=item.attrib.get("en"); tr=item.attrib.get("jp") or item.attrib.get("ko")
            if not en or not tr:continue
            paths=[Path(en.replace("\\","/")),Path(tr.replace("\\","/"))]
            # FOJP's XML paths may be relative to game Data or translation folder.
            candidates=[]
            for name in paths:
                options=[xml.parent/name,source/name,source/name.name]
                candidates.append(next((p for p in options if p.is_file()),None))
            if all(candidates):found.append(tuple(candidates))
    if found:return list(dict.fromkeys(found))
    for en in source.rglob("*.txt"):
        m=re.search(r"(?i)(^|[_\-.])en(?=[_\-.]|$)",en.stem)
        if not m:continue
        for token in ("ko","jp"):
            part=en.stem[:m.start()]+m.group(1)+token+en.stem[m.end():]
            candidate=en.with_name(part+en.suffix)
            if candidate.is_file():
                found.append((en,candidate))
                break
    return list(dict.fromkeys(found))

def load_fojp_dictionary(pairs):
    translations=defaultdict(set)
    stats=Counter()
    files=[]
    for en,ko in pairs:
        eng,encoding_en=read_lines(en)
        kr,encoding_ko=read_lines(ko)
        if len(eng)!=len(kr):
            stats["rejected_mismatched_line_count"]+=1
            files.append({"source":str(en),"target":str(ko),"status":"length_mismatch",
                          "source_lines":len(eng),"target_lines":len(kr)})
            continue
        count=0
        for source,dest in zip(eng,kr):
            s=source.strip("\ufeff")
            d=dest.strip("\ufeff")
            if not s or not d or s==d or not HANGUL.search(d):continue
            stats["valid_korean_pairs"]+=1
            translations[s].add(d)
            count+=1
        files.append({"source":str(en),"target":str(ko),"status":"indexed",
                      "source_lines":len(eng),"candidate_pairs":count,
                      "encodings":[encoding_en,encoding_ko]})
        stats["pair_files_indexed"]+=1
    unique={s:next(iter(v)) for s,v in translations.items() if len(v)==1}
    stats["unique_english_sources"]=len(unique)
    stats["ambiguous_english_sources"]=sum(len(v)>1 for v in translations.values())
    return unique,stats,files

def match_plugin(path:Path,mapping:dict,include_overrides:bool):
    mm=masters(path)
    data=[]
    stats=Counter()
    samples=[]
    names=Counter()
    for fid,sig,items in plugin_records(path):
        index=fid>>24
        if index>len(mm):
            stats["invalid_master_index"]+=1
            continue
        owner=mm[index].casefold() if index<len(mm) else path.name.casefold()
        if index<len(mm) and not include_overrides:
            stats["overrides_intentionally_skipped"]+=1
            continue
        counts=Counter(name for name,_ in items)
        for field,raw in items:
            if field not in DISPLAY_FIELDS:continue
            source=clean_text(raw,"utf-8") or clean_text(raw,"cp1252")
            if not source:continue
            stats["readable_text_subrecords"]+=1
            dest=mapping.get(source)
            if not dest:continue
            # The candidate reader does not know hierarchical xEdit paths:
            # keep no arbitrary path for INFO, TERM, QUST etc.
            if counts[field]!=1:
                stats["repeated_subrecord_skipped"]+=1
                continue
            row={
                "owner":owner,
                "id":f"{fid & 0xffffff:06x}",
                "signature":sig,
                "field":field,
                "path":"",
                "source":source,
                "dest":dest,
                "rec_id":0,"rec_id_max":0,"string_id":0,
                "origin":"fojp_exact_source_candidate",
            }
            try:nskr_xedit.validate_mapping(row)
            except ValueError:
                stats["protected_token_mismatch"]+=1
                continue
            data.append(row)
            names[(sig,field)]+=1
            if len(samples)<5:samples.append({"signature":sig,"field":field,"source":source[:80],"dest":dest[:80]})
    # Ensure each target slot/source resolves to one translation.
    slots=defaultdict(set)
    for row in data:
        key=(row["owner"],row["id"],row["signature"],row["field"],row["source"])
        slots[key].add(row["dest"])
    bad={key for key,ds in slots.items() if len(ds)>1}
    if bad:
        data=[row for row in data if (row["owner"],row["id"],row["signature"],row["field"],row["source"]) not in bad]
        stats["conflicting_record_slots_skipped"]=len(bad)
    stats["unique_candidate_rows"]=len(data)
    stats["records_covered"]=len({(r["owner"],r["id"],r["signature"]) for r in data})
    return data,dict(stats),names.most_common(20),samples

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True,help="Folder of extracted FOJP en/jp text files or fojp.xml")
    ap.add_argument("--plugin",type=Path,required=True,help="Unmodified target MO2 ESP/ESM")
    ap.add_argument("--output",type=Path,required=True,help="NEW local output directory, outside game installation")
    ap.add_argument("--include-overrides",action="store_true",help="Include base master overrides (needs careful review)")
    opts=ap.parse_args()
    folder=opts.source.resolve(); plugin=opts.plugin.resolve(); out=opts.output.resolve()
    if not folder.is_dir() or not plugin.is_file():raise SystemExit("Missing input folder or plugin")
    if out.exists():raise SystemExit("Output exists; never overwrite previous validation")
    if out.is_relative_to(folder) or out.is_relative_to(plugin.parent):
        raise SystemExit("Output must not be inside source or installed MO2 files")
    pairs=discover_fojp_pairs(folder)
    if not pairs:raise SystemExit("No matching FOJP en/ko (or en/jp) text pairs found")
    mapping,stats,sourcefiles=load_fojp_dictionary(pairs)
    if not mapping:raise SystemExit("No validated translated pairs available")
    rows,counts,types,samples=match_plugin(plugin,mapping,opts.include_overrides)
    if not rows:raise SystemExit("No exact safe strings matched; keep original unmodified")
    out.mkdir(parents=True,exist_ok=False)
    (out/"candidate_mappings.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (out/"candidate_mappings.csv").open("w",newline="",encoding="utf-8-sig") as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # write_sst includes plugin as new local master; xTranslator GUI and xEdit still need validation.
    write_sst(out/(plugin.stem+"_en_ko.sst"),masters(plugin),rows)
    report={
        "target_plugin":plugin.name,
        "fojp_pairs":sourcefiles,
        "source_stats":dict(stats),
        "matched_stats":counts,
        "matched_record_field_top20":[{"signature":sig,"field":field,"candidate_rows":n} for (sig,field),n in types],
        "samples":samples,
        "status":"EXPERIMENTAL: SST binary roundtrip verified, xEdit field path and runtime apply NOT verified",
    }
    (out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"plugin":plugin.name,"fojp_pair_files":len(pairs),"unique_source_strings":len(mapping),
                      "sst_candidate_rows":len(rows),"covered_records":counts["records_covered"],"output":str(out)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
