# #13 원인 및 수정 후보 — 2026-10-23

상태: 소스·바이너리 검증용 후보. **실게임 검증 전이며 정식 릴리스가 아니다.**

## 적용

`NuclearSunset-Korean-Patcher-v1.0.7-issue13-candidate.zip` 전체를 **새 폴더**에
압축 해제하고 패처를 실행해 새 Output을 생성한다. 기존 설치에 적용할 때는
동일 경로의 원본을 백업한 후 해당 Output을 적용한다. EXE 한 개만 복사하지 않는다.
전체 폴더를 유지해야 한다. 기존 v1.0.6 번역 자료 및 UI/폰트/DLL/INI는 그대로 포함된다.

검증용 게임 설치가 현재 없으므로 이 문서는 표시가 해결됐다는 실게임 확인을 대신하지 않는다.

## 사진별 확인

원본: <https://github.com/munument1/-KR-Nuclear-Sunset/issues/13>

|사진|표시|원인/처리|
|---|---|---|
|1|Danger Close, Internalize, Reject|`Vegas Elysium.esp`의 `SCPTOnHitElysium`가 `MessageBoxExAlt` 영어 리터럴을 사용. PERK/DESC 번역과 별개. 선택창 전체 및 버튼 수정.|
|2|Thug|`Enemy Rank Renaming`의 `gr_EnemyRankRenamer2.txt`가 Raider1Gun 계열을 `LNSetName`으로 재명명. 해당 명령의 이름 피연산자 수정.|
|3|Thug Brawler|같은 파일에서 Raider1Melee 계열 재명명. 이름 피연산자 수정.|
|4|Metal Butter Knife|`[ALT] - Misc Items and Crafting Tweaks`의 `gr_p20MICmiscnames.txt`가 Knife02 이름을 영어로 덮어씀. 사전에 이미 있는 한국어와 일치시킴.|
|5|Large Metal Pot|같은 스크립트가 BigPot 이름을 영어로 덮어씀. 정적 NS.esp/FULL 사전 누락이 아님.|
|6|(Inexplicable) Feminist Agenda 요구 조건 및 설명 깨짐|v1.0.3~1.0.5의 `sOr` CP949 회귀와 같은 선택창 손상 유형. 이 후보는 v1.0.6의 UTF-8 복원본을 그대로 포함. 이 사진도 실제로 해결되는지는 미검증.|
|7|Educated 설명|`SCPTOnLoadedBasePerks`가 INI `iEducatedLevelRate` 값으로 PERK 설명을 재작성. 1레벨/복수레벨 양 분기 번역, `%.0f`와 설정 계산 보존.|

7번 뒤쪽의 `Select a stat to increase` 팝업도 확인했다. Dynamic Scaling Level Stat Choice
1.2.0의 `nvse/user_defined_functions/DSLC_LevelUp.gek`가 생성한다. 제목과 체력/행동력/
휴대 중량 버튼 4개 리터럴을 번역하며, 설정 키와 실제 Actor Value 식별자는 그대로 둔다.
별도 `DSLC_Message.gek`의 버튼별 실제 능력치 계산도 변경하지 않는다.

## 직접 확인한 증거

- 공식 v1.0.6 TranslationData ZIP SHA-256:
  `e1b2ef051410f409ce461c8928f3f72b112d5b63904146f10c7a67d0112cd6b6`.
  해당 catalog의 Danger Close/PERK/DESC, 두 잡동사니/FULL, Feminist Agenda/PERK/DESC에
  한국어가 이미 있음. 사전만 다시 번역하는 방식으로는 런타임 덮어쓰기를 해결하지 못한다.
- 로컬 보관 Nuclear Sunset 1.0.2.2 `.wabbajack`의 InlineFile에서 실제
  `NS.esp`와 `gr_p20MICmiscnames.txt`를 읽었다. NS.esp SHA-256
  `29c237bc18133751fb9de138cd05644e64f7bb9d80502cd69ceeb9f923d461ea`는
  기존 감사 및 공식 카탈로그의 baseline과 일치한다.
- Nexus 원본 Enemy Rank Renaming 1.1 ZIP (mod 85605, file 1000126229),
  SHA-256 `a706a1902f9c0ce6909852be7f0e812812c0858a4663117d82ea3250dc65b043`.
  Wabbajack이 지시하는 버전과 일치. 두 스크립트 모두 확보하고 모든 활성 이름 변경을 검토했다.
  [원본 모드](https://www.nexusmods.com/newvegas/mods/85605), 제작 CluelessCourier / ESPless GRUmod.
- Dynamic Scaling Level Stat Choice 원본 1.2.0 ZIP (mod 92988, file 1000163988),
  SHA-256 `87f74ac40183fdcd6e7d0bdd1c70862f746ff22a00d6fd5de304289f23278e4d`.
  [원본 모드](https://www.nexusmods.com/newvegas/mods/92988), 제작 FinalCatalyst / S6S / Brandy.
  실제 `.gek` 원본 SHA-256도 고정하고, 알려진 번역본만 재실행을 허용한다.
- 이전 v1.0.4 실제 전체 Output에 보존된 두 ESP의 SCTX/SCDA를 직접 읽었다.
  Vegas Elysium 출력 SHA-256:
  `8b1d35b2be3f8d79ad84e571ba9c12d9b2725bd9a2a52f0062a44bc7d1436f77`.
  S6S Base Game Perks Redux 출력 SHA-256:
  `af542a6fafac138c526d3d665cd1b8e44c077f1349caa005ab59b46d22c6bd4b`.
  전체 ESP를 패키지에 배포하지 않고, 사용자 설치본으로부터 새 Output을 만들 때
  13개 대상 SCPT의 EDID/FormID/owner 및 SCTX/SCDA 전체 해시를 검증한다.

## 수정 범위와 바이너리 보존

- Vegas Elysium 결점 선택창 15개 리터럴, Educated 두 분기: 13개 SCPT / 17개 리터럴.
  Danger Close와 같은 경로의 다른 결점 창도 번역한다.
- Enemy Rank Renaming 두 파일 211개 활성 LNSetName 명령과 잡동사니 8개: 219곳.
  주석 처리된 Regulator 행은 실행 코드로 바꾸지 않는다.
- DSLC 레벨업 능력치 창 4개 문자열. 제목/버튼 외 모든 바이트를 보존한다.
- 컴파일된 문자열을 기존 UTF-8 바이트 예산 안에서 번역하고, 남는 길이는 본문의 끝
  (버튼 `|` 앞) 또는 설명 끝에 ASCII 공백으로 채운다. 문구는 이 제약 안에서 간결하게
  번역했으며, 수치·페널티·보상·설정값은 보존한다.
- SCDA 길이, 문자열 uint16 길이, 명령 길이, 분기/점프와 중첩 람다 바이트는 그대로다.
  `%r`가 컴파일 시 LF로 바뀌는 실제 형태를 반영하며 `%%`, `%.0f`, 버튼 순서를 보존한다.
- SCTX도 같은 문구로 바꾸고, 원본/번역 SCDA와 SCTX 전체 해시를 함께 고정한다.
  역변환 시 원본 복구, 전체 플러그인 readback 및 재실행 시 바이트 동일성을 검증한다.
  해시/소유자/스크립트가 다르면 결과 생성을 중단한다.
- 별도 tNVSE 사전·새 게임 ESP·이벤트 처리기는 추가하지 않는다. 기존 ESP 출력본에서
  검증된 문자열만 바꾸며 사용자 설치 경로/프로필/원본을 수정하지 않는다.

## 남는 검증

자동 검증은 게임 내 UTF-8 렌더링과 같지 않다. MessageBoxExAlt, JIP의 LNSetName,
SetFormDescription의 한글 표시, 길이 보존용 후행 공백의 실제 줄바꿈, 결점 수락/거부,
Educated 설정값 1/2/5에 따른 출력, 기존 세이브의 NPC 이름 갱신은 게임 실행 확인이 필요하다.
기존 세이브에서 이미 이름이 저장된 NPC는 재생성 전까지 이전 이름을 유지할 수 있다.
해결 확인 없이 #13을 닫거나 정식 배포하지 않는다.
