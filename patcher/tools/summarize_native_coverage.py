"""Publishable metadata-only evidence report for isolated Nuclear Sunset SST validation.

Never includes original ESM/ESP, SST mapping payload, or game text.
"""
from __future__ import annotations
from pathlib import Path
import json,sys,collections
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
CATALOG=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
BATCH=ROOT/".local"/"native-plugin-batch-20261010"/"summary.json"
QUEST=ROOT/".local"/"native-validation-20261010-v2"/"summary.json"
PITT=ROOT/".local"/"native-validation-thepitt-20261010"/"result_summary.json"
OUT=ROOT/"docs"/"direct-sst-native-audit.md"
def main():
    catalog=nskr.read_json(CATALOG)
    targets={f["path"].casefold():f for f in catalog["files"] if f.get("kind")=="plugin-records"}
    rows={}
    batch=json.loads(BATCH.read_text(encoding="utf-8"))
    for b in batch:
        key=b["plugin"].casefold()
        if key in rows:raise RuntimeError("Duplicate plugin "+key)
        rows[key]={"name":b["plugin"],"status":b["status"],"applied":b.get("applied",0),
                   "records":b.get("records_verified",0),"candidate":b.get("candidate_rows",0),
                   "observed_unmatched_fields":b.get("unmatched_observed_fields",0),
                   "error":b.get("error","")}
    quest=json.loads(QUEST.read_text(encoding="utf-8"))
    for q in quest:
        if q["status"]!="native_apply_and_readback_passed":raise RuntimeError("Unverified quest "+q["plugin"])
        key=q["plugin"].casefold()
        if key in rows:raise RuntimeError("Duplicate "+key)
        rows[key]={"name":q["plugin"],"status":"PASS","applied":q["stats"]["translated"],
                   "records":q["stats"]["records_verified"],
                   "candidate":q["candidate_rows"],
                   "observed_unmatched_fields":q["stats"]["unmatched"],"error":""}
    pitt=json.loads(PITT.read_text(encoding="utf-8"))
    if pitt["status"]!="apply_and_fresh_readback_passed":raise RuntimeError("Pitt failed")
    rows["thepitt.esm"]={"name":"ThePitt.esm","status":"PASS","applied":pitt["translated"],
                        "records":pitt["records_verified"],"candidate":pitt["candidate_sst_rows"],
                        "observed_unmatched_fields":pitt["unmatched"],"error":""}
    if any(k not in targets for k in rows):raise RuntimeError("unexpected validation target")
    for key,r in rows.items():
        if r["candidate"]!=len(targets[key]["mappings"]):
            raise RuntimeError("Catalog count mismatch "+r["name"])
    untested=sorted(set(targets)-set(rows))
    summary=collections.Counter(r["status"] for r in rows.values())
    target_count=sum(r["candidate"] for r in rows.values())
    applied=sum(r["applied"] for r in rows.values())
    records=sum(r["records"] for r in rows.values())
    lines=[
       "# Nuclear Sunset direct SST native verification (2026-10-10)",
       "",
       "An isolated native XEditLib apply + fresh reload test was run against the installed Nuclear Sunset MO2 profile. All game plugin originals remained unchanged.",
       "",
       f"- Direct SST catalog targets: **{len(targets)}**",
       f"- Actually tested: **{len(rows)}** (pass: {summary['PASS']}; pass without matched text: {summary['PASS_NO_MATCHED_TRANSLATIONS']}; failed: {summary['FAIL']})",
       f"- Untested: **{len(untested)}**",
       f"- Candidate text mappings for tested targets: **{target_count:,}**",
       f"- Native applied and reloaded text fields: **{applied:,}**",
       f"- Structurally verified changed records: **{records:,}**",
       "",
       "The mapping count is a **candidate** count; 'applied' means text was actually written to a staging copy, reloaded and structurally verified. Neither measure is in-game string-coverage percentage. Observed unmatched fields refer to worker-field inspection and cannot be subtracted from the candidate count.",
       "",
       "| Active plugin | Candidate fields | Native applied fields | Verified changed records | Status |",
       "|---|---:|---:|---:|---|"
    ]
    for key in sorted(rows):
        r=rows[key]
        lines.append(f"| {r['name']} | {r['candidate']:,} | {r['applied']:,} | {r['records']:,} | {r['status']} |")
    lines.extend(["","## Untested",""])
    if untested:
        lines.extend("- "+targets[x]["path"] for x in untested)
    else:lines.append("None of the direct-SST plugins remains untested.")
    failures=[r for r in rows.values() if r["status"]=="FAIL"]
    if failures:
        lines.extend(["","## Validation failures",""])
        for f in failures:lines.append(f"- {f['name']}: {f['error'][:200]}")
    lines.extend([
       "",
       "## Still required before release",
       "",
       "- Validate per-record path/source ambiguity and official-base-master inheritance on the 48 identified fallback candidates; resolve candidates with no direct SST separately.",
       "- Inventory and translate active MCM JSON, translations INI, UI strings and any radio/subtitle data not stored in plugin record fields.",
       "- Test the end-to-end packaged installer and MO2 profile output, then test actual game rendering in the target TNVSE runtime.",
       "- Confirm attribution and license restrictions on third-party translated data. No upstream game/mod plugins or original text assets are committed.",
       "- Keep translation_ready=false until those gates are satisfied.",
       ""
    ])
    OUT.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"direct_total":len(targets),"tested":len(rows),"pass":summary["PASS"],
                      "failed":summary["FAIL"],"untested":len(untested),
                      "candidate":target_count,"applied":applied,"records_verified":records},ensure_ascii=False))
if __name__=="__main__":main()
