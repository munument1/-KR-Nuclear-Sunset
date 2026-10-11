---
sidebar_position: 6.5
title: 한국어 패치 설치
sidebar_label: 한국어 패치 설치
---

# Nuclear Sunset 한국어 패치 설치

Nuclear Sunset 설치와 영어 상태의 정상 실행 확인을 마친 뒤 진행하세요. 한국어 패쳐는 **설치된 기존 번역 대상 전체**를 처리합니다. 프로필을 선택하거나 새로 만들 필요가 없으며, 비활성 모드의 번역 대상과 같은 파일명의 모드별 변형도 각각 원문·레코드 경로를 검증해 처리합니다.

기본 실행과 자동 검증은 완료했지만 전 구간 플레이 테스트는 미완료입니다. 모든 영어 문구와 추가 설치 모드까지 번역한다는 뜻은 아닙니다.

## 필수 선행 작업: tNVSE 설치

한국어 패쳐를 실행하기 전에 **tNVSE Font Plugin**을 별도로 설치하고 활성화해야 합니다.

1. [tNVSE Font Plugin (Nexus Mods)](https://www.nexusmods.com/newvegas/mods/95088?tab=files)에서 **tNVSE 본체**와 **tNVSE Default Config**를 다운로드합니다.
2. Nuclear Sunset의 **MO2**에 두 파일을 각각 모드로 설치하고, 왼쪽 모드 목록에서 **둘 다 활성화**합니다. 이미 설치·활성화되어 있다면 다시 설치할 필요는 없습니다.
3. 이후 아래 절차에 따라 한국어 패쳐를 실행합니다. 패쳐가 만든 한국어 폰트·설정 모드는 기존 **tNVSE 및 tNVSE Default Config보다 아래쪽(높은 덮어쓰기 우선순위)**에 배치합니다.

> **중요:** 패쳐의 `폰트·수정 tNVSE` 항목은 기존 tNVSE 본체의 별도 설치·활성화 단계를 생략해도 된다는 뜻이 아닙니다.

## 1. 다운로드

1. [GitHub 릴리즈 v1.0.0](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v1.0.0)에서 `NuclearSunset-Korean-Patcher-v1.0.0.zip`을 다운로드합니다.
2. 쓰기 가능한 별도 폴더에 압축을 풉니다. ZIP 안에서 직접 실행하지 마세요.
3. 게임과 MO2를 종료합니다. 기존 세이브는 별도로 보존하세요.

`TranslationData` ZIP은 개발·재현용이며 일반 설치에는 필요하지 않습니다. 게임 원본이나 완성된 번역 Output은 배포하지 않습니다.

## 2. 전체 Output 생성

1. `NuclearSunsetKoreanPatcher.exe`를 실행합니다.
2. **Nuclear Sunset MO2 폴더**에서 `ModOrganizer.ini`가 있는 설치 폴더를 선택합니다. `mods`나 게임 `Data` 폴더를 선택하지 마세요.
3. MCM·Translations, 폰트·수정 tNVSE, 전체 대상 플러그인 번역의 세 항목을 모두 선택하고 **Output 생성**을 누릅니다.
4. 완료 메시지가 나올 때까지 기다립니다. 설치된 파�� 수와 PC·저장장치 성능에 따라 소요 시간이 달라집니다.
5. **결과 보고서 열기**에서 오류·미대응·제외 내용을 확인합니다. 실패한 Output을 설치하지 마세요. 카탈로그와 달라진 파일에는 정확히 대응되는 문구만 적용합니다.

패쳐는 원본 모드·프로필을 직접 수정하지 않고 실행파일 옆에 `Output/mods`를 생성합니다. 기존 Output이 있으면 날짜가 붙은 새 폴더에 생성합니다. 대응 Translation이 함께 있는 JSON은 원본으로 두고 Translation 쪽에 번역을 적용합니다.

## 3. MO2에 적용

1. 변경 대상 기존 모드 폴더를 별도 위치에 보관합니다. 적용을 되돌릴 때 필요합니다.
2. `Output/mods` **안의 모드 폴더들**을 Nuclear Sunset의 실제 MO2 모드 저장 폴더에 복사합니다. 기본 예시는 `C:\Modlists\NuclearSunset\mods`이며, MO2 경로 설정을 변경했다면 설정된 위치를 사용하세요.
3. 원래 모드명·하위 경로를 유지하고 같은 이름의 파일을 덮어씁니다. Output 전체를 하나의 모드로 설치하거나 게임 `Data`에 복사하지 마세요.
4. MO2에서 다음 새 모드를 활성화합니다.
   - `Nuclear Sunset - Korean Fonts for tNVSE`
   - `Nuclear Sunset - Korean UI Strings`
   - `Nuclear Sunset - Radio Captions`
   - `Nuclear Sunset - Korean UI Runtime Translations`
5. 위 모드들은 기존 tNVSE 및 `tNVSE Default Config`보다 아래쪽, 즉 **더 높은 덮어쓰기 우선순위**에 둡니다. `Korean UI Runtime Translations`는 `Korean Fonts for tNVSE`보다 아래에 둡니다. 기존 tNVSE 모드는 삭제하지 마세요.
6. 오른쪽 **Plugins**에서 `NSKR UI Strings.esp`를 활성화하고 해당 마스터들 및 기존 UI 문자열을 덮어쓰도록 뒤에 배치합니다. 나머지 세 모드에는 활성화할 ESP가 없습니다. 누락 마스터 경고가 있으면 실행하지 마세요.
7. 기존 Nuclear Sunset 실행 항목으로 게임을 실행합니다.

**기존 모드 파일은 프로필 간 공유되므로 번역 Output을 한 번 적용하면 나중에 다른 프로필에서도 해당 번역 파일을 사용합니다.** 프로필마다 패쳐를 다시 실행할 필요는 없습니다. 다만 MO2의 활성화·우선순위 설정은 프로필별이므로, 새 한국어 모드 4개와 `NSKR UI Strings.esp`는 사용할 각 프로필에서도 활성화해야 합니다. 패쳐가 기존 프로필 설정을 자동 변경하지는 않습니다.

## 주의·복구

- `FO3 KR.esm`이나 기존 `TTW KOR Radio + UI.esp`를 추가로 설치·활성화할 필요가 없습니다. 필요한 번역과 분리된 UI·라디오 구성을 패쳐가 제공합니다.
- 게임이 영어 상태에서도 충돌한다면 먼저 Nuclear Sunset 원본 설치 절차와 4GB 패치 상태를 확인하세요. 이 패쳐는 4GB 패치를 자동 수행하지 않습니다.
- 되돌리려면 새 한국어 모드들과 `NSKR UI Strings.esp`를 비활성화하고, 덮어쓴 기존 파일을 보관한 원본으로 복원하세요.
- Wabbajack 업데이트로 원본 모드가 바뀌면 이전 Output을 재사용하지 말고 새 설치본으로 다시 생성하세요.
- 오류 제보에는 모드팩 버전·문제 화면·패쳐 결과 보고서·충돌 로그를 첨부하세요. 개인정보가 없는지 먼저 확인하세요.
