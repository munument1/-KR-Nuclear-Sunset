# Nuclear Sunset 한국어 패쳐

[최신 다운로드](https://github.com/munument1/-KR-Nuclear-Sunset/releases/latest) · [설치 안내](https://munument1.github.io/-KR-Nuclear-Sunset/docs/main/korean-patch)

Viva New Vegas 패쳐를 기반으로 Nuclear Sunset / TTW에 맞춘 한국어 패쳐입니다. 설치된 모드를 읽어 별도 `Output/mods`를 생성하며 원본 모드와 프로필은 직접 수정하지 않습니다.

## v1.0.7 — 퍽·알림·기술 설명 수정

[릴리즈 노트](docs/releases/v1.0.7.md)를 참조하세요. 퍽 설명과 요구 조건의 인코딩 혼용,
아이템 사용 알림의 영어 문구, 실행 중 중화기 설명을 덮어쓰는 경로를 수정했습니다.
ShowOff/UI Organizer의 내부 조회 이름은 영어 식별자를 유지해 버전 `-1` 경고를 방지합니다.
사용자가 실제 게임에서 퍽 표시와 경고 복구를 확인했습니다. 모든 게임 경로를 실제 플레이로 확인한 것은 아닙니다.

새 폴더에 전체 패쳐를 풀고 새 Output을 생성하세요. EXE 또는 TranslationData만 교체하지 마세요.

## 이슈 #11 — NVSE 런타임 특전 설명

실행 중 다시 기록되는 특전 설명을 위해 `Tag Perk Description Adjustment`, `SSS - Sweets Simple Settings`, `Bullet Time - Perk Consistency Patch` 및 관련 모드의 NVSE 스크립트를 처리합니다. 태그!의 실제 한국어 설명을 적용하며, Bullet Time 정규식은 이미 한국어인 설명을 다시 변환하지 않도록 보호합니다. **집중 사격도 한국어로 표시합니다.** 이전 영어 우회 설명은 최종 출력 단계에서 복구됩니다.

퍽 설명과 요구 조건을 조합하는 문자열, JIP가 컴파일하는 표시 리터럴은 검토된 범위에서 CP949로 통일합니다. 컴파일 스크립트의 SCTX는 UTF-8 소스로 유지하고 SCDA의 명령·분기·피연산자 길이는 보존합니다. tNVSE가 자체 변환하는 설정 파일은 UTF-8로 유지합니다. 명령 인자와 플러그인·파일 식별자는 번역 대상에서 제외합니다.

원본 파일 경로·모드 공급자·명령 또는 영문 원문이 달라 검증할 수 없는 항목은 보고서에 남깁니다. 패쳐는 원본 모드에 쓰지 않습니다. Output을 적용하기 전 백업하고, 적용 후에는 게임을 완전히 재시작하세요.

`NS.esp`의 **Head Hunter**와 `Sweet Consumables.esp`의 **Fast Metabolism**은 실행 중 영어 설명을 주입하는 컴파일된 스크립트입니다. 번역은 별도 tNVSE 사전 모드를 만드는 방식이 아니라, **기존 플러그인의 번역 출력본**에서 해당 스크립트의 문자열 상수(SCTX/SCDA)와 그 길이 정보(SCHR 및 레코드 크기)를 함께 검증·교체하는 방식으로 진행합니다. 설치된 원본 ESP와 기존 수정 tNVSE DLL은 변경하지 않습니다.

Head Hunter의 퍼센트 표시는 스크립트의 `%%` 이스케이프를 그대로 보존하고, Fast Metabolism의 `%z` 서식 지정자도 유지합니다. 알려진 스크립트 구조와 다르면 파일을 변경하지 않고 실패하도록 설계하며, 출력 파일은 별도 파서로 재검증합니다. **게임에서 컴파일된 UTF-8 한국어 문자열이 정상 출력되는지 확인하기 전에는 정식 배포하지 않습니다.**

## 이미 한국어 패치를 설치한 경우 (v1.0.5 변경 예정)

GUI에서 다시 `Output 생성`을 누르면 기존 Output/보고서가 있을 경우 새로운 날짜별 Output 폴더를 만듭니다. 이미 번역된 ESM/ESP가 입력으로 발견되면 같은 레코드·필드·경로에서 **현재 카탈로그와 완전히 일치하는 한국어 문구**를 보존합니다. 이 동작은 해당 모드 전체가 최신 번역임을 뜻하지 않습니다.

이전 릴리즈와 바뀐 번역도 안전하게 갱신하려면 새 릴리즈를 빌드할 때 기존 배포본의 `TranslationData/catalog.json`을 사용해 `previous_dests` 이력을 포함해야 합니다. 예를 들어 `python tools/merge_previous_catalogs.py --current NEW/TranslationData/catalog.json --previous OLD/TranslationData/catalog.json --output NEXT/TranslationData/catalog.json`으로 **별도 복사본**을 생성한 다음 NEXT 디렉터리에서 나머지 번들 파일도 보존해 패키징합니다. `previous_dests`는 플러그인/모드 공급자, 원래 영어 문장, FormID, 필드 경로가 모두 같은 과거 번역에만 적용됩니다. 다른 원문이나 출처를 알 수 없는 옛 한글 내용은 경고 대상으로 남습니다.

오래된 패치를 원본 모드 폴더에 직접 덮어쓴 경우 원본 영어 파일을 자동 복원할 수는 없습니다. 업데이트 전 백업을 권장하며, MO2에서 기존 패치와 새 결과물의 우선순위가 충돌하지 않도록 확인하세요. 새 Output을 기존 MO2 `mods` 폴더에 설치할 때 파일 이름·경로가 겹친다면 해당 파일에 대한 기존 백업을 먼저 확보하세요.

## v1.0.4 폴더형 배포

ZIP 전체를 새 폴더에 압축 해제하여 실행합니다. 메인 EXE와 작업용 EXE, `_internal`, `worker-runtime`, `TranslationData`, `Backend`를 함께 유지하세요. 실행 시 자체 압축을 푸는 단일 EXE 배포를 폴더형으로 바꿨습니다. 수정 tNVSE의 대응 소스는 `Licenses-and-Source`에 일반 파일로 제공합니다. 번역 사전·UI ESP·폰트·수정 DLL은 v1.0.3과 동일합니다. 넥서스의 검사 통과를 보장하는 변경은 아닙니다.

재현 빌드는 `.github/workflows/folder-patcher-build.yml`과 `tools/build_folder_release.py`를 사용합니다. 이전 버전 전용 폰트·키 안내 재패키징 도구는 당시 단일 EXE를 다루는 역사적 도구입니다.

## v1.0.1 폰트 수정

나눔스퀘어 ExtraBold에서 실제 글리프 외곽선이 비어 있는 CP949 확장 한글(예: 겍·걕·괙)의 누락을 방지하기 위해 6개 tNVSE 폰트 슬롯을 Pretendard Bold로 변경했습니다. 기존 수정 tNVSE.dll 및 번역 자료는 바이너리 단위로 그대로 유지했습니다. 실제 게임 검증은 별도입니다.

## 배포 상태

`v1.0.1`부터 프로필 선택 없이 설치된 기존 번역 대상 전체를 처리합니다. 같은 파일명의 모드별 변형도 각각 검증하며, 프로필 활성화·우선순위는 변경하지 않습니다. 기본 실행 및 자동 검증은 완료했지만 전 구간 플레이·문맥 검수는 미완료이므로 데이터의 `translation_ready=false`는 유지합니다.

- 이전 버전의 생성 시험: 298.1초, 307개 파일, 플러그인 표시 문자열 275,665곳 적용. 새 버전의 전체 대상 생성 결과는 릴리즈 설명을 참조하세요.
- 대응 Translation 파일이 있는 JSON 11개는 원본 유지.
- 사용자 환경에서 새 게임 및 Fallout 3 구역 시험. 전 구간 안정성은 미검증.

다운로드 ZIP에는 실행파일과 구성요소의 이용 허락·수정 tNVSE 대응 소스를 포함합니다. `TranslationData` 별도 ZIP은 설치용 ZIP의 TranslationData 폴더에 동봉된 번역 자료의 재현용 사본입니다. 일반 모드는 설치된 ESP/ESM에 번역 매핑을 적용하며, 모드별 완성 번역 파일이나 전체 Output을 배포하지 않습니다. 한국어 UI용 `NSKR UI Strings.esp` 1개는 문자열 GMST로 구성된 완성 플러그인으로 동봉되며, 실행 시 Output에 복사됩니다. 별도 번역자료 ZIP에도 같은 UI ESP가 포함됩니다. 따라서 현재 배포를 플러그인 없는 배포로 설명하지 않습니다.

## 개발 및 재현

Python과 개발 의존성은 `requirements.txt`를 참조하세요. 원본 설치 및 XEditLib 백엔드는 별도로 필요합니다.

```powershell
python -m unittest discover -s tests
python ns_inventory.py --mo2 C:\Modlists\NuclearSunset
python tools/build_development.py --catalog PATH_TO_TranslationData --mo2 C:\Modlists\NuclearSunset --profile "A - Uranium Haze NVR High" --backend PATH_TO_XEDIT_BACKEND --destination dist
```

공개된 `TranslationData`를 풀어 카탈로그 경로로 사용합니다. `build_release.ps1`은 정식 검수 완료 카탈로그만 허용하므로 시험판 빌드에는 사용하지 않습니다. 소스 저장소의 기본 카탈로그는 배포용 전체 데이터가 아닌 자리표시자입니다. 번역 자료와 각 구성요소의 권리는 각 권리자에게 있으며, 웹사이트 번역 허락이 제3자 자산의 재배포 허락을 뜻하지 않습니다.

## TTW 사전 커버리지 사전 점검 (2026-10-10)
- 선택 프로필: A - Uranium Haze NVR High
- 활성 모드 1,633개, 활성 플러그인 252개 / 252개 소스 확인
- VNV SST와 이름이 겹치는 플러그인 19개, 사전 후보 87,571행 (실제 적용 건수 아님)
- 기존 MCM/INI 사전과 이름이 겹치는 텍스트 5개
- FO3, DLC 및 TTW 핵심 마스터 8개는 별도의 SST 검수 필요

사전 후보 생성: py -3 tools/import_vnv_catalog.py --vnv-catalog PATH_TO_EXISTING_VNV_CATALOG --output .local/ns-sst-candidate
