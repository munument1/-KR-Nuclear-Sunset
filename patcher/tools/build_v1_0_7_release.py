"""Build v1.0.7 from pinned official v1.0.6 resources and current source.

Rebuilds both onedir executables. No publication, installation or game execution.
Translation payloads stay byte-identical; only catalog release metadata changes.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import nskr
from tools.build_issue13_candidate import BASE_SHA256
from tools.build_v1_0_5_folder_release import checked_zip,checked_path,compile_program,check_binary,package_zip,validate_payloads,unpack

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build(base,work):
    assert nskr.VERSION=='1.0.7'
    base,work=Path(base).resolve(),Path(work).resolve()
    if sha(base)!=BASE_SHA256:raise ValueError('Official v1.0.6 ZIP checksum mismatch')
    if work.exists():raise FileExistsError(work)
    if work.is_relative_to(Path(r'C:\Modlists').resolve()):raise ValueError('Build outside game installations')
    package=work/'package';package.mkdir(parents=True)
    with zipfile.ZipFile(base) as z:
        entries=checked_zip(z)
        original={n:hashlib.sha256(z.read(n)).hexdigest() for n in entries if n.startswith('TranslationData/')}
        for name in entries:
            if name.startswith(('_internal/','worker-runtime/')) or name in {'NuclearSunsetKoreanPatcher.exe','NSKRXEditWorker.exe'}:continue
            target=checked_path(package,name);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
    if any(sha(package/n)!=h for n,h in original.items()):raise ValueError('Baseline extraction mismatch')
    catalog_path=package/'TranslationData/catalog.json'
    catalog=json.loads(catalog_path.read_text('utf-8-sig'))
    catalog.update(version=nskr.VERSION,packaging='folder',channel='release',translation_ready=True)
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    validate_payloads(package,catalog)
    sources=sorted(ROOT.glob('nskr*.py'))+[ROOT/'ns_inventory.py']
    sources += [ROOT/'tools'/n for n in ('loose_translation.py','audit_issue11_compiled_scripts.py','tes4_text_scan.py','build_issue13_candidate.py','build_v1_0_5_folder_release.py','build_v1_0_7_release.py')]
    snapshot=package/'Licenses-and-Source/NuclearSunset-Patcher-v1.0.7';manifest={}
    for p in sources:
        rel=p.relative_to(ROOT).as_posix();target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target);manifest[rel]=sha(p)
    (snapshot/'SOURCE-SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    for source,name in [(ROOT/'README.md','README.md'),(ROOT/'docs/releases/v1.0.7.md','RELEASE-NOTES.md'),
                        (ROOT.parent/'translations/docs/main/korean-patch.md','INSTALL.md')]:shutil.copy2(source,package/name)
    # Remove obsolete candidate instructions only within this new build folder.
    obsolete=package/'ISSUE13-READ-ME.md'
    if obsolete.is_file():obsolete.unlink()
    compile_program(work,package,'NSKRXEditWorker','nskr_xedit_worker.py','worker-runtime',windowed=False)
    compile_program(work,package,'NuclearSunsetKoreanPatcher','nskr_gui.py','_internal',windowed=True)
    binary_check=check_binary(package)
    for source in sources:
        if sha(source)!=manifest[source.relative_to(ROOT).as_posix()]:raise ValueError('Source changed during build')
    for name,digest in original.items():
        if name!='TranslationData/catalog.json' and sha(package/name)!=digest:raise ValueError('Translation payload changed')
    output=work/'output';output.mkdir()
    full=output/'NuclearSunset-Korean-Patcher-v1.0.7.zip';data=output/'NuclearSunset-TranslationData-v1.0.7.zip'
    package_zip(package,full,('',));package_zip(package,data,('TranslationData','Licenses-and-Source'))
    with zipfile.ZipFile(full) as z:
        if z.testzip():raise ValueError('Full archive CRC failed')
        extracted=work/'zip-test';extracted.mkdir();unpack(z,extracted)
        with zipfile.ZipFile(data) as dz:
            if dz.testzip():raise ValueError('TranslationData archive CRC failed')
            for name in checked_zip(dz):
                if dz.read(name)!=z.read(name):raise ValueError('Standalone data differs from full package')
    extracted_check=check_binary(extracted)
    artifacts=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in (full,data)]
    (output/'SHA256SUMS.txt').write_text(''.join(f"{a['sha256']}  {a['file']}\n" for a in artifacts),encoding='ascii')
    report={'version':nskr.VERSION,'base_sha256':BASE_SHA256,'unchanged_payloads':len(original)-1,
            'catalog_payloads_verified':validate_payloads(package,catalog),'source_snapshot':manifest,
            'binary_check':binary_check,'extracted_check':extracted_check,'artifacts':artifacts,
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    (output/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.base,a.work),ensure_ascii=False,indent=2))
