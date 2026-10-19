# Nuclear Sunset 한국어 패쳐

[최신 다운로드](https://github.com/munument1/-KR-Nuclear-Sunset/releases/latest) · [설치 안내](https://munument1.github.io/-KR-Nuclear-Sunset/docs/main/korean-patch)

Viva New Vegas 패쳐를 기반으로 Nuclear Sunset / TTW에 맞춘 한국어 패쳐입니다. 설치된 모드를 읽어 별도 `Output/mods`를 생성하며 원본 모드와 프로필은 직접 수정하지 않습니다.

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
