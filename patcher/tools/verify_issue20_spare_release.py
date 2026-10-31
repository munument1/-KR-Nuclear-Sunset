"""Read-only published v1.0.8 validation of exact #20 casing corrections."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr_issue20_casings as casing


def main(archive):
    with zipfile.ZipFile(archive) as z:
        original_bytes = z.read("TranslationData/catalog.json")
        catalog = json.loads(original_bytes.decode("utf-8-sig"))
    saved = copy.deepcopy(catalog)
    aligned, changed = casing.align_spare_casings(catalog)
    assert catalog == saved, "Source catalog mutated"
    assert len(changed) == len(casing.SPARE_CASINGS) == 7, changed
    assert casing.align_spare_casings(aligned) == (aligned, []), "Not idempotent"

    differences = []
    for first, second in zip(catalog["files"], aligned["files"]):
        assert first["path"] == second["path"]
        if first["mappings"] == second["mappings"]:
            continue
        assert first["path"].casefold() == "spare.esp"
        for a, b in zip(first["mappings"], second["mappings"]):
            if a == b:
                continue
            assert {k: v for k, v in a.items() if k != "dest"} == {
                k: v for k, v in b.items() if k not in ("dest", "previous_dests")
            }, "Changed identity/source/context"
            assert a["dest"] in b["previous_dests"]
            differences.append((a["id"], a["source"], a["dest"], b["dest"]))
    assert len(differences) == 7
    print(json.dumps({
        "release": "v1.0.8", "game_validation": "not_run",
        "catalog_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "changed_rows": len(changed), "all_other_fields_identical": True,
        "idempotent": True, "changes": changed,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
