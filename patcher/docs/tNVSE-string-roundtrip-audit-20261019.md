# Nuclear Sunset #11 — tNVSE·JIP 문자열 경로 감사 (2026-10-19, READ ONLY)

## 진단

현재 근거만으로 **tNVSE가 Concentrated Fire의 `??`를 만들었다고 확정할 수 없다**. 한국어로 번역된 실제 PERK/DESC 바이트는 정상이며, 해당 퍽에는 별도로 JIP의 `GetFormDescription → Sv_RegexReplace → SetFormDescription` 실행 경로가 있다. tNVSE는 게임 UI의 글꼴·인코딩 표시와 사전 치환을 담당하는 코드가 확인되며, 설치된 tNVSE 한국어 소스에서는 세 JIP 문자열 함수의 직접 훅을 발견하지 못했다. 게임 실행 없이 첫 손실 발생 지점을 판별할 수 없다.

## 설치 근거

선택된 MO2 프로필 `KR Test - h8at5ar1`의 `modlist.txt` 상단은 `+NSKR Test - 1cxljp5s`(index 1), `+tNVSE Default Config`(2), `+tNVSE`(3)이다. 이 가상 경로 우선순위라면 NSKR Test의 DLL·INI가 원본 tNVSE 및 Default Config보다 우선하지만, 실행 프로세스가 실제 어떤 DLL을 로드했는지는 미확인이다.

| 파일 | 크기 | SHA-256 / 버전 |
|---|---:|---|
| `mods/tNVSE/NVSE/plugins/tnvse.dll` | 3,411,456 B | `aa107ad376581f9f2440f19dc1f03fa4447193ef186a0cc5d74ffa3e03215725` |
| `mods/NSKR Test - 1cxljp5s/NVSE/plugins/tnvse.dll` | 3,414,016 B | `fae479bd3d6f61b52d824e10cc6fe01abe96c31584f284a5e5969340d0844db4` |
| 10월 10일 문서의 VNV 수정 tNVSE DLL | 3,375,616 B | `ad2a81f1440647919ba792f0216ed26a736d4c4a51777f875e85e270538b3d70` |
| `mods/[DB] - JIP LN NVSE Plugin/nvse/plugins/jip_nvse.dll` | 502,272 B | PE FileVersion `57.30.0.0` |
| 게임 `nvse_loader.exe` | 155,136 B | PE FileVersion `0, 6, 4, 8` |

NSKR Test의 tNVSE DLL은 위 VNV 수정 DLL과도 해시·크기가 다르다. tNVSE DLL에는 식별 가능한 PE FileVersion 문자열이 없어 소스 문서의 'tNVSE 71' 외에 정확한 빌드 식별은 검증되지 않았다.

NSKR Test 활성 `tnvse.ini` 설정: `bEnableFreeTypeFontRendering=1`, `bEnableMultibyteFontHook=1`, `uiEncoding=4`, `bUTF8=1`, `bEnableDictionaryTranslation=1`. 원본 Default Config에서는 모두 0이다. 시험 출력의 `tnvse_dictionary.xml`은 `NSKR_UI_Translations.json`을 참조한다. 해당 JSON 텍스트에서 `Concentrated Fire`, `Headhunter`, `Fast Metabolism` 영어 문구는 발견되지 않았다. 사전 활성화 자체는 추가 통제 변수다.

시험 출력에 포함된 `tNVSE-71-KR-UI-source.zip`의 `tnvse/Src/font/encoding.cpp`, `font/text_hooks.cpp`, `font/font_manager.cpp` 및 사전 소스를 검색했다. 코드에는 한국어 코드페이지 949, UTF-8/멀티바이트 UI 변환, FreeType, 글꼴 및 사전 치환이 존재한다. `tnvse/Src/`의 텍스트에서 `GetFormDescription`, `SetFormDescription`, `Sv_RegexReplace`라는 이름은 발견되지 않았다. 이 세 API는 [GECK GetFormDescription](https://geckwiki.com/index.php?title=GetFormDescription), [SetFormDescription](https://geckwiki.com/index.php?title=SetFormDescription), [Sv_RegexReplace](https://geckwiki.com/index.php?title=Sv_RegexReplace)에서 JIP 함수로 소개된다.

이전 `tNVSE-KR-UI-fix.txt` 설명도 **GMST/UI UTF-8 치환문을 렌더링 전에 기존 인코딩 변환기에 통과시키는 것**을 수정 내용으로 밝힌다. JIP `SetFormDescription` 처리 자체를 수정했다는 근거는 없다.

## 정적 데이터 및 게임 미실행 재현

`mods/NSKR Test - 1cxljp5s/S6S Base Game Perks Redux.esp`의 `PERK` / FormID 하위 `044CAF` / `DESC`를 직접 읽으면 UTF-8이 정상이며 비ASCII 한국어 문자 **56개**가 남아 있다. Python 유니코드 정규식으로 영어 `V.A.T.S.`를 `Bullet Time`으로 치환해도 그 56개는 모두 보존된다. 반면 결과를 가정상 Windows-1252로 `errors='replace'` 왕복시키면 56개가 **56개의 '?'**로 바뀌고 `(Concentrated Fire)`, `Bullet Time`, `20%`는 남는다. 이 결과는 화면과 닮았지만, **실제 JIP DLL이 CP1252로 변환한다고 증명한 테스트는 아니다**. 원문 UTF-8이 `?`로 소실된 이후에는 tNVSE 글꼴 훅으로 복원할 수 없다.

현 `Bullet Time - Perk Consistency Patch/nvse/plugins/Scripts/gr_BulletTimePerkDesc.txt`는 `GLTA 86`, `GLTA 98`, `AVPerception` 세 경로에서 `GetFormDescription`으로 읽고 `Sv_RegexReplace`로 영어 표기를 치환한 뒤 `SetFormDescription`으로 다시 기록한다. 같은 파일 외에는 모드 내용으로 `meta.ini`만 있다.

**`nskr_nvse.py`의 ASCII-only guard는 유지할 가치가 있다.** 이 guard는 한국어를 포함한 설명이 이미 UTF-8 형태로 `GetFormDescription`에 도달하는 경우 재작성을 회피한다. 그러나 함수 반환값이 guard 이전에 이미 ASCII `?`로 손상됐다면 guard가 통과시키므로 효과가 없다. 이를 증명하려면 실제 JIP `Sv_RegexMatch`/`Sv_RegexReplace`/`SetFormDescription`의 인코딩 반환값 및 런타임 문법을 게임에서 검증해야 한다. 기존 단위 테스트는 변경 텍스트와 줄바꿈·명령 구조가 맞음을 검증할 뿐 런타임 실행을 증명하지 않는다.

## A/B 시험 계획 (현재 미실행, 원본 변경 금지)

1. 임시 **복제 MO2 프로필**을 구성하고 현재 NSKR Test tNVSE DLL/INI, JIP DLL, 번역 플러그인 및 로드 순서를 일정하게 유지한다. 새 게임 또는 복제된 별도 세이브로 `Concentrated Fire` 화면을 기록한다(A).
2. 같은 조건에서 **`Bullet Time - Perk Consistency Patch` 모드만 임시 프로필에서 끈다**(B). 이 모드는 위 텍스트 스크립트와 `meta.ini`만 보유한다. 게임 재시작 후 동일 퍽을 비교한다. B가 정상이라면 해당 스크립트 경로가 손상에 관여했을 가능성이 강해진다.
3. C는 Bullet Time 원문 대신 **ASCII guard를 적용한 별도 Output 스크립트**를 임시 프로필에서 시험해 B와 비교한다. JIP의 한글 처리, `CallAfter` 람다 실행 및 새 게임/불러오기 순서를 검증한다.
4. A/B/C 모두 실패할 경우에만 동일한 임시 프로필에서 tNVSE 렌더링 설정·실제 로드된 DLL 버전과 JIP 문자열 반환 경로를 따로 비교한다. 게임/원본 플러그인/DLL을 직접 수정하지 않는다.

`Tag!`의 한국어 `gr_TagPerkDescriptionSetter.txt` 또한 JIP Script Runner의 UTF-8 한글 실행 여부가 검증되지 않았다. 문자열 API 단계에서 손실되면 tNVSE DLL 변경만으로 해결된다고 할 수 없다.

**최종 판정:** tNVSE 결함 가능성은 배제하지 않았지만 필수 DLL 패치라는 결론은 미확정이다. 현 시점의 가장 안전한 접근은 Bullet Time ASCII guard를 유지하고, tNVSE 버전을 고정한 상태에서 해당 스크립트만 끈 A/B 재현을 먼저 실시하는 것이다. 실게임 검증은 아직 수행되지 않았다.
