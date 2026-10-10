# Nuclear Sunset — TTW KOR Radio + UI / Mojave Radio Captions 검토 (2026-10-10)

## 원본 파일 확인

로컬 사용자 제공 자료:
- `D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\TTW KOR Radio + UI.esp`
- 파일 크기 1,745,604바이트, SHA-256 `8adf68074b1506e852d2670f2c7f6c5dcaf8dadc34ec6e30477110e53e2f5e09`
- 13개 마스터 의존성: FalloutNV, 뉴베가스 주요 DLC, Fallout3, 5개 FO3 DLC, TaleOfTwoWastelands

TES4 원본 레코드 조사:
| 종류 | 전체 | 마스터 오버라이드 | 새로 생성 |
|---|---:|---:|---:|
| GMST | 1,464 | 12 | 1,452 |
| INFO | 2,759 | 1,551 | 1,208 |
| MESG | 1,781 | 85 | 1,696 |
| DIAL | 536 | 135 | 401 |
| MICN / VTYP | 4 | 1 | 3 |
| **합계** | **6,544** | | |

한국어 필드 조사:
- `GMST:DATA` 전체 한국어 1,313필드. 기존 마스터 오버라이드 11개, ESP가 신규 생성한 1,302개.
- `INFO:NAM1` 한국어 1,365필드. 기존 마스터 오버라이드 1,346개, 신규 레코드 19개.
- `MESG:DESC` 한국어 1,776필드. 오버라이드 83개, 신규 레코드 1,693개.

### 현행 Nuclear Sunset SST와 중복 조사

- 기존 마스터 INFO/NAM1 번역 **1,216개 동일** → 재번역/중복 덮어쓰기 하지 말 것.
- 동일 INFO/NAM1 식별자에서 번역이 서로 다른 경우 **127개** → 섣불리 덮어쓰지 말고 문맥 검수.
- 기존 INFO/NAM1 번역 사전에서 없는 후보 **3개** → 원문·경로 검증 후 추가 검토.
- 기존 GMST 오버라이드 한국어 11개 중 4개는 현재 SST와 같은 표기, 7개는 상이.
- 한국어 GMST 신규 레코드 **1,302개**는 단순 마스터 원문/FormID 대조로 병합할 수 없다. 게임에 하드코딩된 문자열 설정인 경우가 많으므로 별도 GMST 전용 플러그인에서 EDID 중복/우선순위·TNVSE UTF-8 처리 검증이 필요하다.
- 새 INFO/DIAL/MESG 레코드와 컴파일된 스크립트까지 통째로 옮기면 TTW/Nuclear Sunset의 라디오 조건 및 스크립트와 충돌할 수 있다.

**결론: 원본 TTW KOR Radio + UI.esp를 그대로 설치하거나 패쳐에 포함하지 않는다.** GMST와 실제 라디오 번역만 선택적으로 마이그레이션하고, 이미 존재하는 SST 원문은 우선한다.

## VNV 오픈소스 라디오 자막 모드 재사용

프로젝트: [Mojave Radio Captions](https://github.com/frankischilling/MojaveRadioCaptions) — MIT 라이선스 xNVSE/UIO 플러그인, v0.4.2 기술 시험판.

- 새로운 ESP를 추가하지 않는 방식이며, 게임에서 재생 중인 라디오 음성 자산과 현재 메모리에 로드된 `INFO` 대사를 연결하여 화면 자막을 표시한다.
- 자막은 게임에 로드된 대사의 언어에 따라 달라진다. **TTW 라디오 INFO 자체가 영어면 자막도 영어일 수 있다.**
- 기본 음악에는 노래 가사가 포함되지 않으며 간략한 설명 또는 별도 권한이 있는 WebVTT/로컬 전사 필요.
- TTW/커스텀 라디오, 해당 사용자의 UI 설정, 폰트, 인게임 훅 안정성은 아직 실증되지 않았다.
- MIT 조건에 따라 LICENSE와 THIRD_PARTY_NOTICES.md를 함께 배포해야 한다.

### 별도 로컬 시험본 생성

`D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\12_TTW_Radio_GMST_시험준비_20261010`

- `mods/Nuclear Sunset - Radio Captions (Experimental)` 아래에 VNV의 기존 x86 DLL, INI, UIO 파일, XML, 라이선스/저작권 고지 **6개만 복사**하고 해시 검증했다.
- 소스 패키지의 DLL은 32비트 x86 PE로 확인.
- `README_OPTIONAL_RADIO.txt` 및 `snapshot.json`에 시험 방법, 출처, 해시값, 비설치 상태 기록.
- **아직 Nuclear Sunset MO2에 설치하거나 프로필에서 활성화하지 않았으며, 공식 패쳐의 기본 Output에도 포함하지 않았다.**
- 사용자 원본 TTW KOR 파일이나 게임/모드 원본은 수정·삭제하지 않았다.

## 다음 검증

1. TTW에서 기존 한글 라디오 대사(예: GNR 방송)가 현재 게임 로드 결과에 적용되는지 체크.
2. 옵션 형태로 자막 모드를 MO2에 넣은 후 xNVSE/UIO 로딩, HUD 오버레이, 말 자막 타이밍, TTW 라디오 및 Nuclear Sunset 추가 방송 확인. 문제가 있으면 비활성화만으로 복구.
3. `TTW KOR Radio + UI.esp`의 GMST 신규/기존 1,464건을 위험 없는 GMST 전용 추출본으로 분리하고, 기존 번역과의 충돌, EDID/플레이스홀더/TNVSE 인코딩 검사.
4. 기존 SST에서 빠진 확정 한국어 라디오 INFO만 안전하게 추가. 새 INFO 레코드/스크립트의 무분별한 복사는 금지.
5. 실게임 검증 후에만 선택 기능으로 정식 Nuclear Sunset 패쳐 Output 포함을 판단한다.

검사/준비 스크립트(로컬 스캔 및 선택적 복사):
- `patcher/tools/stage_ttw_radio_captions.py`

기본 브랜치 및 릴리즈는 변경하지 않는다. 사용자 제공 ESP나 게임 자산은 GitHub에 올리지 않는다.

### 추가 로컬 검수용 CSV 생성 완료

`12_TTW_Radio_GMST_시험준비_20261010/donor_translation_candidates` 아래에 한국어 번역 텍스트만 별도 추출했다.

- `01_TTW_GMST_한국어_검수.csv`: GMST:DATA 한국어 **1,313건**. 신규 생성 1,302개가 포함되어 있으므로 EDID, 문자열 플레이스홀더, 기존 TTW 게임 설정과 충돌 검수가 필요하다.
- `02_라디오_기존SST_차이_검수.csv`: 기존 마스터의 INFO:NAM1 중 기존 SST와 표기가 다르거나 빠진 **130건**. 원문·실제 화자 검수 없이는 기존 번역을 교체하지 않는다.
- `03_메시지_기존SST_차이_검수.csv`: 기존 마스터 MESG 필드 중 기존 SST와 표기가 다르거나 빠진 **6건**.
- `00_검수대상_현황.json`: 타입별 목록과 SHA-256 출처 검증 기록.

새 DIAL/INFO/MESG 레코드·컴파일된 스크립트는 추출하거나 복사하지 않았고, 해당 CSV들은 MO2에 바로 설치하는 파일이 아니다. **패쳐 최종 번역에는 검수/원문 대조 후 통합**한다.

추출 스크립트: `patcher/tools/extract_ttw_korean_donor.py`. 안전 시험용 라디오 복사 스크립트: `patcher/tools/stage_ttw_radio_captions.py`.
