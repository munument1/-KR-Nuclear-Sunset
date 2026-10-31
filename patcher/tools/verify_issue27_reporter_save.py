"""Read-only verification of issue #27 save header with pinned supplied attachment.

No user save bytes, names or locations are copied to repo/release or printed.
"""
from __future__ import annotations
import hashlib,io,json,sys,zipfile
from pathlib import Path
from tools.audit_save_title_header import inspect_header

ARCHIVE_SHA256 = 'bba4f84064ecd1aabe63348b6e888e9fe34e6fc81ce3fd5aaee2d26e5e164151'
SAVE_SHA256 = '9f5496551dcf235604b6ebc53c8bce6981fc899bf076aba5cbeb0385cbbef1e8'
EXPECTED_TITLE_HEX = 'ebb3bced8ab820eab1b0eca3bcec9e90'


def verify(path: Path):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Supplied archive SHA mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        saves=[entry for entry in z.infolist() if entry.filename.lower().endswith('.fos')]
        if len(saves)!=1 or saves[0].file_size > 32*1024*1024:
            raise ValueError('Expected exactly one bounded Fallout New Vegas save')
        with z.open(saves[0]) as stream:
            header=stream.read(16385)
            sha=hashlib.sha256()
            sha.update(header)
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                sha.update(chunk)
            if sha.hexdigest()!=SAVE_SHA256:
                raise ValueError('Original .fos SHA mismatch')
        data=inspect_header(header)
    title=data['title']
    if not (data['level']==1 and title['hex']==EXPECTED_TITLE_HEX and
            title['encoding_check']['utf-8']['valid'] and
            title['encoding_check']['utf-8']['text']=='볼트 거주자'):
        raise ValueError('Unexpected save title/level or encoding')
    return {'save_sha256': SAVE_SHA256,
            'level': data['level'], 'title': '볼트 거주자',
            'title_encoding': 'valid UTF-8', 'title_bytes': title['length'],
            'header_integrity':'PASS', 'unchanged':True,
            'privacy':'Names, location, save filename and body bytes not exported'}


if __name__=='__main__':
    print(json.dumps(verify(Path(sys.argv[1])), ensure_ascii=True, indent=2))
