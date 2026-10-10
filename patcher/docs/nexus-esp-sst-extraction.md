# Nuclear Sunset: Nexus 한국어 ESP → SST 추출 결과

2026-10-10. 사용자가 바탕화면에 저장한 Nexus 번역 압축파일을 대상으로 **Nuclear Sunset MO2 활성 플러그인과 직접 대조**했다.

| 대상 | MO2 원본 플러그인 | Nexus 한국어 파일 | 원본 레코드 일치 | 구조 변경 없는 번역 필드 후보 | 번역 레코드 |
|---|---|---|---:|---:|---:|
| Autumn Leaves — Uncreative Edition | `AutumnLeaves.esp` | `Autumn Leaves Uncreative Edition KR ESP-95093-1-2-1767436393.7z` | 8,056/8,056 | **4,296** | 1,792 |
| Zion Trail — Revised Rewritten Revoiced | `ZionTrail.esm` | `Zion Trail - Revised Rewritten Revoiced KR ESP-95078-1-1767436658.7z` | 50,221/50,221 | **2,162** | 1,354 |

검증 절차: 압축 해제 → 원본과 번역판의 TES4 마스터 목록 확인 → 레코드 FormID/시그니처 대조 → 서브레코드 개수·순서·비문자 데이터 보존 → 영문 원본/한글 번역문 비교 → 포맷 토큰 검사 → SSU9 SST 생성 → SST 원문·번역문 및 **소속 마스터(FormID 상위 바이트)** 왕복 검증.

주의: Zion Trail에서는 800개 레코드에 서브레코드 배열 구조 차이가, 49개에 필드 수 차이가, 466개에 비문자 변경 등이 발견되어 후보에서 제외했다. Autumn Leaves도 총 28개 레코드에 구조·비문자 차이가 있었다. 이들은 원본에 자동 적용하지 않는다.

특히 처음 생성한 임시 SST의 마스터 소속 기록이 잘못되는 문제(원본 FalloutNV.esm을 덮어쓰는 문자열 총 3개)를 발견하여 변환기를 수정하고 **v2 사전으로 재생성**했다. 기존 임시 산출물은 사용하지 않는다.

## 현재 로컬 산출물

모두 `D:\Codex_Trans\NuclearSunsetPatcherRepo\patcher\.local` 아래에만 저장됨:

- `nexus_esp/autumn/AutumnLeaves.esp` — 업로드된 번역 압축파일에서 추출한 한국어 ESP (보관용)
- `nexus_esp/zion/ZionTrail.esm` — 업로드된 번역 압축파일에서 추출한 한국어 ESM (보관용)
- `nexus_sst_v2/autumn-uncreative/AutumnLeaves_en_ko.sst` — **4,296 후보**
- `nexus_sst_v2/zion-revised/ZionTrail_en_ko.sst` — **2,162 후보**
- `ns-sst-with-nexus-quest-esp-v2/catalog.json` — 현재 직접 SST 후보가 있는 **38개 플러그인**, 매핑 후보 **225,311건**을 합산한 사전 (이전 후보 218,853건에 6,458건 추가)

## 안전 및 남은 일

- 모든 출력은 별도 `.local`이며 원본 MO2/ESP/ESM을 변경하지 않았다.
- `translation_ready=false`. **실제 XEditLib 로딩·출력·재로드 검사와 게임 화면 표시 검증이 완료된 번역본은 아니다.**
- FOJP 텍스트가 아니라 업로드된 한국어 ESP/ESM 자체와 설치본을 대조한 것이므로 구조가 일치하는 번역 문자열 추출에 더 적합하다.
- `AutumnLeaves.esp`와 `ZionTrail.esm` 외에 아직 SST가 없는 모드는 별도 분석이 필요하다.
- 원본 ESP/ESM 및 게임 자산을 GitHub에 올리지 않는다. 번역 추출 결과도 사용 허락, 출처 및 검수 전에는 릴리즈에 포함하지 않는다.
