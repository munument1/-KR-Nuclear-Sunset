"""Inspect the published Nuclear Sunset v1.0.8 mapping for casing variants."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import zipfile

OUT = Path(sys.argv[2])
with zipfile.ZipFile(sys.argv[1]) as archive:
    catalogs = {}
    for path in (
        "TranslationData/catalog.json",
        "TranslationData/runtime_ui/NSKR_UI_Translations.json",
    ):
        catalogs[path] = json.loads(archive.read(path).decode("utf-8-sig"))

results = []
counts = {}
for catalog, data in catalogs.items():
    if isinstance(data, dict) and isinstance(data.get("files"), list):
        for spec in data["files"]:
            for row in spec.get("mappings", []):
                dest = row.get("dest")
                if not isinstance(dest, str) or "탄피" not in dest:
                    continue
                results.append({
                    "catalog": catalog,
                    "file": spec.get("path"),
                    "kind": spec.get("kind"),
                    "source": row.get("source"),
                    "dest": dest,
                    "owner": row.get("owner"),
                    "id": row.get("id"),
                    "signature": row.get("signature"),
                    "field": row.get("field"),
                    "path": row.get("path"),
                })
    if isinstance(data, list):
        for i, row in enumerate(data):
            if not isinstance(row, dict):
                continue
            dest = row.get("translation")
            if not isinstance(dest, str) or "탄피" not in dest:
                continue
            results.append({
                "catalog": catalog, "index": i,
                "source": row.get("original"), "dest": dest,
            })
for row in results:
    dest = row["dest"].strip()
    kind = "exact" if dest == "탄피" else (
        "punctuated" if dest == "탄피." else "contextual")
    counts[kind] = counts.get(kind, 0) + 1
    row["classification"] = kind

report = {
    "tag": "v1.0.8", "game_validation": "not_run",
    "source": "published TranslationData zip",
    "counts": counts,
    "entries": results,
    "note": "Exact vs punctuated variants require FormID/source context review. No automatic replacement.",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"counts": counts, "entries": results[:60]}, ensure_ascii=False, indent=2))
