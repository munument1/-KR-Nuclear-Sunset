# Nuclear Sunset 미번역 작업 파일 통합 정리 (2026-10-10)

로컬 작업 경로:

D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010

모든 소스는 현재 Nuclear Sunset MO2 프로필의 활성 파일 제공자에서 로컬로 **복사**한 것이다. 설치된 C:\Modlists\NuclearSunset의 원본 모드 파일은 수정하지 않았다.

## 수집 결과

| 항목 | 수량 |
|---|---:|
| Nuclear Sunset 활성 ESP/ESM | 252개 |
| 기존 SST 매핑이 있는 네이티브 검증 대상 (중복 복사 제외) | 38개 |
| 전용 SST가 없는 ESP/ESM 로컬 복사본 | **214개** |
| 신규 번역용 모드 고유 원문 보유 파일 | 157개 |
| 본편/DLC 번역 상속 검토 파일 | 48개 |
| 기존 사전 매칭 없음 | 1개 |
| 플러그인 레코드 표시 영문 미탐지 | 8개 |
| 추출한 영문 원문 필드 | **58,870건** |
| 새 번역이 필요할 가능성이 있는 필드 | **42,021건** |
| 원문/FormID 일치로 기존 번역 상속이 가능한 후보 | **16,849건** |
| MCM JSON 원본 복사 | 24개 |
| Translations INI 원본 복사 | 13개 |
| 기존 SST 적용 기록에 없는 항목의 재검수 CSV | 38개 파일, **12,461건의 후보** |
| 로컬 ESP/ESM 복사본 총 용량 | 약 359.4MiB |

### 폴더 구조

- 01_신규번역_전용SST없음: 157개의 ESP/ESM 원본 복사 및 각 파일의 영문 추출 CSV
- 02_기본번역_상속검수: 48개의 ESP/ESM 원본 복사 및 CSV (이미 적용 가능성이 있는 번역은 참고 후보 기입)
- 03_사전매칭없음_검토: 1개의 ESP/ESM 및 CSV
- 04_표시영문없음_별도확인: 8개의 ESP/ESM 및 CSV (MCM/스크립트 쪽 별도 확인)
- 05_MCM_JSON: 실제 파일 상대 경로를 보존해 복사한 24개 JSON
- 06_Translations_INI: 실제 파일 상대 경로를 보존해 복사한 13개 INI
- 07_기존SST_미적용후보_추가검수: 이미 직접 SST를 보유한 38개 플러그인 가운데 네이티브 변경 기록에 없는 항목의 검수 CSV 및 집계

최상위 파일:
- 00_먼저읽기.md: 폴더별 용도와 주의사항
- 00_작업현황.json: 주요 건수, 원본 복사 총 용량
- 00_플러그인_대상목록.csv: 경로, MO2 공급자, 원본 SHA-256, 후보 원문 건수
- 00_MCM_번역대상목록.csv: JSON/INI 가상 경로와 원본 제공자
- 00_기존SST_추가검수_목록.csv: 38개 SST의 네이티브 적용 차이
- 00_번역우선순위_TOP50.csv: 번역 필요 후보가 많은 50개 플러그인

### 작업 우선순위

신규 번역 후보가 많은 상위 파일은 LoneWandererThemeTTW.esm (3,751), TTW Dialogue and Interactions Expansion Overhaul.esp (3,563), BraveNewWorld.esm (3,094), RaceToTheBottom.esm (2,920), Party Banter 2.esm (2,491), Into The Deep.esm (2,430), AWorldOfPainFO3.esm (2,365), NS.esp (2,011), TTW New Vegas Speech Checks.esm (1,636), TTW Reputations.esm (1,228) 순이다.

**중요:** 수치는 원본 레코드에서 탐지한 영문 **필드 후보** 수이다. 실제 게임에 보이는 문자열 수와 같지 않고, 스크립트나 BSA·UI 자산 등의 문자열은 별도 검수가 필요하다. 07 그룹의 12,461건은 후보 대비 native changed-key 차이로서 실제 미번역 확정 수가 아니다.

### 안전 및 다음 단계

- 원본 복사본과 추출 문장·번역 후보는 로컬 작업 폴더에만 존재한다. **ESP/ESM과 게임 원문을 GitHub에 올리지 않는다.**
- 원본 복사본을 MO2에 그대로 덮어쓰기 하지 않는다. 한국어 CSV 번역을 SST 매핑으로 재생성한 후 xEditLib 안전 검사·읽기 검증을 거쳐 패쳐 산출물로 만든다.
- 번역 후보 자료는 플러그인별 문맥·FormID·필드 경로 확인이 필요하다.
- 별도 패쳐 개발 브랜치는 현재 translation_ready=false이고, 릴리즈/게임 표시 검증은 아직 진행 전이다.
- 재현 도구: patcher/tools/stage_untranslated_workspace.py 및 patcher/tools/stage_unapplied_sst_review.py.
