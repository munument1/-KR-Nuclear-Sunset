---
sidebar_position: 6.5
title: 한국어 패치 설치
sidebar_label: 한국어 패치 설치
---

# Nuclear Sunset 한국어 패치 설치

Nuclear Sunset 설치를 마치고 **영문 상태에서 게임이 정상 실행되는지** 확인한 뒤 적용하세요. 한국어 패쳐는 번역 파일을 별도 `Output`에 생성하며, 원본 모드나 MO2 프로필을 직접 수정하지 않습니다.

## 설치 방법

1. [tNVSE Font Plugin](https://www.nexusmods.com/newvegas/mods/95088?tab=files)에서 **tNVSE 본체**와 **tNVSE Default Config**를 내려받아 MO2에 각각 설치·활성화합니다. 이미 설치했다면 이 단계는 건너뛰세요.
2. [한국어 패쳐 v1.0.1](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v1.0.1)에서 `NuclearSunset-Korean-Patcher-v1.0.1.zip`을 내려받고 압축을 풉니다.
3. 게임과 MO2를 종료한 뒤 `NuclearSunsetKoreanPatcher.exe`를 실행합니다. `ModOrganizer.ini`가 있는 **Nuclear Sunset MO2 폴더**를 선택합니다. (`mods` 또는 게임 `Data` 폴더가 아닙니다.)
4. **MCM·Translations**, **폰트·수정 tNVSE**, **전체 대상 플러그인 번역**을 모두 선택하고 **Output 생성**을 누릅니다. 완료 후 결과 보고서를 확인하고, 오류로 실패한 Output은 설치하지 마세요.
5. 덮어쓸 기존 모드 파일을 백업한 다음, `Output/mods` **안에 있는 모드 폴더들**을 MO2의 실제 `mods` 폴더에 복사해 병합합니다. `Output` 폴더 전체를 하나의 모드로 설치하지 마세요.
6. MO2 왼쪽 목록에서 생성된 다음 한국어 모드 4개를 활성화합니다.
   - `Nuclear Sunset - Korean Fonts for tNVSE`
   - `Nuclear Sunset - Korean UI Strings`
   - `Nuclear Sunset - Radio Captions`
   - `Nuclear Sunset - Korean UI Runtime Translations`
7. 한국어 모드들은 원본 **tNVSE**와 **tNVSE Default Config**보다 **아래쪽(높은 우선순위)**에 두고, `Korean UI Runtime Translations`는 `Korean Fonts for tNVSE`보다 아래에 둡니다. MO2 오른쪽 **Plugins**에서 `NSKR UI Strings.esp`를 활성화한 뒤 기존 Nuclear Sunset 실행 항목으로 게임을 실행합니다.

> **주의:** 원본 tNVSE를 삭제하지 마세요. MO2에 누락 마스터 경고가 있다면 먼저 해결하세요. 새 한국어 모드와 플러그인의 활성화 상태는 사용하는 프로필마다 확인해야 합니다.

**v1.0.1 폰트 수정:** 기존 나눔스퀘어 대신 Pretendard Bold를 사용하는 한국어 폰트 설정이 포함됩니다. 이전 버전 이용자도 패쳐를 새로 실행해 `Nuclear Sunset - Korean Fonts for tNVSE` 폴더를 다시 덮어쓰세요. 다른 번역 파일은 이전 버전과 동일합니다.

## 업데이트·되돌리기

모드팩을 업데이트했다면 이전 Output을 재사용하지 말고 패쳐를 다시 실행하세요. 되돌릴 때는 한국어 모드와 `NSKR UI Strings.esp`를 비활성화하고, 덮어쓴 기존 파일을 백업본으로 복원하면 됩니다.

패쳐의 상세 동작과 검증 범위는 [GitHub README](https://github.com/munument1/-KR-Nuclear-Sunset/blob/main/patcher/README.md)를 참고하세요.
