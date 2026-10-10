# Nuclear Sunset 번역 제외 대상 실증 정리 (2026-10-10)

## 결론

활성 플러그인 252개 가운데 기존 직접 SST로 적용·재로드 검증한 38개를 최초 작업 폴더에서 제외했다. 전용 SST가 없어 수집한 214개 중, 10개를 **일반 ESP/ESM 레코드 문자열 수작업 번역 대기열**에서 추가 분리했다. 따라서 현재 대기 파일은 **204개**다.

| 그룹 | 대상 | 개수 | 판정 |
|---|---|---:|---|
| 직접 SST 기존 검증 | 기존 SST/한국어 ESP 추출본을 네이티브 적용·재로드 검증 | 38 | 작업 폴더에 원본 중복 복사 안 함 |
| 상속 검증 완료 (08) | 기존 본편/DLC/TTW SST로 모든 탐지 영문 필드를 정확히 매핑하고 재로드 검증 | 4 | 일반 레코드 신규 번역 대기 제외 |
| 표시 원문 없는 플러그인 (09) | 활성 플러그인에 레코드는 있지만 추출 대상 일반 영문 표시 필드는 0 | 6 | 일반 레코드 번역 대기 제외, UI/스크립트 별도 확인 |
| 남은 수작업·추가 검수 대기 | 신규 번역 후보 보유 159, 상속 검수 필요 44, 매칭 없음 1 | **204** | 번역 검수 우선 |

### 기존 SST 완전 상속 검증 4개

- SSTFEVGrowths.esm — **2/2** 표시 번역 필드 적용·재로드 성공
- ThePlatinumVault.esm — **1/1** 적용·재로드 성공
- Interiors Improved - Tops Hotel.esp — **4/4** 적용·재로드 성공
- Sierra Madre Suite Windows.esp — **1/1** 적용·재로드 성공

검증 근거: 임시 MO2 게임 복사본에 XEditLib를 통한 실제 적용·새로 읽기, 원본과 FormID/필드/영문 원문 및 경로가 일치해야만 적용. 실증 결과는 로컬 .local/native-full-fallback-candidates-20261010/summary.json에 보관된다.

### 일반 영문 표시 필드 0개로 확인된 6개

| 플러그인 | 레코드 수 | 주요 종류 |
|---|---:|---|
| Main And Pause Menus Overhaul.esm | 29 | SCPT, QUST |
| DSJIPCCCAnims.esp | 34 | SCPT, IDLE, QUST |
| Vanilla UI Plus.esp | 8 | SCPT, QUST |
| ImmersivePickupSoundsRemastered.esp | 202 | SOUN, FLST, SCPT |
| IlluminatedVillaBuildingsOnly.esp | 21 | STAT |
| Uranium Haze Piplight.esp | 5 | SCPT, QUST, LIGH |

**레코드 자체가 아예 없는 파일은 없다.** 위 6개도 레코드는 존재한다. 표시 필드가 감지되지 않을 뿐 스크립트 내부 하드코딩 문자열, UI 메뉴/아이콘, MCM JSON 또는 별도 리소스 문자열의 한글화가 필요할 수 있으므로 완전한 한글화 확정으로 표시하지 않는다.

### 이전 분류 오차 2개 수정

최초 감사에서 no_detected_english_text로 분류된 아래 플러그인은 새로운 필드 검사에서 실제 영문 원문 후보가 확인되었다. 일반 레코드 번역 대상 01로 재분류했다.

- Capital Ruins for TTW.esp — 영문 표시 후보 **123건**
- NeutralWeathers_TTW.esp — 영문 표시 후보 **124건**

## 로컬 결과

작업 루트: D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010

- 00_플러그인_대상목록.csv: 실제 번역·검수 대기 **204개**
- 00_기존SST상속완료_검증목록.csv: 완전 상속 4개
- 00_표시문구없음_UI스크립트확인목록.csv: 레코드 표시 영문 없는 6개
- 08_기존SST_상속완료_번역대기제외: 원본 복사본과 CSV 보관
- 09_레코드표시문구없음_스크립트UI확인: 원본 복사본과 CSV 보관
- 00_번역우선순위_TOP50.csv: 갱신된 수작업 번역 우선순위 목록

**원본 파일을 삭제하지 않았고, MO2 설치 폴더도 수정하지 않았다.** 게임과 모드 원본 바이너리는 로컬에서만 보존하고 GitHub에는 검사 도구와 본 보고서만 올린다. 정식 릴리즈 플래그는 그대로 false다.

재현 스크립트: patcher/tools/separate_no_translation_required.py, patcher/tools/fix_zero_text_classification.py.
