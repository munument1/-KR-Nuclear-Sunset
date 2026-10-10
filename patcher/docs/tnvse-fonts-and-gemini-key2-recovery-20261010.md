# Nuclear Sunset: VNV tNVSE 한국어 폰트·설정 편입 및 Gemini 2번 키 복구 (2026-10-10)

## 1. tNVSE 한국어 폰트·설정

사용자는 tNVSE 본체를 이미 설치했다. Nuclear Sunset 설치의 tNVSE 기본 설정은 FreeType/멀티바이트/UTF-8이 비활성화되어 있었고, VNV의 2026-10-06 검증용 한국어 설정은 모두 활성화돼 있었다.

- **원본 VNV 소스:** 로컬 D:\Codex_Trans\비바 뉴 베가스\bundles\sst-release-20261006\font-payloads
- **가져온 설정:** tnvse.ini, tnvse_fonts.xml
- **핵심 값:** bEnableFreeTypeFontRendering=1, bEnableMultibyteFontHook=1, uiEncoding=4, bUTF8=1, bEnableDictionaryTranslation=0
- **사용 폰트:** Pretendard Bold, NanumSquare ExtraBold, NeoDunggeunmo Pro, TmonMonsori
- **관리 슬롯:** 1~8 및 42
- **라이선스:** 각 폰트별 원본 저작권/배포 고지 6개 보존
- **미포함:** tnvse.dll, 기존 모드의 다른 설정 또는 사전 파일

별도 설치·검수 가능한 MO2 모드 로컬 시험본은 다음에 저장했다.

D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\13_tNVSE_Korean_Fonts_Staging_20261010

프로젝트의 기존 `nskr_fonts.build_fonts` 처리기에 **provider_strategy=separate_mod** 옵션을 추가했다. 기존 tNVSE Default Config의 XML을 병합 참조하되, 작성할 모든 설정·폰트·라이선스 파일은 다음 별도 MO2 폴더로 출력한다.

mods/Nuclear Sunset - Korean Fonts for tNVSE

기존 tNVSE Default Config 원본을 직접 수정하지 않는다. 활성화는 사용자 또는 추후 패쳐 설치 단계에서 하고, 게임 UI 한글 표시 검증 전에는 강제 활성화하지 않는다.

미출시 로컬 SST 카탈로그 `.local/ns-sst-with-nexus-quest-esp-v2/catalog.json`에 `font_bundle`을 연결했고, 원본 catalog 파일은 `catalog.before-tNVSE-font-bundle.json`으로 별도 백업했다. **translation_ready=false 유지**.

실제 `nskr_fonts.build_fonts` 실행 시험:
- 파일 **13개** 작성 및 각각 SHA-256 재검증
- tNVSE 설치 감지 성공
- 모든 Output 경로가 독립적인 Nuclear Sunset 한국어 폰트 모드 아래인지 검증
- 한글 폰트 4개와 라이선스 원본은 로컬에만 보관, GitHub에 업로드하지 않음

관련 코드:
- `patcher/tools/stage_nuclear_tnvse_fonts.py` — 독립 시험본 생성
- `patcher/tools/attach_nuclear_tnvse_font_bundle.py` — 기존 로컬 SST 카탈로그에 폰트 패키징 명세를 안전 검증 후 연결
- `patcher/nskr_fonts.py` — separate_mod 출력 경로 사용

**주의:** tNVSE 런타임/게임/TTW/퀘스트 모드/MCM/HUD에서 모든 한글이 정상 출력되는지 아직 확인하지 않았다. 일부 폰트는 일반적인 SIL OFL과 다른 배포 조건을 가지므로 공식 재배포 전 라이선스를 재확인한다.

## 2. 2번 Gemini API 키 복구

문제: 실행기의 구버전 구현이 일반 HTTP 429 요청 속도 제한을 일일 요청 한도 소진으로 처리했고, `quota_attempts.json`의 2번 프로젝트를 인위적으로 500회로 지정해 다음 날까지 무한 대기시켰다.

확인:
1. 2번 키로 `gemini-3.1-flash-lite` 단일 번역 요청을 별도로 전송해 **정상 응답** 확인.
2. 키의 인증·모델 호환 문제가 아니라 잘못된 429 분류로 판정.
3. 백업 파일 `quota_attempts_before_recovery_20261010_144141.json` 생성 후, 인위적인 500회 표시는 보수적인 220회로 조정. 이는 실제 API 제공 한도 집계값이 아니라 실행기의 보호용 요청 기록이며, 사용량 초과를 단정할 수 없음.
4. 번역 실행기 개선: 429에는 60초부터 단계적으로 대기하며 재시도. **일일 한도임을 명시하는 오류에서만** 다음 날로 대기. 모든 요청은 키별 최대 500회 제한을 계속 준수.
5. 기존 출력의 원문/번역 JSON을 보존하며 재시작. 기술용 레코드를 걸러낸 혼합 JSON 배치에 발생하던 배열 길이 검사 오류(`len(original)` 대신 `len(required_keys)`)도 해결.
6. 정상 재개 후 2번 프로젝트 저장 파일 **148개에서 162개로 증가** 확인 (2026-10-10 14:46 KST 기준). 당시 총 798/859배치 완료, 워커 실행 중, 새로 저장한 배치 실패 0건.

API 키 자체는 출력·커밋·복사하지 않았다. 번역이 완결될 때까지 PC와 네트워크 연결이 필요하며, 완결 후에도 별도 자동 QA와 사람이 수행하는 문맥 검수가 남는다.

변경 파일:
- `patcher/tools/run_gemini_nuclear_unattended.py`
- 본 문서
