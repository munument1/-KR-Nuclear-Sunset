"""Rebuild a fully source-backed v1.1.1 patcher from official v1.1.0.

Strictly preserves all v1.1.0 native DLLs, translations, font binaries,
other scripts and assets. Only the added B42 translation processor, source
snapshot, documentation, binaries and catalog version may change.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nskr
from tools.build_v1_0_5_folder_release import (
    checked_zip, unpack, compile_program, check_binary,
    validate_payloads, package_zip,
)

VERSION = '1.1.1'
BASE_VERSION = '1.1.0'
BASE_SHA = 'd376e152577554e38b3876d2d197d428aeaa814b1237bed90eb3fcc8f860b12f'
BASE_NAME = 'NuclearSunset-Korean-Patcher-v1.1.0.zip'
CHANGE_PATHS = ('nskr.py','nskr_output.py','nskr_b42_data.py',
                'nskr_b42_descriptions.py','tests/test_b42_descriptions.py')

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def run(base, work):
    base,work=Path(base).resolve(),Path(work).resolve()
    if nskr.VERSION != VERSION:
        raise ValueError('Release source version must be 1.1.1')
    if not base.is_file() or base.name!=BASE_NAME or sha(base)!=BASE_SHA:
        raise ValueError('Official v1.1.0 SHA-pinned full ZIP required')
    if work.exists():
        raise FileExistsError('Refusing to overwrite an existing release work folder')
    package=work/'package'
    package.mkdir(parents=True)
    with zipfile.ZipFile(base) as archive:
        names=checked_zip(archive)
        if archive.testzip() is not None:
            raise ValueError('Baseline ZIP CRC failure')
        unpack(archive,package)
    baseline={name:sha(package/name) for name in names}
    catalog_path=package/'TranslationData/catalog.json'
    catalog=nskr.read_json(catalog_path)
    if catalog.get('version')!=BASE_VERSION or catalog.get('channel')!='release':
        raise ValueError('Unexpected v1.1.0 catalog')
    for name in CHANGE_PATHS:
        source=ROOT/name
        if not source.is_file():
            raise FileNotFoundError(source)
    baseline_source=package/'Licenses-and-Source/NuclearSunset-Patcher-v1.1.0'
    changed=[]
    for name in CHANGE_PATHS:
        old=baseline_source/name
        if name not in ('nskr_b42_data.py','nskr_b42_descriptions.py',
                        'tests/test_b42_descriptions.py') and not old.is_file():
            raise FileNotFoundError(old)
        old_sha=sha(old) if old.is_file() else None
        new_sha=sha(ROOT/name)
        if old_sha==new_sha:
            raise ValueError('Expected changed source but unchanged: '+name)
        changed.append({'path':name,'before_sha256':old_sha,'after_sha256':new_sha})
    if not (ROOT/'nskr_b42_data.py').is_file():
        raise FileNotFoundError('Reviewed B42 catalog missing')
    import nskr_b42_data
    data=nskr_b42_data.DATA
    if (len(data),sum(len(row['rows']) for row in data))!=(118,2992):
        raise ValueError('B42 coverage does not match verified original source')

    # Version bump only; no existing game asset, full translation dictionary,
    # renderer binary or tNVSE source may change.
    catalog['version']=VERSION
    prior_validation=catalog.get('game_validation','')
    catalog['game_validation']=prior_validation+'; B42_INI_2992_static_verified_game_not_run'
    nskr.write_json(catalog_path,catalog)
    validate_payloads(package,catalog)

    source_snap=package/'Licenses-and-Source'/f'NuclearSunset-Patcher-v{VERSION}'
    if source_snap.exists():
        raise FileExistsError(source_snap)
    hashes={}
    sources=sorted(ROOT.glob('nskr*.py'))+[ROOT/'ns_inventory.py']
    sources+=sorted((ROOT/'tools').glob('*.py'))
    for source in sources:
        relative=source.relative_to(ROOT).as_posix()
        target=source_snap/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        hashes[relative]=sha(source)
    shutil.copytree(ROOT/'tests',source_snap/'tests',
                    ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT/'native',source_snap/'native',
                    ignore=shutil.ignore_patterns('__pycache__','*.exe','*.obj','*.bin','*.cmd','*.log'))
    (source_snap/'SOURCE-SHA256.json').write_text(
        json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    for source,dest in (
        (ROOT/'README.md', package/'README.md'),
        (ROOT/'docs/releases/v1.1.1.md',package/'RELEASE-NOTES.md'),
        (ROOT.parent/'translations/docs/main/korean-patch.md',package/'INSTALL.md'),
    ):
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source,dest)

    for name in ('NuclearSunsetKoreanPatcher.exe','NSKRXEditWorker.exe'):
        (package/name).unlink()
    for name in ('_internal','worker-runtime'):
        shutil.rmtree(package/name)
    compile_program(work,package,'NSKRXEditWorker','nskr_xedit_worker.py',
                    'worker-runtime',windowed=False)
    compile_program(work,package,'NuclearSunsetKoreanPatcher','nskr_gui.py',
                    '_internal',windowed=True)
    for name,h in hashes.items():
        if sha(ROOT/name)!=h or sha(source_snap/name)!=h:
            raise ValueError('Source changed during compilation: '+name)
    compiled=check_binary(package)

    allow={'TranslationData/catalog.json','README.md','RELEASE-NOTES.md',
           'INSTALL.md','NSKRXEditWorker.exe','NuclearSunsetKoreanPatcher.exe'}
    for name,h in baseline.items():
        if name in allow or name.startswith(('_internal/','worker-runtime/')):
            continue
        if sha(package/name)!=h:
            raise ValueError('Unrelated release payload changed: '+name)

    output=work/'output'
    output.mkdir()
    full=output/f'NuclearSunset-Korean-Patcher-v{VERSION}.zip'
    data_zip=output/f'NuclearSunset-TranslationData-v{VERSION}.zip'
    package_zip(package,full,('',))
    package_zip(package,data_zip,('TranslationData','Licenses-and-Source'))
    with zipfile.ZipFile(full) as f,zipfile.ZipFile(data_zip) as d:
        if f.testzip() is not None or d.testzip() is not None:
            raise ValueError('Archive CRC failure')
        for name in checked_zip(d):
            if d.read(name)!=f.read(name):
                raise ValueError('Standalone TranslationData/full ZIP mismatch: '+name)
        extracted=work/'unpacked'
        extracted.mkdir()
        unpack(f,extracted)
    extracted_result=check_binary(extracted)
    artifacts=[{'file':a.name,'bytes':a.stat().st_size,'sha256':sha(a)}
               for a in (full,data_zip)]
    (output/'SHA256SUMS.txt').write_text(''.join(
        f"{a['sha256']}  {a['file']}\n" for a in artifacts),encoding='ascii')
    report={
        'version':VERSION,'baseline_version':BASE_VERSION,'baseline_sha256':BASE_SHA,
        'unchanged_files_checked':len(baseline),'source_changes':changed,
        'b42_files':len(data),'b42_descriptions':sum(len(row['rows']) for row in data),
        'b42_game_verified':False,'native_dll_sha256':sha(package/'TranslationData/nskr-tNVSE-korean-fonts/tnvse.dll'),
        'binary_selfcheck':compiled,'extracted_binary_selfcheck':extracted_result,
        'source_snapshot_sha_count':len(hashes),
        'game_validation':catalog['game_validation'],'artifacts':artifacts,
    }
    (output/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    run(args.base,args.work)
