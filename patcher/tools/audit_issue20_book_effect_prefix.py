"""Read-only audit of skill book display text and Stewie configuration in v1.0.8."""
import json,sys,zipfile
from pathlib import Path
with zipfile.ZipFile(sys.argv[1]) as z:
    data=json.loads(z.read('TranslationData/catalog.json').decode('utf-8-sig'))
    found=[]
    for spec in data.get('files',[]):
        path=spec.get('path','')
        tests=('stewie' in path.lower(), 'tweaks' in path.lower())
        for i,row in enumerate(spec.get('mappings',[])):
            source=str(row.get('source',''))
            dest=str(row.get('dest',''))
            ctx=str((row.get('section'),row.get('key'),row.get('signature'),row.get('field')))
            if (any(tests) or 'book effects' in ctx.lower() or 'sprefix' in ctx.lower()
                or 'permanent' in source.lower()
                or (row.get('id','').lower()=='034043')
                or ('sbook' in ctx.lower())):
                if len(found)>=300:continue
                found.append({'plugin':path,'kind':spec.get('kind'),'index':i,
                              'owner':row.get('owner'),'id':row.get('id'),
                              'signature':row.get('signature'),'field':row.get('field'),
                              'section':row.get('section'),'key':row.get('key'),
                              'source':source[:200],'dest':dest[:200]})
    print(json.dumps({'all_specs':len(data.get('files',[])),'result_count':len(found),
                      'records':found},ensure_ascii=False,indent=2))
