"""Recover v1.0.1 resources, fix terminal ASCII, and package v1.0.2."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile
import hashlib

from PyInstaller.archive.readers import CArchiveReader
import nskr
from tools.fix_hacking_font import apply
from tools.verify_hacking_font import verify

EXE = 'NuclearSunsetKoreanPatcher.exe'
BASE = 'NuclearSunset-Korean-Patcher-v1.0.1.zip'


def prepare(release: Path, work: Path) -> None:
    expected = {}
    for line in (release / 'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.lstrip('*')] = digest.lower()
    if nskr.sha256(release / BASE) != expected[BASE]:
        raise ValueError('Base release checksum mismatch')
    if work.exists():
        raise FileExistsError(work)
    work.mkdir(parents=True)
    with zipfile.ZipFile(release / BASE) as archive:
        if archive.testzip():
            raise ValueError('Base ZIP corrupt')
        (work / EXE).write_bytes(archive.read(EXE))
    reader = CArchiveReader(str(work / EXE))
    for name in reader.toc:
        relative = name.replace('\\', '/')
        if relative.startswith(('TranslationData/', 'Backend/')) or relative == 'NSKRXEditWorker.exe':
            path = nskr.contained(work, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(reader.extract(name))
    apply(work / 'TranslationData')


def package(release: Path, work: Path, exe: Path, output: Path) -> None:
    verify(work / EXE, exe)
    # Preserve the original worker and all other installer ZIP members.
    old_reader, new_reader = CArchiveReader(str(work / EXE)), CArchiveReader(str(exe))
    if old_reader.extract('NSKRXEditWorker.exe') != new_reader.extract('NSKRXEditWorker.exe'):
        raise ValueError('Worker binary changed')
    output.mkdir(parents=True, exist_ok=True)
    patcher = output / 'NuclearSunset-Korean-Patcher-v1.0.2.zip'
    data = output / 'NuclearSunset-TranslationData-v1.0.2.zip'
    with zipfile.ZipFile(release / BASE) as base, zipfile.ZipFile(patcher, 'w', zipfile.ZIP_DEFLATED) as dest:
        for name in base.namelist():
            dest.writestr(name, exe.read_bytes() if name == EXE else base.read(name))
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as dest:
        for path in sorted((work / 'TranslationData').rglob('*')):
            if path.is_file():
                dest.write(path, 'TranslationData/' + path.relative_to(work / 'TranslationData').as_posix())
    for path in (patcher, data):
        with zipfile.ZipFile(path) as archive:
            if archive.testzip():
                raise ValueError('Output ZIP corrupt')
    (output / 'SHA256SUMS.txt').write_text(''.join(
        f'{nskr.sha256(p)}  {p.name}\n' for p in (patcher, data)), encoding='ascii')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'package'])
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.release, args.work)
    else:
        package(args.release, args.work, args.exe, args.output)
