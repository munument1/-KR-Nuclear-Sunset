"""Read-only inspection of published catalog's possible karma save titles.

Does not touch games, player save files, or release artifacts.
"""
import json
import sys
import zipfile
from pathlib import Path

CANDIDATES = ('karma', 'title', 'ttwnvse', 'roognvse', 'level', 'save')
MAX_MATCHES = 220
def main(archive):
    with zipfile.ZipFile(archive) as z:
        catalog = json.loads(z.read('TranslationData/catalog.json').decode('utf-8-sig'))
    paths = []
    matches = []
    for spec in catalog.get('files', []):
        path = str(spec.get('path', ''))
        if any(x in path.casefold() for x in CANDIDATES):
            paths.append({'path':path,'kind':spec.get('kind'),
                          'mapping_count':len(spec.get('mappings',[]))})
        for row in spec.get('mappings', []):
            context = ' '.join(str(row.get(k,'')) for k in
                               ('section', 'key','field','signature','source','dest'))
            key = (path + ' ' + context).casefold()
            # Only show direct evidence, not all level ups or unrelated 'title'.
            if not any(x in key for x in ('karma title','karmatitl','karama',
                                         'karma','save title','[titles]','sleveltitle')):
                continue
            if len(matches)>=MAX_MATCHES: continue
            matches.append({'file':path, 'owner':row.get('owner'),
                 'id':row.get('id'), 'signature':row.get('signature'),
                 'field':row.get('field'), 'section':row.get('section'),
                 'key':row.get('key'), 'source':str(row.get('source',''))[:220],
                 'dest':str(row.get('dest',''))[:220]})
    result={'version':catalog.get('version'),
            'candidate_paths':paths,'matching_translation_rows':matches,
            'total_displayed_rows':len(matches),
            'note':'Source catalog mapping only; runtime winning file and save header still unknown'}
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return result

if __name__ == '__main__':
    main(Path(sys.argv[1]))
