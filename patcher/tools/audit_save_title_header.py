"""Read-only Fallout New Vegas .fos save title/header encoding diagnostics.

Reads only the uncompressed save header (never rewrites .fos). Its purpose is
to determine whether a broken Level <Karma title> is already corrupt in
the saved bytes or is corrupted only during UI display.
The format offsets are from nrnelson/fnv-save-explorer SPEC.md section 4a,
independently verified on existing FNV saves.

Usage: python tools/audit_save_title_header.py "path/to/save.fos"
No filename, player name or location is printed to reduce information exposure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

SIGNATURE = b'FO3SAVEGAME'
DELIM = 0x7C
HEADER_BOUND = 16384


def decode_checks(data: bytes):
    results = {}
    for encoding in ('utf-8', 'cp949', 'cp1252'):
        try:
            text = data.decode(encoding, errors='strict')
            results[encoding] = {'valid': True, 'text': text,
                                 'roundtrip': text.encode(encoding) == data}
        except UnicodeError:
            results[encoding] = {'valid': False}
    return results


def inspect_header(buf: bytes):
    """Decode only a bounded copy of the save header, never any game state."""
    if len(buf) < 96 or not buf.startswith(SIGNATURE):
        raise ValueError('Invalid Fallout New Vegas .fos header')
    header_size, version = struct.unpack_from('<II', buf, 11)
    if version != 0x30:
        raise ValueError('Unsupported save header version')
    limit = 15 + header_size
    if not (96 < limit <= HEADER_BOUND and len(buf) >= limit):
        raise ValueError('Truncated/oversized save header')
    pos = 0x13
    def sep():
        nonlocal pos
        if pos >= limit or buf[pos] != DELIM:
            raise ValueError('Missing .fos header separator')
        pos += 1
    def integer():
        nonlocal pos
        if pos + 4 > limit:
            raise ValueError('Truncated save header integer')
        n = struct.unpack_from('<I',buf,pos)[0]
        pos += 4
        sep()
        return n
    def string():
        nonlocal pos
        if pos + 2 > limit:
            raise ValueError('Truncated save string length')
        length = struct.unpack_from('<H',buf,pos)[0]
        pos += 2
        sep()
        if length > 4096 or pos + length >= limit:
            raise ValueError('Unreasonable save string length')
        value = buf[pos:pos+length]
        pos += length
        sep()
        return value
    sep()
    language = buf[pos:pos+64].rstrip(b'\x00')
    pos += 64
    sep()  # NV saves contain a '|' delimiter after the 64-byte language field.
    width, height, save_number = integer(), integer(), integer()
    # Header metadata stores its own name/title/level/location separate from UI.
    name, title = string(), string()
    level = integer()
    location, playtime = string(), string()
    if pos != limit:
        raise ValueError('Save header bytes not consumed exactly')
    return {
        'schema': 'fnv-save-title-readonly-v1',
        'header_version': version, 'header_size': header_size,
        'screen_dimensions': [width,height],
        'save_number': save_number,
        'language': language.decode('ascii', errors='replace'),
        'level': level,
        'title': {
            'length': len(title), 'hex': title.hex(),
            'encoding_check': decode_checks(title),
            'has_non_ascii': any(n > 127 for n in title)
        },
        'name_is_non_ascii': any(n > 127 for n in name),
        'location_is_non_ascii': any(n > 127 for n in location),
        'privacy': 'Player name, save location and filename are not printed',
        'read_only': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('save', type=Path)
    args = parser.parse_args()
    with args.save.open('rb') as source:
        buf = source.read(HEADER_BOUND + 1)
    result = inspect_header(buf)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
