"""Build an isolated local development executable; never publish or delete a build."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from nskr_output import output_catalog
from tools.prepare_development_catalog import prepare


def build(args):
    root = Path(__file__).resolve().parents[1]
    args.destination.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix='NuclearSunset-Dev-', dir=args.destination)).resolve()
    catalog_dir = destination / 'TranslationData'
    if args.catalog is not None:
        metadata = nskr.read_json(args.catalog / 'catalog.json')
        output_catalog(metadata, development=True, scopes={'ui', 'fonts', 'plugins'})
        shutil.copytree(args.catalog, catalog_dir)
        summary = {'catalog': str(catalog_dir), **metadata.get('candidate_summary', {}),
                   'translation_ready': False}
    else:
        summary = prepare(args.review, args.sst, nskr.Installation(args.mo2, args.profile),
                          catalog_dir, args.runtime)
    output_catalog(nskr.read_json(catalog_dir / 'catalog.json'), development=True)
    for relative in ('XEditLib.dll', 'FalloutNV.Hardcoded.dat', 'icudtl.dat', 'LICENSE'):
        if not (args.backend / relative).is_file():
            raise FileNotFoundError(args.backend / relative)

    def run(arguments):
        subprocess.run([sys.executable, '-m', 'PyInstaller', *arguments],
                       cwd=root, check=True)

    run(['--noconfirm', '--onefile', '--console', '--name', 'NSKRXEditWorker',
         '--manifest', str(root / 'tools/xedit_worker_utf8.manifest'),
         '--distpath', str(destination), '--workpath', str(destination / 'worker-build'),
         '--specpath', str(destination / 'spec'), str(root / 'nskr_xedit_worker.py')])
    run(['--noconfirm', '--onefile', '--windowed', '--name', 'NuclearSunsetKoreanPatcher',
         '--distpath', str(destination), '--workpath', str(destination / 'patcher-build'),
         '--specpath', str(destination / 'spec'),
         '--add-data', f'{catalog_dir};TranslationData',
         '--add-binary', f'{destination / "NSKRXEditWorker.exe"};.',
         '--add-binary', f'{args.backend / "XEditLib.dll"};Backend',
         '--add-data', f'{args.backend / "FalloutNV.Hardcoded.dat"};Backend',
         '--add-data', f'{args.backend / "icudtl.dat"};Backend',
         '--add-data', f'{args.backend / "LICENSE"};Backend',
         str(root / 'nskr_gui.py')])
    executable = destination / 'NuclearSunsetKoreanPatcher.exe'
    with executable.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {**summary, 'executable': str(executable), 'sha256': digest,
            'bytes': executable.stat().st_size, 'released': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path)
    parser.add_argument('--sst', type=Path)
    parser.add_argument('--catalog', type=Path)
    parser.add_argument('--mo2', type=Path, required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--backend', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--runtime', type=Path)
    args = parser.parse_args()
    if args.catalog is None and (args.review is None or args.sst is None):
        parser.error('--catalog 또는 --review와 --sst가 필요합니다.')
    print(json.dumps(build(args), ensure_ascii=False))


if __name__ == '__main__':
    main()
