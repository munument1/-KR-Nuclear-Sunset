---
sidebar_position: 6.5
title: 한국어 패치 설치
sidebar_label: 한국어 패치 설치
---

# Nuclear Sunset 한국어 패치 설치

Nuclear Sunset 설치를 마치고 영어 상태에서 정상 실행되는지 확인한 다음 진행하세요. 이 패치는 비공식 **시험 배포판**이며, 모든 구간의 번역 문맥과 게임 안정성이 검증된 정식판은 아닙니다.

## 1. 다운로드와 준비

1. [GitHub 릴리즈 v0.1.0-beta.1](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v0.1.0-beta.1)에서 `NuclearSunset-Korean-Patcher-v0.1.0-beta.1.zip`을 다운로드합니다.
2. 쓰기 가능한 별도 폴더에 압축을 풉니다. ZIP 안에서 직접 실행하지 마세요.
3. MO2에서 현재 프로필을 복사해 한국어 시험용 프로필을 만드세요. 기존 세이브는 별도로 보존하세요.

`TranslationData` ZIP은 개발·재현용이며 일반 설치에는 필요하지 않습니다. 게임 원본이나 완성된 번역 Output은 다운로드에 포함되지 않습니다.

## 2. Output 생성

1. `NuclearSunsetKoreanPatcher-Dev.exe`를 실행합니다. 검증한 실행파일을 그대로 배포하므로 창의 개발 검수용 표시와 내부 버전 `0.1.0-dev`는 정상입니다.
2. **Nuclear Sunset MO2 폴더**에서 `ModOrganizer.ini`가 있는 설치 폴더를 선택합니다. `mods`나 게임 `Data` 폴더를 선택하지 마세요.
3. **MO2 프로필**에 번역할 프로필 이름을 정확히 입력합니다. 시험용 프로필을 복사했다면 해당 이름으로 바꾸세요.
4. MCM·Translations, 폰트·수정 tNVSE, 플러그인 번역의 세 항목을 모두 선택한 상태로 **검수용 Output 생성**을 누릅니다. 플러그인 시험 확인창에 동의합니다.
5. 생성 완료 메시지를 기다립니다. 시험 환경에서는 약 5분 걸렸지만 PC와 저장장치에 따라 달라집니다.
6. **결과 보고서 열기**에서 오류·미대응·제외 내용을 확인합니다. 실패한 Output을 설치하지 마세요. 다른 모드팩 버전이나 추가 모드는 대응되지 않을 수 있습니다.

패쳐는 원본 모드·프로필을 수정하지 않고 실행파일 옆에 `Output/mods`를 생성합니다. 기존 Output이 있으면 날짜가 붙은 새 폴더에 생성합니다. 대응 Translation이 함께 있는 JSON은 원본으로 두고 Translation 쪽에 번역을 적용합니다.

## 3. MO2에 적용

게임과 MO2를 닫은 상태에서 진행하세요.

1. 기존 파일을 덮어쓰기 전에 변경 대상 모드 폴더를 별도 위치에 보관합니다. 그래야 한국어 적용을 되돌릴 수 있습니다.
2. `Output/mods` **안의 모드 폴더들**을 Nuclear Sunset의 실제 MO2 모드 저장 폴더에 복사합니다. 기본 예시는 `C:\Modlists\NuclearSunset\mods`이며, MO2 경로 설정을 변경했다면 설정된 위치를 사용하세요.
3. 원래 모드명·하위 경로를 그대로 유지하고 같은 이름의 파일은 덮어씁니다. Output 전체를 하나의 모드로 설치하거나 게임 `Data`에 복사하지 마세요.
4. MO2를 열고 시험용 프로필에서 다음 새 모드를 활성화합니다.
   - `Nuclear Sunset - Korean Fonts for tNVSE`
   - `Nuclear Sunset - Korean UI Strings`
   - `Nuclear Sunset - Radio Captions`
   - `Nuclear Sunset - Korean UI Runtime Translations`
5. 위 모드들은 기존 tNVSE 및 `tNVSE Default Config`보다 아래쪽, 즉 **더 높은 덮어쓰기 우선순위**에 둡니다. 특히 `Korean UI Runtime Translations`는 `Korean Fonts for tNVSE`보다 아래에 둡니다. 기존 tNVSE 모드는 삭제하지 마세요.
6. 오른쪽 **Plugins**에서 `NSKR UI Strings.esp`를 활성화하고 해당 마스터들 및 기존 UI 문자열을 덮어쓰도록 뒤에 배치합니다. 나머지 세 모드에는 별도로 활성화할 ESP가 없습니다. 누락 마스터 경고가 있으면 실행하지 마세요.
7. 기존 Nuclear Sunset 실행 항목으로 새 게임을 시험합니다. 한글, 시작 안내창, 아이템 설명, MCM, 라디오 자막을 확인하세요.

MO2의 모드 파일은 프로필 간 공유됩니다. 시험용 프로필을 복사했다고 해서 덮어쓴 기존 모드 파일이 다른 프로필에서 격리되는 것은 아닙니다.

## 주의·복구

- `FO3 KR.esm`이나 기존 `TTW KOR Radio + UI.esp`를 추가로 설치·활성화할 필요가 없습니다. 필요한 번역과 분리된 UI·라디오 구성을 패쳐가 제공합니다.
- 게임이 기본 영어 상태에서도 충돌한다면 먼저 Nuclear Sunset 원본 설치 절차와 4GB 패치 상태를 확인하세요. 이 패쳐가 4GB 패치를 자동 수행하지는 않습니다.
- 번역 적용을 되돌리려면 새 한국어 모드들과 `NSKR UI Strings.esp`를 비활성화하고, 덮어쓴 기존 모드 파일을 보관한 원본으로 복원하세요.
- Wabbajack 업데이트로 원본 모드가 바뀌면 예전 Output을 그대로 재사용하지 말고 새 설치본으로 다시 생성하세요.
- 오류 제보에는 모드팩 버전·프로필·문제 화면·패쳐 결과 보고서·충돌 로그를 첨부하세요. 세이브나 보고서에 개인정보가 없는지 먼저 확인하세요.

전체 출력 자동 검사는 통과했지만 전 구간 플레이·문맥 검수까지 완료된 것은 아닙니다. 남은 영어·오역·환경별 충돌이 있을 수 있습니다.
