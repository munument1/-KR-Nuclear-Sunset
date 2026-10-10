"""Summarize candidate SST rows not realized by native xEditLib apply; no personal strings emitted."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/".local"/"native-validation-20261010-v2"
INPUT=ROOT/".local"/"ns-sst-with-nexus-quest-esp-v2"/"catalog.json"
OUT=RUN/"candidate-coverage-summary.json"
def key(row):
    return tuple(str(row.get(x,"")).casefold() for x in ("owner","id","signature","field","source","dest"))
def main():
    cat=json.loads(INPUT.read_text(encoding="utf-8"))
    summary=[]
    for name in ("AutumnLeaves.esp","ZionTrail.esm"):
        entry=next(e for e in cat["files"] if e.get("path","").casefold()==name.casefold())
        actual=json.loads((RUN/Path(name).stem/"apply.json").read_text(encoding="utf-8"))
        changed=actual["files"][0]["changed"]
        source_map={key(c) for c in entry["mappings"]}
        applied={key(c) for c in changed}
        unused=[c for c in entry["mappings"] if key(c) not in applied]
        report={
            "plugin":name,
            "sst_rows":len(entry["mappings"]),
            "changed_field_instances":len(changed),
            "unmatched_candidates":len(unused),
            "unmatched_by_record_signature":dict(Counter(c["signature"] for c in unused)),
            "unmatched_by_field":dict(Counter(c["field"] for c in unused)),
            "matched_candidate_keys":len(source_map&applied),
            "applied_without_candidate_key":len(applied-source_map),
            "notes":"Unmatched direct source item diagnostics can include non-eligible text fields, and are not equal to unused candidate count."
        }
        summary.append(report)
        print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
