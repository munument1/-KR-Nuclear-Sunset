# Nuclear Sunset / Viva New Vegas 지명 표기 일관성 감사 (2026-10-19)

## 범위와 근거

- **기준 영어 및 한국어:** `/folder/뉴베가스 용어집 (1).txt`의 “장소 및 지명” 항목(111–148행), `/folder/뉴베가스 세력 단어집.txt`의 정착지 진영(53–67행). 전자는 `New Vegas → 뉴 베가스`, `Nipton → 닙튼`, `Old Mormon Fort → 구 몰몬 요새`, `Camp Golf → 캠프 골프`, `Mojave Wasteland → 모하비 황무지`, `Goodsprings → 굿스프링스`, `Hoover Dam → 후버 댐`을 명시한다.
- **NS 감사/적용 파일:** `../.local/key-prompt/TranslationData/catalog.json` (284개 파일 항목, **298,298**개 mapping). 동일 번역 행을 가진 `../.local/hacking-work/TranslationData/catalog.json`과 비교했으며 두 로컬 복사본은 번역 `files` 배열이 동일했다.
- **NS 게시 릴리스:** GitHub [v1.0.4](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v1.0.4)의 `NuclearSunset-TranslationData-v1.0.4.zip`을 내려받아 압축 속 `TranslationData/catalog.json`의 **284개 `files` 전체와 298,298개 mapping 전체**가 수정 전 `key-prompt` 작업본과 **정확히 동일**함을 JSON으로 확인. 압축본 내 카탈로그 SHA-256은 `642275c1cd38b347a809ecd07edbf85b7bc22bacf8836b3af2efcfca109d8918`; 작업본 수정 전은 `98cc053e9d5036b50f8ffc245e45e3cd595e82b514d6270e05c220825b8915fe`. 바이트 해시 차이는 `version=1.0.4`, `packaging=folder`, `font_bundle` 등의 메타데이터에서 발생한다. **번역 행의 내용은 같다.** 릴리스 ZIP SHA-256: `ffa78eec3126a886efe216bcc89e0f8af6f326fa9189397e79ca8f1f9cc5bcbc`.
- **VNV 감사 파일:** `../../../patcher/.build-resources/key-prompt/TranslationData/catalog.json` (52개 파일 항목, **119,885**개 mapping). `../../../patcher/.build-resources/TranslationData/catalog.json`과 비교 시 번역 `files` 배열 동일. 두 제품의 값은 **카탈로그 원본/후보 값**이며 MO2 설치 순서에서 최종 승리하는 레코드의 인게임 표시 여부는 따로 확인해야 한다.
- **집계 기준:** 원본 `source`에 영어 고유명사를 단어 경계로 포함하고, 번역 `dest`에 해당 한글 표기를 포함하는 **카탈로그 mapping 행 수**. 동일한 기본 레코드가 다른 ESP/ESM에서 재정의되면 각각 센다. 서술상 동일하더라도 번역 필드 전체가 다른 경우와 지명 자체가 다른 경우를 구별한다.

## 적용 완료: NS 확정 표기 55개 mapping

교정 대상은 지명 영어 원문과 한국어 대체형이 **동일한 mapping**에 존재하는 경우로만 제한했다. 독립 도구 `../tools/normalize_place_names.py`를 통해 백업 후 `key-prompt` 카탈로그의 해당 `dest` 문자열만 치환했다.

| 영어 원문 포함 | 통일된 지명 | NS 수정 전 표기 분포¹ | 실제 수정 | 출처 · 정확 레코드 예시 |
|---|---|---:|---:|---|
| `New Vegas` | **뉴 베가스** | 뉴 베가스 647 / 뉴베가스 39 | **39** | `Vanilla Enhancements.esm` → `falloutnv.esm:11a0c5`, `QUST/NNAM`, `Objectives\\[1]\\NNAM`, 원문 “Return to Emily Ortal on the New Vegas Strip…”; `TweaksTTW.esm` → `tweaksttw.esm:0028ee`, `REFR/FULL`, `XMRK\\FULL` (`New Vegas`) |
| `Nipton` | **닙튼** | 닙튼 255 / 닙톤 3 / 닙턴 2 | **5** | `A World of Pain Revised.esm` → `a world of pain revised.esm:02e4a2`, `CELL/FULL`, `Nipton Sewer → 닙톤 하수도`; `Sweet Pain NV.esm`이 **동일 레코드**를 `닙턴 하수도`로 번역; `LegionRadio.esp:00489b`, `INFO/RNAM`에도 닙턴 |
| `Old Mormon Fort` | **구 몰몬 요새** | 구 몰몬 요새 92 / 올드 몰몬 요새 10 | **10** | `NVMMP.esp:000e1a` `REFR/FULL` (`Old Mormon Fort`); `NS.esm:0213d1` `MESG/FULL` 및 `DESC`; `NS.esp`이 `falloutnv.esm:147da0` `INFO/NAM1` 원본 표기를 바꾼 사례 |
| `Camp Golf` | **캠프 골프** | 캠프 골프 120 / 골프 캠프 1 | **1** | `TweaksTTW.esm` → `tweaksttw.esm:04ce69`, `REFR/FULL`, `XMRK\\FULL`, `Camp Golf → 골프 캠프` |

¹ `source`가 해당 지명을 포함하면서 **번역문에 해당 한글 표기가 실제로 나오는 행**만 적었다. 일부 문장은 지명을 생략·의역하므로 `source` 총수와 차이가 난다. 수정 전 원문 매핑은 각각 New Vegas 694, Nipton 264, Old Mormon Fort 102, Camp Golf 123행이다.

- 55건의 수정 발생 위치는 총 **19개 NS 플러그인**이다. `New Vegas` 39건 가운데 `gemini_candidate` 36건, `sst_direct` 3건. `Old Mormon Fort` 10건은 전부 `gemini_candidate`. `Nipton` 5건은 `sst_direct` 2건과 `gemini_candidate` 3건. `Camp Golf` 1건은 `gemini_candidate`.
- 동일 원본 ID를 서로 다른 모드가 덮는 사례까지 각각 고쳤다. 특히 `a world of pain revised.esm:02e4a2 CELL/FULL` 세 공급자(`A World of Pain Revised.esm`, `A World of Pain NV Roombound Project.esm`, `Sweet Pain NV.esm`)의 `Nipton Sewer`가 모두 **닙튼 하수도**로 통일됐다.
- 변경 내용은 `dest` **55개 직렬화 행에 국한**된다. 백업과 수정본을 328만여 줄 순서대로 비교해 변경된 줄이 정확히 55개이며 전부 `"dest":` 줄임을 확인했다. 백업 JSON을 같은 규칙으로 재변환한 전체 객체가 수정본 전체 객체와 일치한다. `source`, `owner`, `id`, `signature`, `field`, `path`, 필드 순서, 태그, 이스케이프, 개행은 보존됐다.

**검증과 복구**

- 적용 전 SHA-256: `98cc053e9d5036b50f8ffc245e45e3cd595e82b514d6270e05c220825b8915fe`.
- 적용 후 SHA-256: `98dd0b15dbec1ca1fd367223b93d81b5fe85ada635e3206105b0e72b678b0e09`.
- 백업: `../.local/place-name-backups/20261019T071639702349Z-98cc053e9d50/catalog.json`. 검증용 `manifest.json` 같은 폴더에 있음. 백업과 수정본의 SHA-256 확인 완료.
- 테스트: `python -m unittest discover -s tests -p test_place_name_normalization.py -v` → **3/3 통과**. `python tools/normalize_place_names.py --check` → **잔여 수정 0**.
- 복구: NS `patcher` 작업 폴더에서 `python tools/normalize_place_names.py --restore .local/place-name-backups/20261019T071639702349Z-98cc053e9d50/manifest.json`. 현재 카탈로그가 위 “적용 후” SHA와 정확히 일치할 때만 복구한다.
- 후속 빌드: v1.0.4 실제 폴더형 패키징은 `origin/main:patcher/tools/build_folder_release.py`에서 **v1.0.3 아카이브를 풀어 PyInstaller onedir로 재컴파일**한다. `tools/prepare_release_package.py`는 구형 빌드 경로이므로, 단순히 `--catalog .local/key-prompt/TranslationData`를 전달해도 **v1.0.5 폴더형 배포에 55건이 자동 반영되지 않는다**. 차기 폴더형 빌드에는 **공식 v1.0.4 번역 자산 전체를 출발점으로 정확한 지명 `dest` 변경 55건과 이후 워커 수정(번역 이력 `previous_dests`, 신규 NVSE runtime 등)을 병합**해야 한다. 이를 위해 독립 스크립트 `../tools/build_v1_0_5_folder_release.py`를 작성했다. `--preflight`로 아카이브 해시와 카탈로그 연결을 검증하고, `--build`는 최신 `origin/main` 소스 통합 후 PyInstaller로 GUI·워커를 새로 만든다. `--overlay-dir`은 선택적 추가 `TranslationData/`, `Backend/`, `Licenses-and-Source/` 자료의 폴더형 입력이며, 해당 자산에 대한 catalog SHA 갱신도 필요하다. 기존 `.local/hacking-work`나 GitHub 공개 v1.0.4 ZIP에는 현재 교정이 자동 반영되지 않으며, 빌드 결과는 먼저 **candidate**로 검증해야 한다.

새 빌더 실행 예시(NS `patcher` 작업 디렉터리):

```powershell
python tools/build_v1_0_5_folder_release.py --preflight
python tools/build_v1_0_5_folder_release.py --baseline-check
# origin/main onedir 코드가 현재 브랜치에 머지/체리픽된 뒤:
python tools/build_v1_0_5_folder_release.py --build
python tools/build_v1_0_5_folder_release.py --package-check --candidate .local/v1.0.5-folder-candidate/output/NuclearSunset-Korean-Patcher-v1.0.5-candidate.zip
```

`--build`는 기본으로 `.local/place-name-release-reference-v1.0.4/`의 **GitHub 공식 v1.0.4 ZIP 두 개**를 검증하고, `.local/key-prompt/TranslationData/catalog.json`의 안전한 변경을 반영한다. 카탈로그 내 기존 영어 source/레코드 식별자 유실은 거부하지만, 55건 외의 신규 번역과 `previous_dests` 별칭은 유지한다. `--overlay-dir`을 주면 추가 runtime 등 파일을 가져오며, 현재 TranslationData에 있는 새 runtime payload 역시 catalog에 기록된 SHA가 일치할 때 자동 동기화한다. PyInstaller용 Python 소스 스냅샷과 SHA, 실행 파일 및 런타임을 포함한 **폴더형 후보 ZIP 2개**, SHA256SUMS, build-report를 생성한다. 현재 작업 브랜치 `fix/key-prompt-encoding`에서는 origin/main의 onedir 빌드 이력이 아직 없으므로 **실제 v1.0.5 빌드는 차단**돼 있다. 공식 v1.0.4 ZIP의 압축을 해제해 실행한 `--package-check`는 통과했고(플러그인 246개 인식), 새 빌더 전용 테스트 5개도 통과했다.

## VNV 감사: 동일한 4개 확정 whitelist 충돌 **0건**

`../../../patcher/.build-resources/key-prompt/TranslationData/catalog.json`에서 동일한 `New Vegas / Nipton / Old Mormon Fort / Camp Golf` 원문 조건과 잘못된 대체형을 검사했지만 교정 대상은 **0건**이다. New Vegas 포함 원문 513행 중 507행의 번역에 **뉴 베가스**, Nipton 포함 원문 138행 중 134행에 **닙튼**, Old Mormon Fort 62행 중 62행에 **구 몰몬 요새**, Camp Golf 75행 중 74행에 **캠프 골프**가 존재했다(나머지는 문맥상 생략·변형 또는 원문 유지). **VNV 파일 수정 없음.**

그러나 별도 고유 장소명 불일치가 존재한다.

| 현상 | VNV 실증 값 | 근거 및 수정 지침 |
|---|---|---|
| **Mojave Outpost Barracks**의 재정의 번역 상충 | **모하비 전초기지 병영 5행**, **모하비 초소 막사 2행** | `falloutnv.esm:141aa5`, `CELL/FULL/FULL`. `FalloutNV.esm`, `Goodies.esp`, `Placement Fixes.esm`, `TLD_Travelers.esm`, `Atmospheric Lighting Tweaks.esp`는 전자. `YUP - Base Game + All DLC.esm`에는 후자 **2행**. 동일 레코드/공급자 중복 행도 있으므로 VNV 담당자에게 실제 winner 및 중복 원인 검증 후 후자를 **모하비 전초기지 병영**으로 통일하도록 제안. |
| **Zion** 계열의 시온 / 자이언 혼용 | Zion 포함 원문 217행 중 `시온` 193, `자이언` 19 (나머지 5는 직접 언급 없음) | `HonestHearts.esm` `honesthearts.esm:00683b WRLD/FULL`의 정확 원문 `Zion Canyon`은 **시온 협곡**으로 고정되어 있음(7행). VNV `MCM/SoMS.json`의 `Zion Clear Tint` 등은 **자이언**. 모드 설정 항목·Zion Valley/Trail·국립공원 여부를 구분해서 수동 검토. |
| **Silver Rush** 용어집과 배포 번역의 차이 | Silver Rush 포함 VNV 원문 40행은 전부 **실버 러시**; 정확 원문 `Silver Rush` 5행도 모두 실버 러시 | 용어집은 **실버 러쉬**. 기존 배포 사용량이 압도적이므로 어느 쪽을 공통 규칙으로 채택할지 먼저 결정해야 함. 결론 전 VNV 일괄 치환 보류. |

## NS 잔여 후보: 원문/맥락 확인 후 수동 결정

| 이름 | 관찰 수량 · 플러그인/레코드 예시 | 판단 |
|---|---|---|
| **Zion** | NS 원문 301행 중 **시온 255**, **자이언 41** (나머지 5). `HonestHearts.esm`의 `honesthearts.esm:00c5d7 REFR/XATO` `Exit to Zion Valley → 자이언 밸리로 나가기`와 `honesthearts.esm:00683b WRLD/FULL` `Zion Canyon → 시온 협곡`이 공존. `FiendsLeave.esm` 14행·`ZionTrail.esm` 5행에도 자이언. | Canyon / Valley / National Park / 고유 모드명 `Zion Trail` / 내부 퀘스트 스크립트 등 맥락이 다르므로 일괄 치환하지 말 것. `Zion Canyon`은 용어집의 **시온 협곡** 고정. |
| **Silver Rush** | NS Silver Rush 포함 59행 중 **실버 러시 58**, **실버 러쉬 1**. `Long15Reloaded.esm` → `long15reloaded.esm:00db46 INFO/NAM1 Responses\\[1]\\NAM1`: `Visit my sister at the Silver Rush sometime` → `실버 러쉬` 표기. | NS/VNV 다수 사용례는 실버 러시, 제공 용어집은 실버 러쉬. 표준 확정 뒤 분기 없이 통일. |
| **The Strip** | 정확 원문 `The Strip` NS **28행**, VNV **5행** 모두 `뉴 베가스`. NS `falloutnv.esm:13b308 WRLD/FULL` 등. | 용어집 `The Strip → 스트립`과 다르지만, 기존 베이스의 월드스페이스/평판 이름이라는 특성이 있어 기계 치환 금지. 실제 지도 라벨/월드스페이스 표시 확인 후 개별 결정. |
| **Quarry Junction** | 정확 원문 NS 2행, VNV 2행은 모두 **채석장 교차로**. 예: `falloutnv.esm:167f2c REGN/RDMP`. 용어집은 **채석장**. | 대역 차이이나 출판본 간 표기 충돌은 아님. `Junction`을 포함한 정확 지명인지 확인하고 용어집 변경 여부 결정. |
| **Mojave Outpost Barracks** | VNV에서 상충하던 `falloutnv.esm:141aa5 CELL/FULL`은 NS 카탈로그에서는 **모하비 전초기지 병영**으로 일관. | VNV 수정 시 NS와 같은 표기를 우선 추천. |

반면 `Mojave` 계열은 NS 1,356개 원문 중 1,330개가 `모하비`를 포함하고 VNV는 741개 중 724개가 포함한다. `Goodsprings`는 NS 360개 중 352개, VNV 184개 중 177개에 **굿스프링스**. `Megaton`은 NS 395개 중 390개, VNV 43개 중 43개에 **메가톤**. `Hoover Dam`은 NS 749개 중 732개, VNV 583개 중 565개에 **후버 댐**이 나타났으며 사전에 정의한 다른 철자 변형은 발견되지 않았다. 해당 이름이 번역문에서 생략된 행을 오역으로 일괄 판정하지 않았다.

**유의:** 이 감사는 소스/배포 데이터의 표기 정합성을 검증했다. 모드 선택 상태, 플러그인 load order, 인게임 UI 렌더링까지 재현한 검증은 아니다. `translation_ready=false`, `game_validation=pending` 개발 채널 카탈로그의 지명 교정이며, 새 배포물 제작/게시에는 별도의 패키징·게임 검증이 필요하다.
