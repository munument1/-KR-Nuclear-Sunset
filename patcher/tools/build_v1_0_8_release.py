"""Rebuild v1.0.8 from verified v1.0.7, reviewed tNVSE source and Win32 DLL."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import nskr
from nskr_runtime_override_data import ENGINE_LOCK
from tools.build_v1_0_5_folder_release import checked_zip,checked_path,compile_program,check_binary,package_zip,validate_payloads,unpack
BASE_SHA='3c2c4c9925511c794b93ae881e1b4c2f389bc8a4ec61491e26a1efa917807633'
DLL_SHA='0bb5c3c5387fb76679a1bef7dbdd2bced05c7fa9e849d3d80613d5814b58c52f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(base,work,native):
    assert nskr.VERSION=='1.0.8'
    base,work,native=map(lambda p:Path(p).resolve(),(base,work,native))
    if sha(base)!=BASE_SHA:raise ValueError('v1.0.7 checksum mismatch')
    dll=native/'build/bin/Release/tnvse.dll'
    if sha(dll)!=DLL_SHA:raise ValueError('Unreviewed native build')
    if work.exists():raise FileExistsError(work)
    if work.is_relative_to(Path(r'C:\Modlists').resolve()):raise ValueError('Build outside game')
    package=work/'package';package.mkdir(parents=True)
    with zipfile.ZipFile(base) as z:
        original={}
        for name in checked_zip(z):
            if name.startswith(('_internal/','worker-runtime/')) or name in {'NuclearSunsetKoreanPatcher.exe','NSKRXEditWorker.exe'}:continue
            target=checked_path(package,name);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
            if name.startswith('TranslationData/'):original[name]=sha(target)
    data=package/'TranslationData';catalog_path=data/'catalog.json'
    catalog=json.loads(catalog_path.read_text('utf-8-sig'))
    dictionary=data/'runtime_ui/NSKR_UI_Translations.json'
    entries=json.loads(dictionary.read_text('utf-8-sig'))
    if any(e['original']==ENGINE_LOCK[0] for e in entries):raise ValueError('Duplicate lock entry')
    entries.append(dict(zip(('original','translation'),ENGINE_LOCK)))
    dictionary.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assets=catalog['font_bundle']['assets']+[f for m in catalog['runtime_mods'] for f in m['files']]
    changed={'TranslationData/catalog.json','TranslationData/runtime_ui/NSKR_UI_Translations.json'}
    for asset in assets:
        target=data/asset['payload']
        if asset['path'].casefold().endswith('/tnvse.dll'):
            shutil.copy2(dll,target);changed.add('TranslationData/'+asset['payload'])
        asset['payload_sha256']=sha(target)
    catalog.update(version=nskr.VERSION,channel='release',translation_ready=True,
                   game_validation='pending_same_save_reporter_verification')
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    validate_payloads(package,catalog)
    native_dst=package/'Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE'
    # Retain the complete GPL source/dependencies shipped by the baseline.
    for rel in ('font/encoding.cpp','font/encoding.h','font/text_hooks.cpp','game/game_hooks.cpp','dictionary/dictionary_translate.cpp'):
        shutil.copy2(native/'source/tnvse/Src'/rel,native_dst/'tnvse/Src'/rel)
    evidence=package/'Licenses-and-Source/tNVSE-v1.0.8-validation'
    evidence.mkdir()
    for name in ('source.patch','source-changes.json','binary-verification.json','dependency-packages.json','README.md'):
        shutil.copy2(native/name,evidence/name)
    shutil.copy2(native/'tests/results.json',evidence/'native-tests.json')
    sources=sorted(ROOT.glob('nskr*.py'))+[ROOT/'ns_inventory.py']
    sources+=sorted((ROOT/'tools').glob('*.py'))
    snapshot=package/'Licenses-and-Source/NuclearSunset-Patcher-v1.0.8';manifest={}
    for p in sources:
        rel=p.relative_to(ROOT).as_posix();target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target);manifest[rel]=sha(p)
    shutil.copytree(ROOT/'tests',snapshot/'tests',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT/'native',snapshot/'native',
                    ignore=shutil.ignore_patterns('__pycache__','*.exe','*.obj','*.bin','*.cmd','*.log','regression.cpp'))
    (snapshot/'SOURCE-SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    for source,name in [(ROOT/'README.md','README.md'),(ROOT/'docs/releases/v1.0.8.md','RELEASE-NOTES.md'),
                        (ROOT.parent/'translations/docs/main/korean-patch.md','INSTALL.md')]:shutil.copy2(source,package/name)
    compile_program(work,package,'NSKRXEditWorker','nskr_xedit_worker.py','worker-runtime',windowed=False)
    compile_program(work,package,'NuclearSunsetKoreanPatcher','nskr_gui.py','_internal',windowed=True)
    binary_check=check_binary(package)
    for p in sources:
        if sha(p)!=manifest[p.relative_to(ROOT).as_posix()]:raise ValueError('Source changed during build')
    for name,digest in original.items():
        if name not in changed and sha(package/name)!=digest:raise ValueError('Unexpected payload change: '+name)
    output=work/'output';output.mkdir()
    full=output/'NuclearSunset-Korean-Patcher-v1.0.8.zip';datazip=output/'NuclearSunset-TranslationData-v1.0.8.zip'
    package_zip(package,full,('',));package_zip(package,datazip,('TranslationData','Licenses-and-Source'))
    with zipfile.ZipFile(full) as z:
        if z.testzip():raise ValueError('CRC failed')
        extracted=work/'zip-test';extracted.mkdir();unpack(z,extracted)
        with zipfile.ZipFile(datazip) as dz:
            if dz.testzip():raise ValueError('Data CRC failed')
            for name in checked_zip(dz):
                if dz.read(name)!=z.read(name):raise ValueError('Data/full mismatch')
    extracted_check=check_binary(extracted)
    artifacts=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in (full,datazip)]
    (output/'SHA256SUMS.txt').write_text(''.join(f"{a['sha256']}  {a['file']}\n" for a in artifacts),encoding='ascii')
    report={'version':nskr.VERSION,'base_sha256':BASE_SHA,'native_sha256':DLL_SHA,
            'changed_payloads':sorted(changed),'payloads_verified':validate_payloads(package,catalog),
            'binary_check':binary_check,'extracted_check':extracted_check,'artifacts':artifacts,
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    (output/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--work',required=True);p.add_argument('--native',required=True)
    a=p.parse_args();build(a.base,a.work,a.native)
