"""Build a transparent folder release from the verified v1.0.3 resources.

Both programs use PyInstaller onedir, with external translation data and DLLs.
Corresponding tNVSE source remains available as ordinary files, not nested ZIPs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from tools.repack_pretendard_release import normalize_archive

BASE_SHA256 = '960730db44f03e626bee68f57c7c2929893d5844948de398782d4c1e8a92b324'


def unpack_plain(archive, destination):
    """Expand a known archive as regular files while keeping paths contained."""
    count = 0
    for item in archive.infolist():
        relative = item.filename.replace('\\', '/')
        target = nskr.contained(destination, relative)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
            count += 1
    return count


def expand_python_library(folder):
    # Standard Python import paths also include the onedir runtime directory.
    # Keep its standard-library modules as ordinary files for archive scanners.
    for archive in list(folder.rglob('base_library.zip')):
        with zipfile.ZipFile(archive) as contents:
            unpack_plain(contents, archive.parent)
        archive.unlink()


def check_program(exe, *args):
    subprocess.run([str(exe.resolve()), *map(str, args)], check=True, timeout=120,
                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


def build(base, work, output):
    if nskr.sha256(base) != BASE_SHA256:
        raise ValueError('Expected verified v1.0.3 base ZIP')
    if work.exists():
        raise FileExistsError(work)
    work.mkdir(parents=True)
    output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    with zipfile.ZipFile(base) as archive:
        old_exe = work / 'v1.0.3.exe'
        old_exe.write_bytes(archive.read('NuclearSunsetKoreanPatcher.exe'))
        outer = {n: archive.read(n) for n in archive.namelist()
                 if n.startswith('Licenses-and-Source/') and not n.endswith('/')}
    original = normalize_archive(old_exe)
    package = work / 'package'
    package.mkdir()
    for relative, raw in original.items():
        if relative.startswith(('TranslationData/', 'Backend/')):
            target = nskr.contained(package, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    for relative, raw in outer.items():
        target = nskr.contained(package, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    data = package / 'TranslationData'
    catalog_path = data / 'catalog.json'
    catalog = nskr.read_json(catalog_path)
    source_assets = [a for a in catalog['font_bundle']['assets']
                     if a['payload'].lower().endswith('.zip')]
    source_files = 0
    for item in source_assets:
        source = nskr.contained(data, item['payload'])
        if nskr.sha256(source) != item['payload_sha256']:
            raise ValueError('Corresponding source ZIP hash mismatch')
        destination = package / 'Licenses-and-Source' / Path(item['payload']).stem
        with zipfile.ZipFile(source) as archive:
            source_files += unpack_plain(archive, destination)
        # Corresponding source is distributed beside the program, not copied
        # into the game's font mod by the font bundle.
        catalog['font_bundle']['assets'].remove(item)
        source.unlink()
    for path in list((package / 'Licenses-and-Source').rglob('*.zip')):
        # These are the same corresponding sources extracted above.
        path.unlink()
    catalog['packaging'] = 'folder'
    catalog['version'] = nskr.VERSION
    nskr.write_json(catalog_path, catalog)

    def compile_program(name, source, windowed=False, manifest=None, contents='_internal'):
        args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--onedir', '--noupx',
                '--name', name, '--contents-directory', contents,
                '--distpath', str(work/'compiled'), '--workpath', str(work/'build'/name),
                '--specpath', str(work/'spec'), '--windowed' if windowed else '--console']
        if manifest:
            args += ['--manifest', str(root/manifest)]
        subprocess.run(args + [str(root/source)], cwd=root, check=True)
        built = work/'compiled'/name
        expand_python_library(built)
        shutil.copytree(built, package, dirs_exist_ok=True)
    compile_program('NSKRXEditWorker', 'nskr_xedit_worker.py',
                    manifest='tools/xedit_worker_utf8.manifest', contents='worker-runtime')
    compile_program('NuclearSunsetKoreanPatcher', 'nskr_gui.py', windowed=True)
    for name in ('README.md',):
        shutil.copy2(root/name, package/name)
    shutil.copy2(root.parent/'translations/docs/main/korean-patch.md', package/'INSTALL.md')
    shutil.copy2(root.parent/'docs/releases/v1.0.4.md', package/'RELEASE-NOTES.md')
    check_program(package/'NuclearSunsetKoreanPatcher.exe', '--package-check')

    # Translation dictionaries, fonts, native DLLs and the UI ESP must retain
    # exactly the released bytes; only the packaging/source-archive entry changes.
    changed_resources = []
    for relative, raw in original.items():
        if not relative.startswith(('TranslationData/', 'Backend/')):
            continue
        target = nskr.contained(package, relative)
        if not target.exists() or target.read_bytes() != raw:
            changed_resources.append(relative)
    expected = ['TranslationData/catalog.json'] + ['TranslationData/'+a['payload'] for a in source_assets]
    if set(changed_resources) != set(expected):
        raise RuntimeError('Unexpected resource changes: '+repr(changed_resources))
    assets = []
    for name, folders in ((f'NuclearSunset-Korean-Patcher-v{nskr.VERSION}.zip', [package]),
                          (f'NuclearSunset-TranslationData-v{nskr.VERSION}.zip',
                           [data, package/'Licenses-and-Source'])):
        target = output/name
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for folder in folders:
                for path in sorted(folder.rglob('*')):
                    if path.is_file():
                        archive.write(path, path.relative_to(package).as_posix())
        assets.append(target)
    # Exercise the ZIP as users receive it, including the flattened stdlib.
    extracted = work/'zip-test'
    with zipfile.ZipFile(assets[0]) as archive:
        unpack_plain(archive, extracted)
    check_program(extracted/'NuclearSunsetKoreanPatcher.exe', '--package-check')
    (output/'SHA256SUMS.txt').write_text(''.join(
        nskr.sha256(p)+'  '+p.name+'\n' for p in assets), encoding='ascii')
    report = {'version':nskr.VERSION,'packaging':'folder','base_sha256':nskr.sha256(base),
              'corresponding_source_files':source_files,'changed_resources':changed_resources,
              'package_check':True,'extracted_zip_package_check':True,
              'assets':[{'name':p.name,'bytes':p.stat().st_size,'sha256':nskr.sha256(p)} for p in assets]}
    (output/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    build(a.base.resolve(),a.work.resolve(),a.output.resolve())
