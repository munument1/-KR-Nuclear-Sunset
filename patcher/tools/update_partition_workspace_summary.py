"""Add the native inheritance partition summary to the local translation workspace."""
from pathlib import Path
import json
WORK=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010")
PART=WORK/"10_번역분리_신규와_기존상속"/"00_분류현황.json"
def main():
    data=json.loads(PART.read_text(encoding="utf-8"))
    root=WORK/"00_작업현황.json"
    d=json.loads(root.read_text(encoding="utf-8"))
    if d["staged_untranslated_plugin_sources"]!=204:
        raise RuntimeError("Workspace changed")
    d["translation_partition"]=data
    root.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    readme=WORK/"00_먼저읽기.md"
    s=readme.read_text(encoding="utf-8")
    if "## 10번 작업 폴더" not in s:
        s+="\n## 10번 작업 폴더: 기존 SST 상속 우선, 신규 문장만 번역\n\n"
        s+="10_번역분리_신규와_기존상속/01_신규번역_필요 : SST에 원문 일치 후보가 없는 42,021개 필드입니다. 새 번역은 이곳부터 시작합니다.\n"
        s+="10_번역분리_신규와_기존상속/02_상속번역_검증대기 : 기존 SST 후보는 있지만 native 적용 검증이 남은 4,502개 필드입니다. 새로 번역하지 말고 먼저 검증합니다.\n"
        s+="10_번역분리_신규와_기존상속/03_상속번역_적용검증완료 : Native XEditLib 적용/새로읽기가 증명되고 영문/FormID/필드 키로 확실히 일치한 12,339개 필드입니다.\n"
        s+="원본 CSV는 수정하지 않았습니다. 각 CSV의 korean_translation은 아직 비워져 있습니다. 03 그룹의 existing_korean_candidate만 기존 번역 재사용 근거가 있습니다.\n"
        s+="위 건수는 게임에서 보이는 미번역 문장의 확정 수가 아닌 레코드 필드 후보 수입니다. MCM/UI와 스크립트는 별도 검토합니다.\n"
        readme.write_text(s,encoding="utf-8")
    print("WORKSPACE_UPDATED",json.dumps(data,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
