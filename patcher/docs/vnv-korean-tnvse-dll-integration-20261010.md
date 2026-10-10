# Nuclear Sunset — VNV 한국어 수정 tNVSE 71 DLL 도입 (2026-10-10)

## 도입 이유

사용자 실게임 피드백: **기본 tNVSE DLL을 사용하면 일부 상호작용 UI 글자가 깨지고, Viva New Vegas 한국어 패쳐에 포함된 수정 tNVSE DLL을 사용해야 정상 출력**된다.

두 파일은 실제로 다른 바이너리다.

| 원본 | 크기 | SHA-256 |
|---|---:|---|
| Nuclear Sunset `mods/tNVSE/NVSE/plugins/tnvse.dll` | 3,411,456바이트 | `AA107AD376581F9F2440F19DC1F03FA4447193EF186A0CC5D74FFA3E03215725` |
| VNV `mods/VNV Korean Fonts - tNVSE/NVSE/plugins/tnvse.dll` | 3,375,616바이트 | `AD2A81F1440647919BA792F0216ED26A736D4C4A51777F875E85E270538B3D70` |

VNV 한국어 수정판은 **2026-10-07**, 기본 tNVSE 71을 기반으로 만든 Win32 DLL이다. 기존 `tNVSE-KR-UI-fix.txt`의 수정 설명: UTF-8 GMST/UI 치환 문자열을 기존 인코딩 변환기를 거쳐 레이아웃에 전달하며, 리치 텍스트 치환을 포함한다. 다른 훅·셰이더·플러그인 식별자·폰트 기본값은 변경하지 않았다고 설명한다. *이 원본 문서의 설명과 해시는 검증됐으나, Nuclear Sunset 실게임에서의 동작은 아직 시험하지 않았다.*

## 안전한 패쳐 통합

- 기존 `tNVSE` 및 `tNVSE Default Config` 모드는 **수정하지 않는다**.
- Nuclear Sunset 한국어 패쳐가 작성하는 독립 MO2 모드 `mods/Nuclear Sunset - Korean Fonts for tNVSE`에 **수정 tnvse.dll**을 추가한다.
- 기존 tNVSE 및 기본 설정 모드 **이후(높은 우선순위)**에 한국어 모드를 배치하면 수정 DLL/INI/XML/폰트가 우선 적용된다.
- 전용 설정: VNV 기준 `uiEncoding=4`, `bUTF8=1`, `bEnableMultibyteFontHook=1`, `bEnableFreeTypeFontRendering=1`.
- 4개 한국어 폰트와 기존 저작권 고지를 보존한다.
- tNVSE는 GPL-3.0: **원본 GPL 라이선스 전문, 수정 안내 및 해당 수정 DLL의 대응 소스 ZIP**을 DLL과 함께 별도로 포함한다.
- tNVSE/폰트/게임 파일 원본이나 바이너리는 GitHub에 업로드하지 않는다. 로컬 카탈로그의 해시 검증 대상 패키징 리소스로만 사용한다.

로컬 VNV 수정 DLL 출처:

`C:\Modlists\VNV\mods\VNV Korean Fonts - tNVSE\NVSE\plugins\tnvse.dll`

로컬 시험용 패키지:

`D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\13_tNVSE_Korean_Fonts_Staging_20261010`

미출시 카탈로그:

`D:\Codex_Trans\NuclearSunsetPatcherRepo\patcher\.local\ns-sst-with-nexus-quest-esp-v2\catalog.json`

`translation_ready=false` 유지, 정식 공개/릴리즈 전 실게임 검증 필요.

## 검증 결과

- VNV 수정 DLL 원본 SHA-256과 고정 핀 일치 확인.
- 기본 Nuclear Sunset DLL과 실제 내용이 다르며, 기존 설치 DLL이 수정되지 않았음 확인.
- VNV 수정 DLL Win32 x86 PE 검사 통과.
- 수정 소스 ZIP CRC 검사 및 GPL 원본 고지 확인.
- `nskr_fonts.build_fonts`의 격리된 Output 생성 시험: **17개 파일** 기록, 각각 SHA-256 재확인, DLL 별도 복사 및 원본 무변경 확인.
- `stage_nuclear_tnvse_fonts.py`로 깨끗한 새 임시 Output 생성 시험: **16개 소스 파일**, 해시 재검증, 사용 파일 제거 후 로컬 예비 시험본만 남김.
- 본인 Nuclear Sunset 설치의 MO2 모드 목록/플러그인 활성 상태는 변경하지 않았음. 실제 게임에서 상호작용 텍스트·HUD·Pip-Boy·MCM·라디오·터미널 출력 시험이 남아 있음.

## 코드

- `patcher/tools/attach_vnv_korean_tnvse_dll.py`: 기존 미출시 한글 폰트 카탈로그에 VNV 수정 DLL/GPL 소스 추가, 원본 SHA 확인, Output 안전 재검증.
- `patcher/tools/stage_nuclear_tnvse_fonts.py`: 신규 로컬 테스트 폰트 모드 생성 시 수정 DLL 및 소스도 함께 복사.
- `patcher/nskr_fonts.py`: `provider_strategy=separate_mod`로 원본 `tNVSE Default Config`를 덮어쓰지 않고 별도 우선순위 모드에 출력.

## 권장 실게임 확인

MO2에서 한국어 폰트 모드를 tNVSE와 기본 설정 모드보다 높은 우선순위로 켜고, 한글 상호작용 항목(문/컨테이너/액터), 대사 선택지, HUD, Pip-Boy, 터미널, MCM을 비교한다. 이상 시 **한국어 폰트 모드만 비활성화해 원상 복구**할 수 있다.
