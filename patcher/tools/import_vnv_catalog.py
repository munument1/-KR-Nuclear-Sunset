"""Prepare a local, UNRELEASED Nuclear Sunset catalog from an existing VNV SST catalog.

Never publishes third-party plugin/master files. All translations remain in local
candidate output until the Fallout 3/TTW master mapping audit is completed.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import nskr
from nskr_output import FO3_TTW_MASTERS

def make_candidate(install, vnv, vnv_path: Path):
    if not install.is_ttw:
        raise ValueError('A TTW MO2 profile is required')
    selected=[]
    skipped=[]
    for original in vnv.get('files',[]):
        entry=copy.deepcopy(original)
        path=entry.get('path','')
        kind=entry.get('kind','')
        # This is filename/provider eligibility only, not proof of actual SST matches.
        if kind=='plugin-records':
            if path.casefold() not in install.active_keys:
                skipped.append({'path':path,'reason':'not_active_plugin'})
                continue
        elif kind in {'json','ini'}:
            if path.casefold() not in install.providers:
                skipped.append({'path':path,'reason':'not_installed_loose_text'})
                continue
        else:
            skipped.append({'path':path,'reason':'unsupported_kind'})
            continue
        entry.pop('verified_delta',None)
        selected.append(entry)
    included={e['path'].casefold() for e in selected if e.get('kind')=='plugin-records'}
    required_fo3=sorted(p for p in FO3_TTW_MASTERS if p in install.active_keys)
    still_missing=[p for p in required_fo3 if p not in included]
    catalog={
        'schema_version':1,
        'target_modlist':'nuclear-sunset-ttw',
        'translation_ready':False,
        'files':selected,
        'plugin_fields':vnv.get('plugin_fields',{}),
        'updated_plugin_backend':'Python ctypes + XEditLib',
        'game_validation':'not_run',
        'sst_source_policy':'Exact record identity and current English source matching; no approximate substitutions.',
        'translation_records':'VNV candidates only; FO3 and TTW coverage pending',
        'source_vnv_catalog_sha256':hashlib.sha256(vnv_path.read_bytes()).hexdigest(),
    }
    report={
        'profile':install.profile,
        'eligible_vnv_direct_plugins':len([e for e in selected if e.get('kind')=='plugin-records']),
        'direct_sst_candidate_rows':sum(len(e.get('mappings',[])) for e in selected if e.get('kind')=='plugin-records'),
        'eligible_vnv_loose_text_files':sum(e.get('kind') in {'ini','json'} for e in selected),
        'missing_ttw_fo3_masters':still_missing,
        'skipped_entries_count':len(skipped),
        'skipped_entries':skipped,
        'status':'PRELIMINARY ONLY; cannot build or release until TTW/FO3 SST review',
    }
    return catalog,report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mo2',type=Path,default=Path(r'C:\Modlists\NuclearSunset'))
    ap.add_argument('--profile')
    ap.add_argument('--vnv-catalog',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if args.output.exists():
        raise SystemExit('Output must be a NEW directory')
    installation=nskr.Installation(args.mo2,profile=args.profile)
    vnv=nskr.read_json(args.vnv_catalog)
    if vnv.get('schema_version')!=1:
        raise SystemExit('Unexpected VNV catalog schema')
    catalog,report=make_candidate(installation,vnv,args.vnv_catalog)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (args.output/'candidate-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
