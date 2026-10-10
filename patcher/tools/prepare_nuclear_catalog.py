"""Prepare a non-release TTW translation catalog from audited local SST sources.

Requires existing read-only plugin audit, and never modifies installed mods.
Catalog stays under .local; no original ESMs or complete translations on GitHub.
"""
from pathlib import Path
import json,sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_sst_catalog import export_for_entry
import nskr
SOURCE=Path(r"F:\번역\프로그램\xTranslator\UserDictionaries\FalloutNV")
OUT=ROOT/".local"/"ns-sst-expanded"
PITT=ROOT/".local"/"thepitt"/"thepitt_en_ko.sst"

def main():
    if OUT.exists():raise SystemExit("Catalog output already exists - won't overwrite")
    base=nskr.read_json(ROOT/".local"/"ns-sst-candidate"/"catalog.json")
    audit=nskr.read_json(ROOT/".local"/"plugin-audit"/"full-audit.json")
    ref={f["path"].casefold():f for f in base["files"] if f["kind"]=="plugin-records"}
    stats=[]
    entries=[]
    for item in audit["plugins"]:
        filename=item.get("direct_sst")
        if not filename:continue
        plugin=item["plugin"]
        sst=(PITT if filename=="thepitt_en_ko.sst" else SOURCE/filename)
        old=ref.get(plugin.casefold(),{})
        rows,counts,parsed=export_for_entry(sst,old)
        if not rows:
            stats.append({"plugin":plugin,"sst":filename,"rows":0,"status":"no_safe_rows"})
            continue
        entry={"path":plugin,"kind":"plugin-records",
               "mappings":rows,
               "translation_source":"local_xtranslator_sst",
               "source_sst_filename":filename}
        entries.append(entry)
        stats.append({"plugin":plugin,"sst":filename,"rows":len(rows),
                      "skipped":counts.get("old_or_unchanged_skipped",0)+counts.get("unsafe_mapping_skipped",0),
                      "pathless":counts.get("pathless_direct",0),"status":"candidate_not_validated"})
    candidate={k:v for k,v in base.items() if k!="files"}
    candidate["files"]=entries+[f for f in base["files"] if f["kind"] in {"json","ini"}]
    candidate["target_modlist"]="nuclear-sunset-ttw"
    candidate["translation_ready"]=False
    candidate["game_validation"]="not_run"
    candidate["data_status"]="uncertified candidate SST mappings; not bundled or released"
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/"catalog.json").write_text(json.dumps(candidate,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    report={"direct_candidate_plugins":len(entries),
            "candidate_sst_rows":sum(len(x["mappings"]) for x in entries),
            "master_sst_rows":[x for x in stats if x["plugin"].casefold() in 
              {"fallout3.esm","anchorage.esm","thepitt.esm","brokensteel.esm","pointlookout.esm","zeta.esm","taleoftwowastelands.esm","yupttw.esm"}],
            "all_plugin_rows":stats,
            "catalog_path":str(OUT/"catalog.json"),"translation_ready":False}
    (OUT/"catalog-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("all_plugin_rows","catalog_path")},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
