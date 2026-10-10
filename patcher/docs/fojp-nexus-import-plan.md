# Nexus FOJP → Nuclear Sunset SST 소스 확인 (2026-10-10)

Nuclear Sunset의 실제 MO2 플러그인과 일치하는 Party1Noodle의 Nexus Mods 번역 파일을 확인한 결과다. **Nexus 파일 본문은 로그인 없이 다운로드할 수 없어 아직 가져오지 못했음.** 영어·한국어 사전 원문을 확보한 것처럼 표시하지 않는다.

| 설치 플러그인 | 활성 MO2 공급자 | 사용자 번역 Nexus 페이지 | 공개 파일 유형 |
|---|---|---|---|
| `AutumnLeaves.esp` | `[OP] - Autumn Leaves - Uncreative Edition` | https://www.nexusmods.com/newvegas/mods/95093?tab=files | `Autumn Leaves Uncreative Edition KR ESP` (333 KB, tNVSE), `Autumn Leaves Uncreative Edition KR` (237 KB, FOJP) |
| `ZionTrail.esm` | `[OP] - Zion Trail - Revised, Rewritten, and Revoiced` | https://www.nexusmods.com/newvegas/mods/95078?tab=files | 한국어판 2개(FOJP 파일 존재) |

일반 `Autumn Leaves` 번역 (https://www.nexusmods.com/newvegas/mods/95025) 과 설치된 Uncreative Edition은 별도로 구분한다. Zion Trail Redux/Integrated와 Revised도 혼합하지 않는다.

## 소스 확보 상태

- Nexus 페이지의 번역 유형·버전·파일 크기를 확인했다.
- `F:\번역`, `D:\Codex_Trans`, 사용자 Downloads 및 Nuclear Sunset Downloads의 파일명 검색에서 해당 한국어판 압축본은 발견되지 않았다.
- 현재 **FOJP 원문 파일을 가져와 SST를 완성한 단계는 아니다**.
- Nexus 로그인 또는 승인된 다운로드 경로에서 사용자가 압축본을 다운로드한 뒤 아래 경로에 해제하면 로컬 매칭 도구를 적용할 수 있다.

## 안전한 로컬 변환

변환 스크립트: `patcher/tools/fojp_to_sst_candidate.py`

- FOJP의 `fojp.xml`에서 참조하는 `en`/`jp` (또는 `ko`) 쌍을 찾거나, `*_en.txt` + `*_ko.txt`/ `*_jp.txt` 쌍을 자동 감지한다.
- 같은 줄 번호의 영어·한국어를 연결하며, 번역이 서로 충돌하는 동일 영문 원문은 제외한다.
- 실제 설치 ESP/ESM에서 **영문이 문자 단위로 완전히 일치하는** 레코드만 FormID 소속 마스터와 필드 서명을 기록한다.
- 기본적으로 플러그인 고유 레코드만 대상으로 하며 다른 마스터의 override는 제외한다.
- 형식 지정자 보호 검사와 xTranslator SST roundtrip을 수행하지만, **계층화된 xEdit 필드 경로와 실행 시 표시 검증은 별도로 필요하다**.
- 원본 게임 데이터와 번역 ZIP은 수정하지 않고 `.local` 폴더에 후보 사전과 검증 리포트만 생성한다.

### 사용 예시

```powershell
cd "D:\Codex_Trans\NuclearSunsetPatcherRepo\patcher"

py -3 tools\fojp_to_sst_candidate.py `
  --source ".local\fojp_sources\AutumnLeaves-Uncreative" `
  --plugin "C:\Modlists\NuclearSunset\mods\[OP] - Autumn Leaves - Uncreative Edition\AutumnLeaves.esp" `
  --output ".local\fojp_candidates\autumnleaves-uncreative"
```

해제본의 FOJP 파일 구성을 확인한 후 파서의 입력 형식을 추가로 보완할 수 있다. 아직 검증되지 않은 번역 결과는 GitHub 저장소 및 정식 릴리즈에 포함하지 않는다.
