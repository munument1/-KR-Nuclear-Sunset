---
sidebar_position: 6.5
title: 한국어 패치 설치
sidebar_label: 한국어 패치 설치
---

# Nuclear Sunset 한국어 패치 설치

Nuclear Sunset 설치를 마치고 **영문 상태에서 게임이 정상 실행되는지** 확인한 뒤 적용하세요. 한국어 패쳐는 번역 파일을 별도 `Output`에 생성하며, 원본 모드나 MO2 프로필을 직접 수정하지 않습니다.

## 배포 구성과 번역 적용 방식

현재 안내 기준은 [v1.0.3](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v1.0.3)입니다.

- **일반 모드 번역:** 설치된 ESP/ESM을 읽고 레코드·필드·현재 원문에 맞는 번역 데이터를 적용해 Output을 생성합니다. 일반 모드의 완성된 번역 플러그인을 통째로 넣어 교체하는 방식은 아닙니다.
- **한국어 UI 지원:** `NSKR UI Strings.esp`는 패쳐에 포함된 완성 플러그인을 Output으로 복사합니다. 문자열 GMST로 구성된 한국어 UI 지원 파일이며, 일반 모드에 번역 사전을 적용하는 경로와 별개입니다.
- **기타 구성요소:** 한국어 폰트·수정 tNVSE·라디오 자막 및 UI 실행 중 번역 자료가 포함됩니다. 별도 `TranslationData` ZIP은 실행파일에 포함된 번역 자료의 재현용 사본이며, 여기에도 같은 UI ESP가 들어 있습니다. 일반 설치에는 별도 번역자료 ZIP이 필요하지 않습니다.

게임과 Nuclear Sunset 모드리스트는 먼저 별도로 설치해야 합니다. 현재 패쳐는 **UI용 ESP 1개를 포함**하므로, 플러그인이 전혀 없는 배포물은 아닙니다.

## 설치 방법

1. [tNVSE Font Plugin](https://www.nexusmods.com/newvegas/mods/95088?tab=files)에서 **tNVSE 본체**와 **tNVSE Default Config**를 내려받아 MO2에 각각 설치·활성화합니다. 이미 설치했다면 이 단계는 건너뛰세요.
2. [최신 한국어 패쳐](https://github.com/munument1/-KR-Nuclear-Sunset/releases/latest)의 **Assets**에서 설치용 ZIP(현재 `NuclearSunset-Korean-Patcher-v1.0.3.zip`)을 내려받고 압축을 풉니다.
3. 게임과 MO2를 종료한 뒤 `NuclearSunsetKoreanPatcher.exe`를 실행합니다. `ModOrganizer.ini`가 있는 **Nuclear Sunset MO2 폴더**를 선택합니다. (`mods` 또는 게임 `Data` 폴더가 아닙니다.)
4. **MCM·Translations**, **폰트·수정 tNVSE**, **전체 대상 플러그인 번역**을 모두 선택하고 **Output 생성**을 누릅니다. 완료 후 결과 보고서를 확인하고, 오류로 실패한 Output은 설치하지 마세요.
5. 덮어쓸 기존 모드 파일을 백업한 다음, `Output/mods` **안에 있는 모드 폴더들**을 MO2의 실제 `mods` 폴더에 복사해 병합합니다. `Output` 폴더 전체를 하나의 모드로 설치하지 마세요.
6. MO2 왼쪽 목록에서 Output에 추가된 다음 한국어 모드 4개를 활성화합니다.
   - `Nuclear Sunset - Korean Fonts for tNVSE`
   - `Nuclear Sunset - Korean UI Strings`
   - `Nuclear Sunset - Radio Captions`
   - `Nuclear Sunset - Korean UI Runtime Translations`
7. 한국어 모드들은 원본 **tNVSE**와 **tNVSE Default Config**보다 **아래쪽(높은 우선순위)**에 두고, `Korean UI Runtime Translations`는 `Korean Fonts for tNVSE`보다 아래에 둡니다. MO2 오른쪽 **Plugins**에서 `NSKR UI Strings.esp`를 활성화한 뒤 기존 Nuclear Sunset 실행 항목으로 게임을 실행합니다.

> **주의:** 원본 tNVSE를 삭제하지 마세요. MO2에 누락 마스터 경고가 있다면 먼저 해결하세요. 새 한국어 모드와 플러그인의 활성화 상태는 사용하는 프로필마다 확인해야 합니다.

**v1.0.1 폰트 수정:** 기존 나눔스퀘어 대신 Pretendard Bold를 사용하는 한국어 폰트 설정이 포함됩니다. 이전 버전 이용자도 패쳐를 새로 실행해 `Nuclear Sunset - Korean Fonts for tNVSE` 폴더를 다시 덮어쓰세요. v1.0.2의 터미널 해킹 폰트 조정과 v1.0.3의 키 안내 인코딩 수정 등 이후 변경사항은 [릴리즈 노트](https://github.com/munument1/-KR-Nuclear-Sunset/releases/latest)를 확인하세요.

## 업데이트·되돌리기

모드팩을 업데이트했다면 최신 패쳐의 지원 범위와 릴리즈 노트를 확인한 뒤 Output을 다시 생성하세요. 이전 Output을 새 버전 모드에 그대로 덮어쓰지 마세요. 사전과 현재 원문이 달라진 문구는 미번역으로 남을 수 있습니다. 동봉된 UI ESP는 설치 원본에서 매번 새로 만드는 파일이 아니므로, 모드팩 업데이트에 맞는 패쳐 버전을 사용해야 합니다. 되돌릴 때는 한국어 모드와 `NSKR UI Strings.esp`를 비활성화하고, 덮어쓴 기존 파일을 백업본으로 복원하면 됩니다.

패쳐의 상세 동작과 검증 범위는 [GitHub README](https://github.com/munument1/-KR-Nuclear-Sunset/blob/main/patcher/README.md)를 참고하세요.
