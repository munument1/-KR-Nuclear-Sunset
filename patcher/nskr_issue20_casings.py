"""Exact v1.0.8 SPARE casing-name consistency corrections for issue #20.

The seven reviewed mappings come from the *published* v1.0.8
TranslationData/catalog.json (source, plugin, owner, FormID, field).
No arbitrary punctuation removal and no source file edits.
"""

# (owning plugin, FormID, original English, old Korean, corrected Korean)
SPARE_CASINGS = (
    ('spare.esp', '00ecb2', 'Shell, 25mm Grenade',
     '탄피, 25mm 유탄', '[탄피] 25mm 유탄'),
    ('spare.esp', '00ecb1', 'Shell, 40mm Grenade',
     '탄피, 40mm 유탄', '[탄피] 40mm 유탄'),
    ('spare.esp', '00ebed', 'Case, .223',
     '탄피, .223', '[탄피] .223'),
    ('spare.esp', '00138c', 'Case, 7.62mm',
     '탄피, 7.62mm', '[탄피] 7.62mm'),
    ('spare.esp', '00138b', 'Case, .44 Special',
     '탄피, .44 스페셜', '[탄피] .44 스페셜'),
    ('spare.esp', '00138a', 'Case, .38 Special',
     '탄피, .38 스페셜', '[탄피] .38 스페셜'),
    ('taleoftwowastelands.esm', '007c7c', 'Case, .32 Magnum',
     '탄피, .32 매그넘', '[탄피] .32 매그넘'),
)
BY_KEY = {(owner, fid): (source, old, new)
          for owner, fid, source, old, new in SPARE_CASINGS}


def align_spare_casings(catalog):
    """Return a new in-memory catalog and a ledger of exact edits.

    Only SPARE.esp MISC/FULL entries matching reviewed original English
    and exact prior translation are changed. Old Korean text is registered
    as previous_dests for safe upgrades of previously patched input.
    Unexpected variants fail closed rather than being overwritten.
    """
    files = []
    changes = []
    seen = set()
    for spec in catalog.get('files', ()):
        if spec.get('kind') != 'plugin-records' or spec.get('path', '').casefold() != 'spare.esp':
            files.append(spec)
            continue
        mappings = []
        for entry in spec.get('mappings', ()):
            key = (str(entry.get('owner', '')).casefold(),
                   str(entry.get('id', '')).casefold())
            target = BY_KEY.get(key)
            if target is None:
                mappings.append(entry)
                continue
            if key in seen:
                raise ValueError('Duplicate SPARE casing identity: ' + repr(key))
            seen.add(key)
            source, old, new = target
            if (entry.get('signature') != 'MISC' or entry.get('field') != 'FULL'
                    or entry.get('path') != 'FULL' or entry.get('source') != source):
                raise ValueError('SPARE casing source identity drift: ' + repr(key))
            present = entry.get('dest')
            if present not in (old, new):
                raise ValueError('Unreviewed SPARE casing destination: ' + repr(key))
            if present == new:
                mappings.append(entry)
                continue
            revised = dict(entry)
            revised['dest'] = new
            revised['previous_dests'] = sorted(set(entry.get('previous_dests') or ()) | {old})
            mappings.append(revised)
            changes.append({'plugin': spec['path'], 'owner': key[0],
                            'id': key[1], 'source': source, 'from': old, 'to': new})
        files.append({**spec, 'mappings': mappings})
    return {**catalog, 'files': files}, changes
