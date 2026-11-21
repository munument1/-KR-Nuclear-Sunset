"""Read-only v1.0.8 release audit of #20 screenshot-visible English text."""
import json
from pathlib import Path
import re
import sys
import zipfile

TESTS = {
    "glowing_fungus": lambda s: "glowing fungus" in s.casefold(),
    "healing_percentage": lambda s: bool(
        re.search(r"Restores? (?:one limb|[0-9]+%|%[a-z.0-9]+)", s, re.I)),
    "first_aid": lambda s: "first aid" in s.casefold() or "medical bag" in s.casefold(),
    "dc_journal": lambda s: "journal of internal medicine" in s.casefold(),
}

def main(archive):
    with zipfile.ZipFile(archive) as z:
        docs = {}
        for p in ("TranslationData/catalog.json",
                  "TranslationData/runtime_ui/NSKR_UI_Translations.json"):
            docs[p] = json.loads(z.read(p).decode('utf-8-sig'))
    result = {key: [] for key in TESTS}
    for path, doc in docs.items():
        if isinstance(doc, dict):
            for spec in doc.get('files', []):
                for m in spec.get('mappings', []):
                    source, target = m.get('source', ''), m.get('dest', '')
                    if not isinstance(source, str) or not isinstance(target, str):
                        continue
                    for key, fn in TESTS.items():
                        if fn(source):
                            result[key].append(dict(catalog=path, plugin=spec.get('path'),
                                                    source=source, dest=target,
                                                    owner=m.get('owner'), id=m.get('id'),
                                                    signature=m.get('signature'), field=m.get('field')))
        elif isinstance(doc, list):
            for i, m in enumerate(doc):
                if not isinstance(m, dict):continue
                source, target = m.get('original', ''), m.get('translation', '')
                for key, fn in TESTS.items():
                    if isinstance(source, str) and fn(source):
                        result[key].append(dict(catalog=path, index=i, source=source, dest=target))
    print(json.dumps({k: {'count': len(v), 'matches': v[:30]}
                      for k, v in result.items()}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
