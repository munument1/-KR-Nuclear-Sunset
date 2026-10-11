"""Read-only FalloutNV BSA UI extraction using the format documented by xTranslator.

Reference: MGuffin/xTranslator, TESVT_bsa.pas ReadDirectory/GetData.
No archive is rewritten; archive candidates are not treated as proven VFS winners.
"""
from pathlib import Path
import json
import re
import struct
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr

LEAF = re.compile(r'<([A-Za-z_][\w.-]*)\b[^>]*>([^<>]*)</\1\s*>', re.S)
COMMENT = re.compile(r'<!--.*?-->', re.S)
WORD = re.compile(r'[A-Za-z]{2,}')


def directory(path):
    with path.open('rb') as stream:
        head = stream.read(36)
        if len(head) != 36:
            raise ValueError('Truncated BSA header')
        magic, version, offset, flags, folders, total, folder_names, file_names, types = struct.unpack(
            '<4s8I', head)
        if magic != b'BSA\0' or version != 104 or offset != 36:
            raise ValueError('Expected FalloutNV BSA version 104')
        table = [struct.unpack('<QII', stream.read(16)) for _ in range(folders)]
        records = []
        filename_offset = 36 + folders * 16
        for folder_hash, count, folder_offset in table:
            stream.seek(folder_offset - file_names)
            length = stream.read(1)[0]
            name = stream.read(length).rstrip(b'\0').decode('cp1252').replace('\\', '/')
            for _ in range(count):
                file_hash, size, position = struct.unpack('<QII', stream.read(16))
                records.append((name, size, position))
            filename_offset = stream.tell()
        if len(records) != total:
            raise ValueError('BSA directory count mismatch')
        stream.seek(filename_offset)
        names = stream.read(file_names).split(b'\0')
        if len(names) < total + 1 or any(names[total:]) or any(not name for name in names[:total]):
            raise ValueError(f'BSA filename table mismatch: {path}')
        return flags, [(folder + '/' + name.decode('cp1252'), size, position)
                       for (folder, size, position), name in zip(records, names[:total])]


def payload(path, flags, size, offset):
    compressed = bool(size & 0x40000000) ^ bool(flags & 4)
    length = size & ~0x40000000
    if length > 8 * 1024 * 1024:
        raise ValueError('UI payload exceeds bounded extraction size')
    with path.open('rb') as stream:
        stream.seek(offset)
        data = stream.read(length)
    if len(data) != length:
        raise ValueError('Truncated BSA UI payload')
    if flags & 0x100:
        prefix = data[0]
        data = data[1 + prefix:]
    if compressed:
        expected = struct.unpack_from('<I', data)[0]
        if expected > 8 * 1024 * 1024:
            raise ValueError('Expanded UI payload exceeds bounded extraction size')
        data = zlib.decompress(data[4:])
        if len(data) != expected:
            raise ValueError('Expanded BSA UI length mismatch')
    return data


def main():
    installation = nskr.Installation(Path(r'C:\Modlists\NuclearSunset'), 'KR Test - h8at5ar1')
    active = {name.casefold() for name in nskr.list_lines(installation.profile_dir / 'archives.txt')}
    archives = {}
    for row in installation.archives:
        root = (installation.data if row['provider'] == 'game:Data' else
                installation.overwrite if row['provider'] == 'MO2:overwrite' else
                installation.mods / row['provider'])
        if Path(row['path']).name.casefold() in active:
            archives[Path(row['path']).name.casefold()] = root / row['path']
    output = Path(tempfile.mkdtemp(prefix='remaining-bsa-', dir=ROOT / '.local'))
    count = 0
    inspected = 0
    hashes = {}
    with (output / 'bsa_ui_candidates.jsonl').open('x', encoding='utf-8') as target:
        for archive in archives.values():
            before = archive.stat()
            flags, files = directory(archive)
            for virtual, size, position in files:
                key = virtual.casefold().lstrip('/')
                if (not key.startswith(('menus/', 'interface/', 'mcm/', 'config/', 'nvse/'))
                        or Path(key).suffix not in ('.xml', '.ini', '.json', '.txt')
                        or key in installation.providers):
                    continue
                raw = payload(archive, flags, size, position)
                inspected += 1
                try:
                    text = raw.decode('utf-8-sig')
                    encoding = 'utf-8-sig'
                except UnicodeDecodeError:
                    text = raw.decode('cp1252')
                    encoding = 'cp1252'
                if Path(key).suffix == '.xml':
                    candidates = [(match[1], match[2].strip())
                                  for match in LEAF.finditer(COMMENT.sub('', text))]
                else:
                    candidates = [('raw_line_review', line) for line in text.splitlines()
                                  if not line.lstrip().startswith((';', '#'))]
                for tag, value in candidates:
                    if not WORD.search(value) or re.fullmatch(r'&[^;]+;', value):
                        continue
                    row = {'archive': str(archive), 'path': virtual, 'tag': tag,
                           'source': value, 'encoding': encoding,
                           'kind': 'archive_literal_review', 'live_vfs_validation_required': True}
                    target.write(json.dumps(row, ensure_ascii=False) + '\n')
                    count += 1
                    if re.search(r'\bpurchases\b|\bpermanent\b', value, re.I):
                        print('REQUESTED_TERM', json.dumps(row, ensure_ascii=False), flush=True)
            after = archive.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise RuntimeError('Archive changed while being read')
    print(json.dumps({'output': str(output), 'active_archives_scanned': len(archives),
                      'non_loose_ui_files_inspected': inspected, 'candidates': count,
                      'archives_written': 0}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
