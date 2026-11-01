"""Source-pinned Korean B42 Descriptions INIs for the Nuclear Sunset Output.

Only copies verified B42 provider files into a separately staged MO2 Output.
Does not alter the original mods, profile, or ESM/ESP. The reviewed source and
translation pairs live in bundled ``nskr_b42_data`` (imported by PyInstaller).
"""
from __future__ import annotations

from collections import Counter
import hashlib
import re

from nskr_b42_data import DATA

_MARKERS = re.compile(r'%(?:\d+(?:\.\d+)?)?[A-Za-z]')


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode(raw: bytes) -> str:
    for name in ('utf-8-sig','cp1252'):
        try:
            return raw.decode(name)
        except UnicodeDecodeError:
            continue
    return raw.decode('latin-1')


def _split_ending(line: bytes):
    for ending in (b'\r\n',b'\n',b'\r'):
        if line.endswith(ending):
            return line[:-len(ending)],ending
    return line,b''


def patch_ini(raw: bytes, descriptor: dict) -> bytes:
    """Patch 1 identified INI; require exact file SHA, lines, keys and text."""
    if _sha(raw)!=descriptor['sha256']:
        raise ValueError('Unreviewed B42 original INI SHA')
    lines=raw.splitlines(keepends=True)
    result=list(lines)
    line_ids=set()
    for line_number,key,english,translation,mode in descriptor['rows']:
        index=line_number-1
        if index in line_ids or not 0<=index<len(lines):
            raise ValueError('Duplicate or missing B42 description line')
        line_ids.add(index)
        original,eol=_split_ending(lines[index])
        head,separator,value=original.partition(b'=')
        if not separator or _decode(head).strip()!=key or _decode(value).strip()!=english:
            raise ValueError('B42 source key/value drifted')
        if not translation or '\n' in translation or '\r' in translation:
            raise ValueError('Invalid B42 replacement')
        if _MARKERS.findall(english)!=_MARKERS.findall(translation):
            raise ValueError('B42 format token order/count changed')
        if mode=='strip-outer-double-quotes':
            if not english.startswith('"') or not english.endswith('"'):
                raise ValueError('B42 quote provenance is inconsistent')
            translation='"'+translation+'"'
        elif mode=='strip-outer-single-quotes':
            if not english.startswith("'") or not english.endswith("'"):
                raise ValueError('B42 quote provenance is inconsistent')
            translation="'"+translation+"'"
        elif mode!='exact':
            raise ValueError('Unexpected B42 source match class')
        prefix=value[:len(value)-len(value.lstrip(b' \t'))]
        suffix=value[len(value.rstrip(b' \t')):]
        result[index]=head+separator+prefix+translation.encode('utf-8')+suffix+eol
        if result[index]==lines[index]:
            raise ValueError('B42 approved record was not translated')
    return b''.join(result)


def finalize(installation,stage,files):
    """Extend normal patcher Output with translated B42 descriptions.

    Only active installed providers with byte-identical source INIs are used.
    Other B42 versions remain untouched, including older `[OP]` English files
    hidden by `B42 Descriptions Revised` at a higher MO2 priority.
    """
    import nskr

    enabled={name.casefold() for name in installation.mods_enabled}
    registered={row['output_path'].casefold():row for row in files}
    patched=0
    translated=0
    skipped=[]
    for entry in DATA:
        provider=entry['provider']
        if provider.casefold() not in enabled:
            continue
        virtual=provider+'/'+entry['path']
        source=nskr.contained(installation.mods,virtual)
        if not source.is_file():
            skipped.append({'provider':provider,'path':entry['path'],
                            'reason':'source_file_missing'})
            continue
        original=source.read_bytes()
        if _sha(original)!=entry['sha256']:
            skipped.append({'provider':provider,'path':entry['path'],
                            'reason':'source_file_updated_no_exact_approved_translation'})
            continue
        output_virtual='mods/'+virtual
        target=nskr.contained(stage,output_virtual)
        current_row=registered.get(output_virtual.casefold())
        if target.exists() and (not current_row or target.read_bytes()!=original):
            skipped.append({'provider':provider,'path':entry['path'],
                            'reason':'existing_staged_output_differs_from_reviewed_source'})
            continue
        data=patch_ini(original,entry)
        if _sha(source.read_bytes())!=entry['sha256']:
            raise ValueError('B42 source changed during patcher generation')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        if target.read_bytes()!=data:
            raise ValueError('B42 stage output readback mismatch')
        row=current_row if current_row is not None else {
            'path':entry['path'],
            'provider':provider,
            'output_path':output_virtual,
            'source_sha256':entry['sha256'],
            'status':'reviewed_B42_INI_copy',
        }
        row['output_sha256']=_sha(data)
        row['translated']=len(entry['rows'])
        row['b42_descriptions_translated']=len(entry['rows'])
        row['status']+='; reviewed_exact_B42_UTF8_descriptions'
        if current_row is None:
            files.append(row)
            registered[output_virtual.casefold()]=row
        patched+=1
        translated+=len(entry['rows'])
    return {'files':patched,'translated':translated,'skipped':skipped,
            'source':'bundled_exact_B42_descriptions'}
