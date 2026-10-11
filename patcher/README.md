# Nuclear Sunset 한국어 패쳐 — 시험 배포판

[다운로드](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v0.1.0-beta.1) · [설치 안내](https://munument1.github.io/-KR-Nuclear-Sunset/docs/main/korean-patch)

Viva New Vegas 패쳐를 기반으로 Nuclear Sunset / TTW에 맞춘 한국어 패쳐입니다. 설치된 모드를 읽어 별도 `Output/mods`를 생성하며 원본 모드와 프로필은 직접 수정하지 않습니다.

## 배포 상태

`v0.1.0-beta.1`은 시험 배포판입니다. 검증한 실행파일의 내부 버전은 `0.1.0-dev`이며 개발 검수용 문구는 의도적으로 유지했습니다. `translation_ready=false`입니다. 전 구간 문맥·안정성 검수가 완료된 정식 번역은 아닙니다.

- 공개 실행파일의 전체 생성 시험: 298.1초, 307개 파일, 플러그인 표시 문자열 275,665곳 적용.
- 적용 대상 미일치·경고·제외 0건, 저장 결과 재검증 및 출력 해시 검사 통과.
- 대응 Translation 파일이 있는 JSON 11개는 원본 유지.
- 사용자 환경에서 새 게임 및 Fallout 3 구역 시험. 전 구간 안정성은 미검증.

다운로드 ZIP에는 검증한 실행파일과 구성요소의 이용 허락·수정 tNVSE 대응 소스를 포함합니다. `TranslationData` 별도 ZIP은 같은 실행파일에 포함된 번역 자료의 재현용 사본입니다. 게임·모드 ESM/ESP 전체나 시험 Output은 배포하지 않습니다. 생성되는 `NSKR UI Strings.esp`는 GMST 전용 별도 구성입니다.

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
