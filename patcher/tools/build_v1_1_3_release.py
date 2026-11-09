"""Build 1.1.3 from the exact 1.1.2 release and successful native CI artifact."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import nskr
from tools.build_v1_0_5_folder_release import checked_zip,unpack,compile_program,check_binary,validate_payloads,package_zip

BASE_SHA='4c121b4ca2100d322e21005b44d9fbf0a538ee85a6753ceacf3521e05e3a7d16'
NATIVE_PREFIX='Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE/'
CI_URL='https://github.com/munument1/-KR-Nuclear-Sunset/actions/runs/42543333821'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(base,work,native):
 base,work,native=[Path(x).resolve() for x in (base,work,native)]
 if nskr.VERSION!='1.1.3' or sha(base)!=BASE_SHA:raise ValueError('Pinned release/version mismatch')
 if work.exists():raise FileExistsError(work)
 dll=native/'tnvse.dll';expected=(native/'SHA256SUMS.txt').read_text().split()[0]
 if sha(dll)!=expected:raise ValueError('Native CI artifact hash mismatch')
 native_results=json.loads((native/'native-test-results.json').read_text())
 if any(x['exit_code'] for x in native_results):raise ValueError('Native tests failed')
 package=work/'package';package.mkdir(parents=True)
 with zipfile.ZipFile(base) as z:
  unpack(z,package);baseline={n:hashlib.sha256(z.read(n)).hexdigest() for n in checked_zip(z)}
 # Exact corresponding native sources are checked against the successful CI ZIP.
 native_changed=[]
 with zipfile.ZipFile(native/'GPL-corresponding-source.zip') as source:
  for name,old_hash in baseline.items():
   if not name.startswith(NATIVE_PREFIX):continue
   rel=name[len(NATIVE_PREFIX):];data=source.read(rel)
   if hashlib.sha256(data).hexdigest()!=old_hash:
    if rel not in ('tnvse/Src/font/encoding.cpp','tnvse/Src/font/encoding.h'):
     raise ValueError('Unrelated native source changed: '+rel)
    if data!=(ROOT/'native/tnvse/Src'/rel[len('tnvse/Src/'):]).read_bytes():
     raise ValueError('Native CI and current source differ')
    (package/name).write_bytes(data);native_changed.append(name)
 if len(native_changed)!=2:raise ValueError('Expected exactly two native source changes')
 catalog_path=package/'TranslationData/catalog.json';catalog=nskr.read_json(catalog_path)
 if catalog['version']!='1.1.2':raise ValueError('Unexpected baseline catalog')
 changed_dll=[]
 assets=catalog['font_bundle']['assets']+[a for m in catalog['runtime_mods'] for a in m['files']]
 for asset in assets:
  if asset['path'].casefold().replace('\\','/').endswith('/tnvse.dll'):
   path=package/'TranslationData'/asset['payload'];shutil.copy2(dll,path)
   asset['payload_sha256']=sha(path);changed_dll.append(path.relative_to(package).as_posix())
 if len(changed_dll)!=1:raise ValueError('Expected one native DLL payload')
 catalog['version']='1.1.3';catalog['game_validation']+='; issue35_native_178_checks_passed_game_screen_not_verified'
 nskr.write_json(catalog_path,catalog);payload_count=validate_payloads(package,catalog)
 snap=package/'Licenses-and-Source/NuclearSunset-Patcher-v1.1.3';snap.mkdir()
 hashes={}
 for source in sorted(ROOT.glob('nskr*.py'))+[ROOT/'ns_inventory.py']+sorted((ROOT/'tools').glob('*.py')):
  rel=source.relative_to(ROOT);target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(source,target);hashes[rel.as_posix()]=sha(source)
 shutil.copytree(ROOT/'tests',snap/'tests',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(ROOT/'native',snap/'native',ignore=shutil.ignore_patterns('__pycache__','*.exe','*.obj','*.bin','*.cmd','*.log'))
 (snap/'SOURCE-SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
 for source,name in ((ROOT/'README.md','README.md'),(ROOT/'docs/releases/v1.1.3.md','RELEASE-NOTES.md'),
                     (ROOT.parent/'translations/docs/main/korean-patch.md','INSTALL.md')):
  shutil.copy2(source,package/name)
 for name in ('NuclearSunsetKoreanPatcher.exe','NSKRXEditWorker.exe'):(package/name).unlink()
 for name in ('_internal','worker-runtime'):
  target=(package/name).resolve()
  if not target.is_relative_to(work):raise ValueError('Build cleanup escaped workspace')
  shutil.rmtree(target)
 compile_program(work,package,'NSKRXEditWorker','nskr_xedit_worker.py','worker-runtime',windowed=False)
 compile_program(work,package,'NuclearSunsetKoreanPatcher','nskr_gui.py','_internal',windowed=True)
 check=check_binary(package)
 for rel,digest in hashes.items():
  if sha(ROOT/rel)!=digest or sha(snap/rel)!=digest:raise ValueError('Source changed during build')
 allowed=set(native_changed+changed_dll+['TranslationData/catalog.json','README.md','RELEASE-NOTES.md','INSTALL.md','NuclearSunsetKoreanPatcher.exe','NSKRXEditWorker.exe'])
 for name,digest in baseline.items():
  if name in allowed or name.startswith(('_internal/','worker-runtime/')):continue
  if sha(package/name)!=digest:raise ValueError('Unrelated release payload changed: '+name)
 out=work/'output';out.mkdir();full=out/'NuclearSunset-Korean-Patcher-v1.1.3.zip';data=out/'NuclearSunset-TranslationData-v1.1.3.zip'
 package_zip(package,full,('',));package_zip(package,data,('TranslationData','Licenses-and-Source'))
 with zipfile.ZipFile(full) as f,zipfile.ZipFile(data) as d:
  if f.testzip() or d.testzip():raise ValueError('Archive CRC failure')
  for name in checked_zip(d):
   if d.read(name)!=f.read(name):raise ValueError('Standalone data differs: '+name)
  extracted=work/'unpacked';extracted.mkdir();unpack(f,extracted)
 extracted_check=check_binary(extracted)
 artifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in (full,data)]
 (out/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in artifacts),encoding='ascii')
 report=dict(version='1.1.3',base_sha256=BASE_SHA,native_ci=CI_URL,native_dll_sha256=expected,
  native_checks=native_results,payloads_verified=payload_count,unchanged_baseline_files_checked=len(baseline),
  changed_game_payloads=changed_dll,changed_native_sources=native_changed,binary_selfcheck=check,
  extracted_binary_selfcheck=extracted_check,gameplay_tested=False,artifacts=artifacts)
 (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=True,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--work',required=True);p.add_argument('--native',required=True)
 a=p.parse_args();build(a.base,a.work,a.native)
