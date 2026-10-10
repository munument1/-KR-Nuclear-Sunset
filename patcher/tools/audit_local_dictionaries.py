"""Read-only audit of xTranslator FalloutNV SST and saved MCM mapping sources.

No game files, source dictionaries or MO2 profile files are modified.
"""
from pathlib import Path
from collections import Counter
import json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nskr
from nskr_sst import read_sst, SstParseError
ROOT=Path(r"F:\번역\프로그램")
SST_DIR=ROOT/"xTranslator"/"UserDictionaries"/"FalloutNV"
MCM_DB=ROOT/"SimpleMcmJsonTranslator"/"db"
VNV_MCM=Path(__file__).resolve().parents[1]/"data"/"mcm_direct_mappings.json"
MASTERS=["fallout3","anchorage","thepitt","brokensteel","pointlookout","zeta","taleoftwowastelands","yupttw"]
def main():
    install=nskr.Installation(Path(r"C:\Modlists\NuclearSunset"))
    active={p.casefold().removesuffix(".esm").removesuffix(".esp") for p in install.active}
    all_sst=sorted(SST_DIR.glob("*_en_ko.sst"))
    summaries=[]
    for f in all_sst:
        stem=f.name.casefold().removesuffix("_en_ko.sst")
        # All direct filename matches and key TTW masters get parsed.
        if stem not in active and stem not in MASTERS: continue
        try:
            info=read_sst(f)
            translated=sum(bool(e.source and e.dest and e.source!=e.dest and "\ufffd" not in (e.source+e.dest)) for e in info.entries)
            summaries.append({"name":f.name,"plugin":stem,"bytes":f.stat().st_size,
                              "format":info.format,"plugin_headers":info.plugins[:20],
                              "total_entries":len(info.entries),"translated_candidate_entries":translated,
                              "status":"readable"})
        except Exception as exc:
            summaries.append({"name":f.name,"plugin":stem,"bytes":f.stat().st_size,
                              "status":"parse_error","error":repr(exc)[:240]})
    missing=[x for x in MASTERS if not (SST_DIR/(x+"_en_ko.sst")).is_file()]
    if VNV_MCM.exists():
        mcm=json.loads(VNV_MCM.read_text(encoding="utf-8-sig"))
        mcm_entries=mcm.get("files",[])
    else: mcm_entries=[]
    report={
      "xtranslator_sst_directory":str(SST_DIR),
      "sst_total":len(all_sst),
      "sst_match_with_active_or_core_count":len(summaries),
      "master_sst_missing":missing,
      "master_sst":[row for row in summaries if row["plugin"] in MASTERS],
      "other_matched_sst":[row for row in summaries if row["plugin"] not in MASTERS],
      "saved_vnv_mcm": {"path":str(VNV_MCM),"files":len(mcm_entries),
        "mapping_rows":sum(len(e.get("mappings",[])) for e in mcm_entries),
        "entries":[{"path":e.get("path"),"provider":e.get("provider"),"mapping_rows":len(e.get("mappings",[])),
                    "installed_provider":e.get("path","").casefold() in install.providers} for e in mcm_entries]},
      "simple_mcm_json_translator":{"path":str(MCM_DB),"mcmdb_files":len(list(MCM_DB.glob("*.mcmdb"))),
                                    "note":"Appears primarily Fallout 4, different from NV MCM/Translations INI"},
      "disclaimer":"SST parse and filename matches only, no live plugin XEditLib validation, not install-ready."
    }
    out=Path(__file__).resolve().parents[1]/".local"/"f-drive-audit.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("other_matched_sst", "master_sst")},ensure_ascii=False,indent=2))
    print("MASTER SST",json.dumps(report["master_sst"],ensure_ascii=False))
    print("OTHER_MATCHED",len(report["other_matched_sst"]))
    print("OTHER_MATCHED_NAMES",", ".join(row["name"] for row in report["other_matched_sst"]))
if __name__=="__main__": main()
