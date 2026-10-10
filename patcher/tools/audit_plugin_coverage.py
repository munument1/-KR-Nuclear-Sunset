"""Audit all ACTIVE Nuclear Sunset MO2 plugins against local SST sources and text fields.

Read only. Reports potential exact FormID-field-source matches; no plugin is modified.
"""
from pathlib import Path
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
import csv,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
from nskr_sst import read_sst
from tes4_text_scan import masters,plugin_records,DISPLAY_FIELDS,clean_text,HANGUL,ENGLISH
from tools.build_sst_catalog import FLAT_SIGNATURES

SST=Path(r"F:\번역\프로그램\xTranslator\UserDictionaries\FalloutNV")
MO2=Path(r"C:\Modlists\NuclearSunset")
OUT=ROOT/".local"/"plugin-audit"
PITT=ROOT/".local"/"thepitt"/"thepitt_en_ko.sst"

def sst_index():
    sources={}
    memory=defaultdict(set)
    diag=Counter()
    for p in sorted([*SST.glob("*_en_ko.sst"),PITT]):
        if not p.is_file():continue
        try:sst=read_sst(p)
        except Exception as exc:
            print("ERROR SST",p.name,repr(exc)[:160],flush=True)
            continue
        target=sst.plugins[-1].casefold() if sst.plugins else ''
        if target and target not in sources:
            sources[target]=p.name
        diag["sst_files"]+=1
        for item in sst.entries:
            diag["sst_entries"]+=1
            owner_idx=item.form_id>>24
            if owner_idx>=len(sst.plugins) or not item.source or item.dest==item.source or '\ufffd' in item.dest:
                continue
            sig=item.rec[:4]; field=item.rec[4:]
            key=(sst.plugins[owner_idx].casefold(),item.form_id&0xffffff,sig,field,item.source)
            memory[key].add(item.dest)
    usable={k:next(iter(v)) for k,v in memory.items() if len(v)==1}
    diag["unique_identity_mappings"]=len(usable)
    diag["conflicting_identity_mappings"]=sum(len(v)>1 for v in memory.values())
    return sources,usable,diag

def inspect(thing,dict_sources,memory):
    plugin,physical,provider=thing
    path=Path(physical)
    result={"plugin":plugin,"provider":provider,"path":str(path),"bytes":path.stat().st_size if path.is_file() else 0,
            "direct_sst":dict_sources.get(plugin.casefold()),"status":"analyzed"}
    if not path.is_file():
        result["status"]="source_missing"
        return result
    try:
        mm=masters(path)
        # For official plugin origin, own records are len(masters). For patchers, this is also correct.
        c=Counter()
        samples=[]
        for fid,sig,subfields in plugin_records(path,only_display=True):
            owner_index=fid>>24
            if owner_index<len(mm):owner=mm[owner_index].casefold()
            elif owner_index==len(mm):owner=plugin.casefold()
            else:
                c["unresolved_owner_records"]+=1
                continue
            local=fid&0xffffff
            for field,raw in subfields:
                if field not in DISPLAY_FIELDS:continue
                content=clean_text(raw,"utf-8") or clean_text(raw,"cp1252")
                if not content:continue
                if HANGUL.search(content):
                    c["existing_korean_fields"]+=1
                    continue
                if not ENGLISH.search(content):
                    continue
                c["english_fields"]+=1
                if owner==plugin.casefold():c["english_own_records"]+=1
                else:c["english_override_records"]+=1
                k=(owner,local,sig,field,content)
                trans=memory.get(k)
                if trans:
                    c["sst_identity_candidates"]+=1
                    if owner==plugin.casefold():c["sst_direct_identity_matches"]+=1
                    else:c["sst_override_identity_matches"]+=1
                    if sig in FLAT_SIGNATURES and field in ("FULL","DESC","NNAM","RNAM","CNAM","TNAM"):
                        c["high_confidence_flat_matches"]+=1
                elif owner==plugin.casefold() and len(samples)<5:
                    samples.append({"record":f"{fid:08X}","signature":sig,"field":field,"source":content[:150]})
        result.update(c)
        result["sample_own_untranslated"]=samples
        if result["direct_sst"]:
            if c["sst_identity_candidates"]:
                result["category"]="direct_sst_matches"
            else:
                result["category"]="direct_sst_no_exact_source_match"
        elif c["english_fields"]==0:
            result["category"]="no_detected_english_text"
        elif c["english_own_records"]==0 and c["sst_override_identity_matches"]:
            result["category"]="override_fallback_candidates"
        elif c["english_own_records"]>0:
            result["category"]="own_text_without_sst"
        elif c["sst_identity_candidates"]>0:
            result["category"]="override_fallback_candidates"
        else:result["category"]="no_sst_no_identified_translation"
    except Exception as exc:
        result["status"]="inspection_error"
        result["category"]="inspection_error"
        result["error"]=str(exc)[:200]
    return result

def main():
    install=nskr.Installation(MO2)
    if not install.is_ttw:raise ValueError("Not TTW")
    sources,memory,diag=sst_index()
    print("SST INDEX:",dict(diag),"direct targets",len(sources),flush=True)
    jobs=[]
    for plugin in install.active:
        chain=install.providers.get(plugin.casefold(),[])
        if not chain:
            jobs.append((plugin,"","missing"))
        else:
            jobs.append((plugin,chain[-1]["physical"],chain[-1]["provider"]))
    OUT.mkdir(parents=True,exist_ok=True)
    done=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        tasks={pool.submit(inspect,job,sources,memory):job[0] for job in jobs}
        for task in as_completed(tasks):
            value=task.result()
            done.append(value)
            if len(done)%25==0 or len(done)==len(jobs):
                print("SCAN",len(done),"/",len(jobs),dict(Counter(x.get("category") for x in done)),flush=True)
    ordered={v["plugin"].casefold():v for v in done}
    ordered_list=[ordered[x.casefold()] for x in install.active]
    metrics=Counter()
    cats=Counter()
    for row in ordered_list:
        cats[row["category"]]+=1
        for name in ("english_fields","existing_korean_fields","english_own_records",
                     "english_override_records","sst_identity_candidates","sst_direct_identity_matches",
                     "sst_override_identity_matches","high_confidence_flat_matches"):
            metrics[name]+=row.get(name,0)
    report={
        "target":"Nuclear Sunset","profile":install.profile,"plugins_active":len(jobs),
        "counts_by_category":dict(cats),"metrics":dict(metrics),
        "sst_inventory":dict(diag),"classification_caution":
        "SST source filename and identity matches are preflight only; requires native xEdit field-path/readback validation.",
        "plugins":ordered_list
    }
    (OUT/"full-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    columns=["plugin","category","provider","direct_sst","english_fields","english_own_records",
             "english_override_records","existing_korean_fields","sst_identity_candidates",
             "sst_direct_identity_matches","sst_override_identity_matches",
             "high_confidence_flat_matches","bytes","status","error"]
    with (OUT/"plugin-classification.csv").open("w",encoding="utf-8-sig",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=columns,extrasaction="ignore");writer.writeheader();writer.writerows(ordered_list)
    with (ROOT/"docs"/"nuclear-sunset-plugin-coverage.md").open("w",encoding="utf-8") as fp:
        fp.write("# Nuclear Sunset: 252 active plugin Korean SST feasibility audit\n\n")
        fp.write("Read-only analysis of the selected MO2 profile; no ESP/ESM files were modified.\n\n")
        fp.write(f"- Selected profile: {install.profile}\n- Plugins: {len(jobs)}\n\n")
        fp.write("## Audit categories (not translated/applied counts)\n\n")
        for label,count in cats.most_common():fp.write(f"- {label}: **{count}**\n")
        fp.write("\n## Candidate field counts (not applied strings)\n\n")
        for label,count in metrics.items():fp.write(f"- {label}: {count:,}\n")
        fp.write("\n## All active plugins\n\n")
        fp.write("| Plugin | Category | Direct SST | English fields | Own English | Exact SST identity candidates |\n")
        fp.write("|---|---|---|---:|---:|---:|\n")
        for row in ordered_list:
            values=[row["plugin"],row.get("category",""),row.get("direct_sst","") or "—",
                    str(row.get("english_fields",0)),str(row.get("english_own_records",0)),
                    str(row.get("sst_identity_candidates",0))]
            fp.write("| "+" | ".join(s.replace("|","/").replace("\n"," ") for s in values)+" |\n")
        fp.write("\nThis is NOT proof of xEdit path-level validity, runtime displayed translation, or permission to redistribute third-party source data.\n")
    print("AUDIT_REPORT",json.dumps({"counts":dict(cats),"metrics":dict(metrics)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
