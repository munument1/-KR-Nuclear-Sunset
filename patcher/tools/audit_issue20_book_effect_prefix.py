"""Focused inventory: Stewie tweak prefix, book record, and game settings."""
import json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    data=json.loads(z.read('TranslationData/catalog.json').decode('utf-8-sig'))
results=[]
paths=[]
for spec in data.get('files',[]):
    path=spec.get('path','')
    if 'stewie' in path.casefold() or 'tweak' in path.casefold():
        paths.append({'path':path,'kind':spec.get('kind'),'num_mappings':len(spec.get('mappings',[]))})
    for row in spec.get('mappings',[]):
        section=str(row.get('section','')); key=str(row.get('key',''))
        source=str(row.get('source','')); owner=str(row.get('owner',''))
        ident=str(row.get('id','')).casefold()
        if (section.casefold() in ('[book effects]','book effects')
            or (key.casefold()=='sprefix' and 'book' in path.casefold())
            or ident in ('034043','00034043')
            or (path.lower().endswith('falloutnv.esm') and row.get('signature')=='GMST'
                and ('book' in source.casefold() or 'permanent' in source.casefold()))):
            results.append({'plugin':path,'owner':owner,'id':ident,
                'section':section,'key':key,'sig':row.get('signature'),
                'field':row.get('field'),'source':source[:300],
                'dest':str(row.get('dest'))[:300]})
print(json.dumps({'stewie_or_tweaks_paths':paths,'book_effect_records':results[:80],
                  'matches_total':len(results)},ensure_ascii=False,indent=2))
