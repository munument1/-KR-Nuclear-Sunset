from pathlib import Path
import argparse,json
import nskr
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mo2',type=Path,default=Path(r'C:\Modlists\NuclearSunset'))
    ap.add_argument('--profile')
    ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    install=nskr.Installation(a.mo2, profile=a.profile)
    if not install.is_ttw: raise SystemExit('TTW MO2 required')
    names={k:rows[-1]['provider'] for k,rows in install.providers.items() if rows}
    masters=['Fallout3.esm','Anchorage.esm','TaleOfTwoWastelands.esm','YUPTTW.esm']
    report={'mo2_root':str(install.root),'profile':install.profile,'game':'TTW',
      'enabled_mods':len(install.mods_enabled),'active_plugins':len(install.active),
      'active_plugins_with_provider':sum(1 for p in install.active if p.casefold() in names),
      'ttw_masters':{p:names.get(p.casefold()) for p in masters},'warnings':install.warnings}
    output=json.dumps(report,ensure_ascii=False,indent=2)
    print(output)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(output+'\n',encoding='utf-8')
if __name__=='__main__': main()
