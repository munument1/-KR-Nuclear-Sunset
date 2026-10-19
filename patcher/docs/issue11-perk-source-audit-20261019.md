# Nuclear Sunset issue #11 — PERK 원문·실행 시 덮어쓰기 감사 (2026-10-19)

## 결론

이슈 #11의 네 화면은 단순한 PERK/DESC 번역 누락만으로 설명되지 않는다. 원래 영문 PERK를 번역한 뒤 **게임 실행 중 다른 스크립트가 설명을 다시 덮어쓴다**. 다음 중 세 개는 수정되지 않은 영문을 주입하는 코드를 설치된 파일에서 직접 확인했다.

1. **Headhunter**: NS.esp 안의 SCPTPatchForJBT가 더 상세한 *Bullet Time 전용* 영문 설명을 주입한다. 누락되기 쉬운 효과는 2단계에서 **엎드린 자세 재장전 속도 +25%**.
2. **Tag!**: NVSE 텍스트 스크립트 두 공급자에서 같은 SetFormDescription 영문을 주입한다. **기술 +15 즉시 상승**이라는 원본 PERK 문구와 **기술 증가 속도 2배**라는 실제 화면의 기계적 효과가 다르다.
3. **Fast Metabolism**: Sweet Consumables.esp의 SCPT sssSCPTIngestiblesStartup이 원래 한국어 설명 뒤에 **술 섭취 시 방사능 감소 속도 2배** 영문을 이어 붙인다.
4. **Concentrated Fire**: S6S Base Game Perks Redux.esp 안의 한국어 DESC는 이미 정상이다. 별도의 Bullet Time NVSE 스크립트가 GetFormDescription → Sv_RegexReplace → SetFormDescription으로 여러 게임 설명을 다시 기록한다. 스크린샷의 물음표·자모 훼손이 이 처리 단계에서 발생했을 가능성이 높지만, 실시간 실행 추적은 하지 않았으므로 원인 확정에는 게임 재검증이 필요하다.

영문 원본과 실제 출력 번역을 읽기 전용으로 확인했다. **원본 모드·게임·번역 카탈로그·패처 소스는 바꾸지 않았다.** 이 보고서와 조사용 NVSE 원본 스크립트의 별도 복사본만 추가했다.

## 감사 대상과 신뢰도

| 항목 | 감사한 정확한 위치 / 정보 |
|---|---|
| 이슈 원본 | https://github.com/munument1/-KR-Nuclear-Sunset/issues/11 |
| 네 스크린샷 | patcher/.local/issue11_1.png ~ issue11_4.png; 순서대로 Headhunter, Concentrated Fire, Tag!, Fast Metabolism |
| 활성 카탈로그 | patcher/.local/key-prompt/TranslationData/catalog.json, 약 121.7 MiB, 2026-10-15 수정. schema_version=1, target_modlist=nuclear-sunset-ttw, channel=development |
| 원본 데이터 | C:\Modlists\NuclearSunset\mods 아래 실제 설치된 모드의 ESP/ESM, NVSE 텍스트 스크립트. 번역 카탈로그의 baseline_sha256과 원본 ESP/ESM 해시가 일치한다 |
| 번역 결과 파일 | C:\Modlists\NuclearSunset\mods\NSKR Test - 1cxljp5s 에 있는 번역된 FalloutNV.esm, S6S Base Game Perks Redux.esp, S6S Perks.esp, NS.esp 및 Sweet Consumables.esp |
| 검증 방법 | 네 이미지 육안 확인; Python JSON 행/키 직접 읽기; tools/tes4_text_scan.py의 읽기 전용 TES4 record/subrecord 스캐너로 실제 PERK·SCPT의 EDID/FULL/DESC/SCTX/SCDA 분리; 원본과 번역본 비교 |
| 적용 범위 한계 | 로컬 원본/출력 바이트와 스크린샷은 확인. 게임 프로세스의 실시간 모드 우선순위와 스크립트 실행 시각은 직접 관찰하지 않음 |

## 1. 스크린샷과 PERK의 정확한 연결

| 이미지 | 표시된 이름 | 대상 플러그인과 PERK 본래 소유자 | FormID 하위 24비트 | 카탈로그 DESC 상태 / 런타임 차이 |
|---|---|---|---|---|
| 1 | 헤드헌터 (Headhunter) | S6S Perks.esp / s6s perks.esp | 00bd3a | 카탈로그 원문과 한국어 DESC가 실제 설치 원본에 정확하게 일치. 하지만 NS.esp에서 동적으로 더 긴 영문 설명으로 덮어씀 |
| 2 | 집중 사격 (Concentrated Fire) | FalloutNV.esm / falloutnv.esm; 마지막 관련 정적 override는 S6S Base Game Perks Redux.esp | 044caf | 해당 S6S override의 새 원문과 한국어 DESC 모두 정상이며 자동 무기 탄 퍼짐 -20%를 포함. 스크린샷은 요구 조건과 설명이 글자 단위로 훼손 |
| 3 | 태그! (Tag!) | FalloutNV.esm / falloutnv.esm | 031dbd | 카탈로그는 15점 즉시 상승 설명. 런타임 스크립트는 기술 성장 속도 2배로 설명을 변경 |
| 4 | 재빠른 신진대사 (Fast Metabolism) | FalloutNV.esm / falloutnv.esm; S6S Base Game Perks Redux.esp도 같은 PERK DESC 계승 | 094ebf | 카탈로그는 스팀팩 체력 회복 +20%. 런타임 Sweet Consumables 스크립트가 술/방사능 설명을 추가 |

확인한 활성 카탈로그의 원본 SHA-256:

| 파일 경로 | baseline_sha256 |
|---|---|
| FalloutNV.esm | afcf8fc4d3317f31ba559c11de46e3b5e3d4d4c8002bdd9454ba92cc0db72bc1 |
| S6S Base Game Perks Redux.esp | 7dbd817a844ac83b38a1fc562385de76ff7064775bb85c99019576134037d882 |
| S6S Perks.esp | 03b400d7e31d028c70f2870c68fa9c6bd7f5bb27bae123ddc12ca7f86283ce2a |
| NS.esp | 29c237bc18133751fb9de138cd05644e64f7bb9d80502cd69ceeb9f923d461ea |
| Sweet Consumables.esp | fbb771d36b5cc4c37e269a67caf48202afaf3654e9a87aaeaba3cebf74063fa1 |

### 정적 PERK 설명과 실제 번역본 검증

- S6S Perks.esp, owner=s6s perks.esp, id=00bd3a, signature=PERK, field=DESC, path=DESC, field_occurrence=0: 원문은 "You take your time ... +25% ... V.A.T.S. ... 50% ... second rank ... 15%."로 끝난다. catalog.dest: "시간을 들여 조준하면 총알이 정확히 적의 눈 사이에 박힙니다. V.A.T.S.에서 머리 명중률이 25% 증가하지만, AP 소모량이 50% 증가합니다. 2단계에서는 V.A.T.S.에서 머리 공격 시 치명타 피해량이 15% 증가합니다." 실제 NSKR Test/S6S Perks.esp 바이너리도 **이 한국어 그대로**이다.
- S6S Base Game Perks Redux.esp, owner=falloutnv.esm, id=044caf, signature=PERK, field=DESC, path=DESC, field_occurrence=0: "With Concentrated Fire, your accuracy when targeting any body part in V.A.T.S. increases slightly with each subsequent attack on that body part, and your spread is decreased by 20% when using an automatic weapon." → "집중 사격(Concentrated Fire)을 사용하면 V.A.T.S.에서 신체 부위를 조준할 때마다 해당 부위에 대한 명중률이 약간씩 증가하며, 자동 무기 사용 시 탄 퍼짐이 20% 감소합니다." 실제 NSKR Test의 해당 override DESC도 이 한국어다.
- FalloutNV.esm, owner=falloutnv.esm, id=031dbd, PERK/DESC: 기본 원문 "The Tag! perk allows you to select a fourth Skill to be a Tag skill, which instantly raises it by 15 points." → catalog.dest는 "태그! 퍽이 있으면 네 번째 주력 스킬을 선택할 수 있으며, 선택된 스킬이 15 증가할 것입니다." 실제 NSKR Test/FalloutNV.esm에도 정적 번역 적용이 확인된다.
- FalloutNV.esm, owner=falloutnv.esm, id=094ebf, PERK/DESC: "With the Fast Metabolism perk, you gain a 20% Health bonus when using Stimpaks." → "재빠른 신진대사 퍽이 있으면, 스팀팩의 체력 회복량이 20% 증가합니다." 실제 NSKR Test/FalloutNV.esm와 NSKR Test/S6S Base Game Perks Redux.esp에도 정적 번역이 적용되어 있다.
- 위 PERK 레코드에 텍스트 EPF2 subrecord는 발견되지 않았다. Headhunter와 Concentrated Fire의 일부 perk entry는 PRKE/EPFT/EPFD 바이너리 하위 레코드를 가지며 그 안의 수치 데이터를 번역 대상으로 오인해 수정하면 안 된다. catalog.json 전체에서도 EPF2라는 field/path 매핑을 발견하지 못했다.

## 2. Headhunter: NS.esp의 동적 스크립트가 정적 설명을 덮어씀

- 파일: C:\Modlists\NuclearSunset\mods\[#] [INF] - Nuclear Sunset Master Patches\NS.esp
- SCPT FormID 0x91082F79, owner=s6s perks.esp (마스터 배열 index 0x91), 하위 ID=082f79, EDID=SCPTPatchForJBT.
- SCTX와 SCDA에 같은 영문 리터럴이 한 번씩 있다. 번역된 NSKR Test/NS.esp에도 같은 영어가 남아 있다.
- 확인한 SCTX 문장 (원문 스크립트 이스케이프된 %%, 실행 출력에서는 %):

~~~text
SetFormDescription sssPerkHeadhunter "You take your time to ensure that your bullets will land right between your target's eyes. You gain +25%% chance to hit your target's head in Bullet Time, at cost of 50%% increased AP cost. The second rank increases your reload speed while prone by 25%%, and your crit. damage while attacking your target's head in Bullet Time by 15%%."
~~~

스크린샷 1도 V.A.T.S. 대신 Bullet Time, 재장전 속도 25%를 포함하므로 이 동적 설명과 일치한다. 기존 S6S Perks.esp 정적 DESC만 번역해도 이 화면은 고쳐지지 않는다.

정확한 한국어 런타임 문안(%% 보존):

~~~text
SetFormDescription sssPerkHeadhunter "적의 두 눈 사이에 총알을 명중시키기 위해 신중하게 조준합니다. 불릿 타임에서 적의 머리를 명중시킬 확률이 25%% 증가하는 대신 AP 소모량이 50%% 증가합니다. 2단계에서는 엎드린 자세에서 재장전 속도가 25%% 증가하고, 불릿 타임에서 적의 머리를 공격할 때 치명타 피해량이 15%% 증가합니다."
~~~

**적용 제약:** NS.esp의 SCTX는 사람이 읽는 소스지만 실행되는 내용은 이미 컴파일된 SCDA다. SCTX만 교체하면 게임에서 영어가 계속 나올 수 있다. 컴파일 가능한 GECK/xEdit+적정 스크립트 도구에서 SCDA까지 정합적으로 갱신해야 하며, 별도 NVSE 런타임 교정 스크립트가 뒤에 실행되도록 설계하는 경우에도 실제 순서를 확인해야 한다.

## 3. Concentrated Fire: 정상적인 정적 한국어 위에 런타임 재기록

- 실제 설치 S6S Base Game Perks Redux.esp의 owner=falloutnv.esm / id=044caf / PERK DESC는 활성 카탈로그의 변경 원문과 완전히 같다. 공격할 때마다 명중률 조금씩 상승, 자동 무기 탄 퍼짐 **20% 감소**라는 두 효과를 모두 보존한 번역이 이미 NSKR Test 출력에 존재한다.
- 별도 런타임 스크립트 C:\Modlists\NuclearSunset\mods\Bullet Time - Perk Consistency Patch\nvse\plugins\Scripts\gr_BulletTimePerkDesc.txt는 GLTA 86, GLTA 98에서 받은 여러 폼 각각에 다음 작업을 한다:

~~~text
svDescription = Sv_RegexReplace (GetFormDescription rRef) "Bullet Time|VATS|V\.A\.T\.S\.(?!\s[A-Z])|V\.A\.T\.S"
SetFormDescription rRef "%z" svDescription
~~~

두 번째 루프도 유사한 식으로 rR을 대상으로 실행하고, AVPerception 설명도 가공한다. 이미 UTF-8 한글로 번역된 설명을 다시 스크립트의 문자열 처리 함수에서 해석/저장하면서 글자가 훼손될 수 있다. 스크린샷 2는 한글 부분이 "?..."로 반복되고 "(Concentrated Fire)", "Bullet Time", "20%" 등 ASCII가 남는다. 이는 해당 처리 경로와 부합하지만 아직 **스크립트 단독 재현 및 실제 함수 인코딩 검증은 미완료**다.

수정 방향: 이 런타임 스크립트의 원문 문자열을 먼저 보존해 두고, 한국어 설명을 다시 읽고 쓰지 않게 하거나 한글 지원이 검증된 처리 경로를 사용한다. 임의로 PERK/DESC 한글 문구를 바꾸는 것만으로는 스크립트에 의한 훼손이 해결되지 않는다. 조건문에 한글 탐지를 추가할 경우에도 실제 스크립트 API의 유니코드/CP 호환성을 확인해야 한다.

## 4. Tag!: NVSE 스크립트의 현재 효과 설명

동일 이름과 동일 내용, SHA-256 동일(674285048997d75262fccc6bf0f5b51c1e1e0b563e0e032a1714d221629f838a), 150바이트 ASCII/no BOM/no newline:

- C:\Modlists\NuclearSunset\mods\Tag Perk Description Adjustment\nvse\plugins\scripts\gr_TagPerkDescriptionSetter.txt
- C:\Modlists\NuclearSunset\mods\SSS - Sweets Simple Settings\nvse\plugins\scripts\gr_TagPerkDescriptionSetter.txt

~~~text
SetFormDescription Tag "The Tag! perk allows you to select a fourth skill to be a tag skill, which will double the rate at which that skill advances."
~~~

스크린샷 3이 이 문장과 일치한다. **현재 효과 기준** 권장 번역:

~~~text
SetFormDescription Tag "태그! 퍽을 선택하면 네 번째 주력 기술을 지정할 수 있으며, 해당 기술의 숙련도 상승 속도가 두 배가 됩니다."
~~~

현재 카탈로그에 있는 "15 증가" 설명은 기본 PERK의 정적 기록이므로 **별개 버전**으로 유지한다. 런타임 오버라이드에 이를 그대로 재사용하면 게임 동작과 맞지 않는 설명이 된다. 두 스크립트는 동일 가상 경로이므로 실제 MO2 제공자 우선순위를 확인하고 하나의 최종 출력만 사용해야 한다.

## 5. Fast Metabolism: Sweet Consumables.esp의 컴파일된 문장 추가

- 파일: C:\Modlists\NuclearSunset\mods\[FL] [OP] - Sweet Consumables\Sweet Consumables.esp
- SCPT owner=Sweet Consumables.esp, FormID=0x12001870 (하위 id=001870), EDID=sssSCPTIngestiblesStartup.
- SCTX 원문과 SCDA 컴파일 코드 양쪽에 아래 조건부 쓰기 동작이 있다.

~~~text
if AlcoholRadHealing == 1
    sMetabolismDesc = GetFormDescription FastMetabolism
    SetFormDescription FastMetabolism "%z Alcohol will also reduce your radiation twice as quickly." sMetabolismDesc
    sv_destruct sMetabolismDesc
endif
~~~

AlcoholRadHealing은 해당 스크립트에서 Consumable Settings:bAlcoholRadRemoval / Sweet Consumables Config.ini 값을 읽어 설정한다. 이미 한국어인 스팀팩 효과 설명을 받아 영어 문장을 뒤에 붙이므로 스크린샷 4의 혼합 출력과 정확히 대응한다. 원본 및 NSKR Test 번역본의 SCPT에 같은 영문 리터럴이 남아 있다.

권장 추가 문장: "술을 마시면 방사능 수치도 두 배 빠르게 감소합니다." 기존 한국어 설명의 **스팀팩 체력 회복량 +20%**는 그대로 보존한다. 스크립트 출처 기준 수정 후보:

~~~text
SetFormDescription FastMetabolism "%z 술을 마시면 방사능 수치도 두 배 빠르게 감소합니다." sMetabolismDesc
~~~

**바이너리 편집 제약:** 문자열 "%z Alcohol will also reduce your radiation twice as quickly."는 SCDA payload 내부에 ASCII로 정확히 한 번 있으며 시작 직전 2바이트 little-endian 값은 60(원문 60바이트)이다. SCTX에도 한 번 있다. 한국어 UTF-8 문자열은 바이트 길이가 달라지므로, 단순 byte replace 또는 SCTX만 변경하는 작업은 안전하지 않다. 컴파일러와 구조적 사후 검증 없이는 실제 .esp에 패치하지 않는다.

## 6. 작업자가 복사해 사용할 수 있는 최소 매핑 후보

아래 JSON은 **적용할 대상을 설명하는 제안**이다. 기존 catalog.json의 schema에 SCPT/런타임 스크립트가 지원된다는 의미가 아니며, SCTX/SCDA 수정 항목은 스크립트 컴파일 또는 확실한 런타임 교정 경로가 확인되어야 적용 가능하다.

~~~json
[
  {
    "plugin": "NS.esp",
    "owner": "s6s perks.esp",
    "id": "082f79",
    "signature": "SCPT",
    "field": "SCTX+SCDA",
    "path": "SCPTPatchForJBT/SetFormDescription sssPerkHeadhunter",
    "source_en": "You take your time to ensure that your bullets will land right between your target's eyes. You gain +25%% chance to hit your target's head in Bullet Time, at cost of 50%% increased AP cost. The second rank increases your reload speed while prone by 25%%, and your crit. damage while attacking your target's head in Bullet Time by 15%%.",
    "dest_ko": "적의 두 눈 사이에 총알을 명중시키기 위해 신중하게 조준합니다. 불릿 타임에서 적의 머리를 명중시킬 확률이 25%% 증가하는 대신 AP 소모량이 50%% 증가합니다. 2단계에서는 엎드린 자세에서 재장전 속도가 25%% 증가하고, 불릿 타임에서 적의 머리를 공격할 때 치명타 피해량이 15%% 증가합니다.",
    "verified_from": "installed NS.esp SCPT SCTX and SCDA; screenshot 1 matches",
    "apply": "script compiler + SCDA validation required"
  },
  {
    "plugin": "Tag Perk Description Adjustment / SSS - Sweets Simple Settings",
    "owner": "falloutnv.esm",
    "id": "031dbd",
    "signature": "NVSE-script",
    "field": "SetFormDescription",
    "path": "nvse/plugins/scripts/gr_TagPerkDescriptionSetter.txt",
    "source_en": "The Tag! perk allows you to select a fourth skill to be a tag skill, which will double the rate at which that skill advances.",
    "dest_ko": "태그! 퍽을 선택하면 네 번째 주력 기술을 지정할 수 있으며, 해당 기술의 숙련도 상승 속도가 두 배가 됩니다.",
    "verified_from": "two identical installed ASCII script files; screenshot 3 matches",
    "apply": "replace exact quoted string in Output script copy after validating runtime UTF-8 Hangul support"
  },
  {
    "plugin": "Sweet Consumables.esp",
    "owner": "sweet consumables.esp",
    "id": "001870",
    "signature": "SCPT",
    "field": "SCTX+SCDA",
    "path": "sssSCPTIngestiblesStartup/SetFormDescription FastMetabolism",
    "source_en": "%z Alcohol will also reduce your radiation twice as quickly.",
    "dest_ko": "%z 술을 마시면 방사능 수치도 두 배 빠르게 감소합니다.",
    "verified_from": "installed ESP SCPT SCTX and SCDA; screenshot 4 matches",
    "apply": "script compiler + SCDA validation required; preserve %z"
  },
  {
    "plugin": "S6S Base Game Perks Redux.esp",
    "owner": "falloutnv.esm",
    "id": "044caf",
    "signature": "PERK",
    "field": "DESC",
    "path": "DESC",
    "source_en": "With Concentrated Fire, your accuracy when targeting any body part in V.A.T.S. increases slightly with each subsequent attack on that body part, and your spread is decreased by 20% when using an automatic weapon.",
    "dest_ko": "집중 사격(Concentrated Fire)을 사용하면 V.A.T.S.에서 신체 부위를 조준할 때마다 해당 부위에 대한 명중률이 약간씩 증가하며, 자동 무기 사용 시 탄 퍼짐이 20% 감소합니다.",
    "verified_from": "installed S6S override and translated NSKR Test binary (already correct)",
    "apply": "no catalog edit; verify Bullet Time script handling of already translated text"
  }
]
~~~

## 7. 자료 복사, 인코딩 및 후속 실증

읽기 전용으로 원본과 SHA를 대조해 바이트 단위 그대로 복제한 파일:

| 새 복사본 | 원본 / 바이트 특성 |
|---|---|
| patcher/.local/issue11-nvse-scripts/Tag-SSS.txt | SSS - Sweets Simple Settings의 gr_TagPerkDescriptionSetter.txt, 150B, ASCII/UTF-8 무 BOM, 개행 없음 |
| patcher/.local/issue11-nvse-scripts/Tag-Adjustment.txt | Tag Perk Description Adjustment의 같은 파일, 150B, 위와 바이너리 동일 |
| patcher/.local/issue11-nvse-scripts/Bullet-PerkDesc.txt | Bullet Time - Perk Consistency Patch의 gr_BulletTimePerkDesc.txt, 1200B, ASCII/UTF-8 무 BOM, CRLF 46개, 마지막 개행 없음 |

Bullet-PerkDesc SHA-256: d26401da3e60a84d4cfbc6ac1b9382fe5a48dd8c3d7dbab13924fcd3341390f5. 설치된 NVSE .txt 전체에서 확인한 한국어 포함 텍스트 파일은 NSKR 테스트용 폰트 README뿐이었다. **실제로 작동하는 한국어 SetFormDescription 텍스트 스크립트의 선례는 발견하지 못했으므로** 번역문을 UTF-8로 넣은 뒤 실제 게임에서 표시·인코딩을 시험해야 한다.

검증 우선순위는 (1) 출력에 포함된 Tag 런타임 스크립트가 한글을 출력하는지, (2) Bullet Time 스크립트만 끈 비교 프로필에서 Concentrated Fire의 정상 한국어가 유지되는지, (3) NS.esp와 Sweet Consumables.esp SCPT의 소스/컴파일 코드가 동시 갱신된 빌드에서 Headhunter의 25/50/25/15%와 Fast Metabolism의 20%/방사능 2배가 표시되는지다. 스크립트가 게임 메커니즘 자체를 조정하므로 모드를 삭제해 영구 해결하는 방식은 권장하지 않는다.

## 8. 추가 감사: 컴파일된 SCDA의 안전한 자동 수정 가능성 (2026-10-19)

**판정: 현재 패처 도구로 SCPT/SCTX/SCDA를 안전하게 재컴파일한다는 증거가 없어 ESP 수정 빌드는 보류했다.** 원본 게임, 설치 모드 및 기존 코드/카탈로그는 그대로 유지했다.

독립 감사 도구 `tools/audit_issue11_compiled_scripts.py`를 신규 작성했다. 이 도구는 설치 ESP를 오직 읽기만 하며, 파일 해시를 고정해 현재 버전이 맞는지 검증하고, 특정 FormID의 SCPT 레코드를 가져와 실제 MAST 소유자·EDID·SCHR·SCDA·SCTX 및 런타임 원문을 검사한다. XEditLib DLL의 PE 버전과 export도 조사한다. ESP 수정/저장/빌드 기능은 없다.

~~~powershell
cd D:\Codex_Trans\비바\nuclear-sunset\patcher
python tools/audit_issue11_compiled_scripts.py --json-output .local/issue11-scpt-audit-20261019-verified.json
~~~

실제 실행 성공. JSON 증거: `.local/issue11-scpt-audit-20261019-verified.json`.

| 검증 항목 | Headhunter | Fast Metabolism |
|---|---|---|
| 설치 원본 | NS.esp, SCPTPatchForJBT | Sweet Consumables.esp, sssSCPTIngestiblesStartup |
| FormID | 91082F79 | 12001870 |
| 원 소유자 | S6S Perks.esp (MAST index 145) | Sweet Consumables.esp |
| SCTX 크기 | 2,537 bytes | 7,058 bytes |
| SCDA 크기 | 1,384 bytes | 3,477 bytes |
| SCHR에 기록된 컴파일 크기 | 1,384 (일치) | 3,477 (일치) |
| 대상 영어 문자열 | 335 ASCII bytes (%% 포함) | 60 ASCII bytes (%z 포함) |
| 원문 출현 | SCTX 1회, SCDA 1회 | SCTX 1회, SCDA 1회 |
| SCDA 문자열 시작 직전 LE uint16 값 | 335 | 60 |
| 번역 바이트코드 재컴파일 | **미검증** | **미검증** |

직전 2바이트를 문자열 길이로 해석하면 원문 길이와 일치한다. 그러나 이는 **관측 결과**이고, 해당 문자열 외 바이트코드·점프 오프셋·SCHR·레코드 및 GRUP 길이까지 재계산하는 공인 패처를 검증했다는 의미가 아니다. 가변 길이 UTF-8 문장을 SCDA에 그대로 덮어쓰거나 SCTX만 바꾸는 처리는 하지 않았다.

### 로컬 컴파일러 조사

- **XEditLib**: `patcher/.local/key-prompt/Backend/XEditLib.dll`의 PE FileVersion은 `0.6.0.0`, ProductVersion은 `0.6`이다. `pefile`로 166개 이름 있는 export를 확인했으며 이름에 `compile`, `script`, `scda`, `sctx`가 포함된 함수는 **0개**다. 패처의 `nskr_xelib.py`는 `SetValue`/`SaveFile`을 노출하지만, SCTX 편집이 SCDA를 올바르게 재컴파일한다는 증거가 없다. 따라서 이 DLL을 스크립트 컴파일러로 사용하지 않았다.
- **GECK / NVSE**: `C:\Modlists\NuclearSunset\GECK.exe`가 존재하며 버전 `1.4.0.518`, `[NoDelete] Stock New Vegas\nvse_loader.exe`가 존재하며 버전 `0.6.4.8`이다. NVSE 확장 명령을 포함한 원본 스크립트가 GECK에서 실제로 재컴파일되는지에 대한 안전한 비대화형 테스트 환경은 확보하지 못했다. 실행파일의 존재는 동작 보증이 아니다.
- **런타임 CompileScript / RunScriptSnippet**: xNVSE 문서에 따르면 텍스트 파일을 런타임 UDF로 컴파일하거나 임시 스크립트를 실행하는 기능이다. 기존 ESP SCPT 레코드의 SCDA를 다시 빌드해 정상적으로 저장하는 API라는 근거는 없다.

외부 근거: [xNVSE 개발 가이드](https://github.com/xNVSE/NVSE/blob/master/DEVELOPMENT.md), [xNVSE CompileScript](https://geckwiki.com/index.php?title=CompileScript), [RunScriptSnippet](https://geckwiki.com/index.php?title=RunScriptSnippet), [NVSE GECK 컴파일 지침](https://mod.pub/falloutnv/41/docs/7-readme).

### 런타임 사본 오버레이도 순서 검증이 필요함

JIP LN Script Runner의 공식 이벤트는 `gr_` 게임 시작, `gl_` 게임 로드, `gn_` 새 게임, `ln_` 새 게임/로드다. 그러나 이 이벤트 설명만으로 두 원본 SCPT보다 나중에 실행된다고 보장할 수 없다.

- **Headhunter**: NS.esp의 `SCPTPatchForJBT`는 `begin function {}` 안에 있으며 `if ismodloaded "Enhanced Movement.esp"`가 참일 때 `SetFormDescription sssPerkHeadhunter`를 실행한다. 이 함수를 호출하는 위치와 시점은 이번 조사에서 입증하지 않았다. 별도 번역 스크립트가 먼저 실행되면 원문으로 돌아갈 수 있다.
- **Fast Metabolism**: Sweet Consumables.esp의 `sssSCPTIngestiblesStartup`은 `begin Gamemode` 안 `if GetGameRestarted` 분기에서 `AlcoholRadHealing == 1`일 때 현재 설명을 `GetFormDescription`으로 읽고 `%z`를 이용해 영어를 덧붙인다. 기존 분기보다 늦게 최종 번역문을 덮어쓰는지, 여러 번 추가되어 문장이 중복될 수 있는지는 실제 게임에서 확인해야 한다.
- 별도 스크립트는 ESP의 SCDA를 건드리지 않고도 `SetFormDescription`을 호출할 수 있다는 장점이 있지만, 한글 인코딩, 대상 폼 식별, JIP/JohnnyGuitar 의존성 및 실행 순서가 실제 게임에서 검증되기 전에는 출시 대상이 아니다.

공식 문서: [JIP Script Runner 이벤트](https://geckwiki.com/index.php?title=JIP_Script_Runner), [SetFormDescription](https://geckwiki.com/index.php?title=SetFormDescription).

### 안전한 후속 선택지

1. **컴파일 경로 검증**: 복제된 독립 게임/GECK 프로필에서 NVSE 지원 편집기로 두 SCPT만 수정해 정상 컴파일한 후, SCTX와 SCDA가 모두 교체됐는지, SCDA·SCHR 크기가 일치하는지 확인한다. 새 ESP의 나머지 모든 레코드를 기존 사본과 비교하고 실제 게임에서 기능·표시를 재검증한다. 다른 스크립트까지 수정하는 전역 `Recompile All Scripts` 작업은 피한다.
2. **출력용 런타임 스크립트**: `ln_` 등 별도 JIP 파일을 독립 시험 프로필에 배치하여 시작·새 게임·로드·재로드 시각, 설명 중복, 한글 인코딩과 NS.esp UDF 호출 순서를 실증한다. **원본 스크립트가 모두 실행된 뒤 한국어 설명이 유지됨을 확인**해야 배포할 수 있다.

현 상태에서는 어느 쪽도 최종 실게임 검증을 통과하지 않았으며, 증명되지 않은 SCDA 수정 빌드는 만들지 않았다. 별도 감사 도구와 결과 파일만 제공한다.
