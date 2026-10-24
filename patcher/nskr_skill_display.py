"""Korean text for JIP's runtime Big Guns description override.

JIP replaces the AVIF record text when enabling its Big Guns patch. tNVSE has
a version-gated, instruction-signature-checked adapter for JIP 57.30, and reads
this setting as UTF-8 before converting it to the selected game encoding.
"""
import re

BIG_GUNS_DESCRIPTION = ('중화기 기술은 팻 맨, 미사일 발사기, 화염방사기, 미니건, '
                        '개틀링 레이저 등 대형 무기의 전투 효율을 결정합니다.')
PROVIDERS = {'Nuclear Sunset - Korean UI Runtime Translations',
             'Nuclear Sunset - Korean Fonts for tNVSE'}

def patch_config(raw):
    text=raw.decode('utf-8-sig')
    section='';result=[];found=set()
    values={'bChangeJIPBigGunDesc':'1','sNewBigGunsDesc':'"'+BIG_GUNS_DESCRIPTION+'"'}
    for line in text.splitlines(keepends=True):
        match=re.fullmatch(r'\s*\[([^]]+)\]\s*',line.strip())
        if match:section=match[1]
        if section=='Multibyte':
            for key,value in values.items():
                match=re.fullmatch(r'([ \t]*'+key+r'[ \t]*=[ \t]*)([^\r\n]*)(\r\n|\n|\r|)',line)
                if match:
                    if key in found:raise ValueError('Duplicate Big Guns display setting')
                    found.add(key);line=match[1]+value+match[3]
        result.append(line)
    if found!=set(values):raise ValueError('Missing Big Guns display settings')
    return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+''.join(result).encode('utf-8')
