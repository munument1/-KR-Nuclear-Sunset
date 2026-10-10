"""Merge reviewed-by-structure Nexus translated ESP candidates into a local, UNRELEASED TTW catalog.

Sources are verified against local original plugin bytes; still requires xEdit readback.
Preserves existing catalog and source data.
"""
from __future__ import annotations
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
from nskr_sst import read_sst
from tools.build_sst_catalog import export_for_entry

SOURCE=ROOT/".local"/"ns-sst-expanded"/"catalog.json"
OUT=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"
MAPS=[
 (ROOT/".local"/"nexus_sst_v2"/"autumn-uncreative"/"AutumnLeaves_en_ko.sst","AutumnLeaves.esp"),
 (ROOT/".local"/"nexus_sst_v2"/"zion-revised"/"ZionTrail_en_ko.sst","ZionTrail.esm")
]
def main():
    if OUT.exists():raise SystemExit("Destination exists, won't overwrite!")
    d=nskr.read_json(SOURCE)
    if d.get("translation_ready") is not False:raise SystemExit("Only nonrelease catalog accepted")
    existing={x["path"].casefold() for x in d["files"] if x["kind"]=="plugin-records"}
    details=[]
    for file,plugin in MAPS:
        if plugin.casefold() in existing:raise SystemExit("Duplicate plugin in previous catalog")
        rows,stat,_=export_for_entry(file,{"mappings":[]})
        if not rows:raise RuntimeError("Failed SST conversion: "+plugin)
        expected=nskr.read_json(file.parent/"report.json")["counts"]["translated_text_candidate_rows"]
        if len(rows)!=expected:
            raise RuntimeError(f"Row mismatch {plugin}: {len(rows)} vs {expected}")
        d["files"].append({
            "path":plugin,"kind":"plugin-records",
            "mappings":rows,
            "translation_source":"nexus_korean_esp_exact_text_diff",
            "source_sst_filename":file.name,
            "verified_delta":None
        })
        details.append({"plugin":plugin,"rows":len(rows),"sst_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                        "pathless":stat["pathless_direct"],"unsafe_skipped":stat["unsafe_mapping_skipped"]})
    d["translation_ready"]=False
    d["game_validation"]="not_run"
    d["data_status"]="Candidates only; xEditLib field-path, game, copyright/release review outstanding"
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/"catalog.json").write_text(json.dumps(d,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    report={"source_catalog":str(SOURCE),"entries":details,
            "total_candidate_plugin_rows":sum(len(f["mappings"]) for f in d["files"] if f["kind"]=="plugin-records"),
            "total_direct_sst_plugins":sum(f["kind"]=="plugin-records" for f in d["files"]),
            "translation_ready":False}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
