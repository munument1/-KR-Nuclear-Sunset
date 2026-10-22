# Nuclear Sunset #14 — 42 screenshot evidence classification (2026-10-22)

Original issue: https://github.com/munument1/-KR-Nuclear-Sunset/issues/14

Evidence collection: [GitHub Actions run 39775199812](https://github.com/munument1/-KR-Nuclear-Sunset/actions/runs/39775199812) successfully fetched **42/42 original images**. The analyst inspected all 42 panels visually (not OCR). Names were independently checked against the actual published v1.0.5 TranslationData `PERK/FULL` records.

## Quantified findings

- 42/42 selected PERK names match a current Korean `FULL` dictionary string exactly.
- 41/42 screenshots contain obvious `?` and damaged Korean in the **requirements** string; #31 is the exception.
- 39/42 screenshots have similarly damaged Korean **description** text. Of those, #11, #28 and #37 have an additional intact English suffix.
- #7 displays an entirely English description even though a Korean catalog DESC exists; #31 has readable Korean plus a separate English suffix; #40 has English intentionally maintained by the v1.0.5 Concentrated Fire workaround (but damaged requirements).
- A second real release-data comparison found **2151/2151 unchanged PERK mappings** between v1.0.2 and v1.0.5: 1,104 FULL, 1,047 DESC, with no source/dest/history changes.
- This is far broader than the four known runtime script cases from #11: requirements are affected even for #40, where the English-only DESC remains readable.

## Exact packaged runtime and font comparison

The CI's additional SHA-256 audit compared both **published** TranslationData archives, not only source control:

- `NVSE/plugins/tnvse.dll`: same SHA-256 (`fae479bd3d6f61b52d824e10cc6fe01abe96c31584f284a5e5969340d0844db4`).
- `tnvse.ini` payload: identical. `tnvse_fonts.xml` payload: identical.
- `plugin_fields` catalog policy: identical.
- `font_bundle` difference: the old bundled source ZIP `NVSE/plugins/fonts/licenses/tNVSE-71-KR-UI-source.zip` was removed in the later folder-based release. No runtime DLL/font config payload difference detected.
- `runtime_mods`: the sole differing payload is `Nuclear Sunset - Korean UI Strings/NSKR UI Strings.esp` (consistent with the previously documented key-prompt/GMST update). The other UI/runtime bundle payload hashes match.

This narrows the *package difference*, but does not prove what actually loaded in the reporter's MO2 virtual filesystem. In particular, an older or other-mod override can still win at runtime. No causal tie between the UI Strings ESP and this PERK bug has been established.

Evidence: [GitHub Actions comparison run](https://github.com/munument1/-KR-Nuclear-Sunset/actions/runs/39777641060).

## Screenshot list (PERK owner/FormID candidates)

**IMPORTANT:** These are owner/lower-FormID candidates from release TranslationData, **not confirmed winning plugin overrides in the user's game**. A common master may be overridden by multiple other ESPs. At #40 and #42, different PERK records can share the same translated display name.

| Screenshot | Visible name | Requirements | Description | Owner / lower FormID |
|---:|---|---|---|---|
| 01 | 저격수 | Garbled | Garbled Korean | FalloutNV.esm:031db4 |
| 02 | 헤드헌터 | Garbled | Garbled Korean | S6S Perks.esp:00bd3a |
| 03 | 육혈포 사무라이 | Garbled | Garbled Korean | Vegas Elysium.esp:019ed7 |
| 04 | 치명적인 반격 | Garbled | Garbled Korean | S6S Perks.esp:022424 |
| 05 | 총잡이 | Garbled | Garbled Korean | FalloutNV.esm:094ebb |
| 06 | 서부의 대치 | Garbled | Garbled Korean | S6S Perks.esp:005a99 |
| 07 | 신속한 주머니 | Garbled | English only | NS QuickSelect.esp:011dcf |
| 08 | 혹독한 훈련 | Garbled | Garbled Korean | FalloutNV.esm:044cb1 |
| 09 | 꼼짝 마! | Garbled | Garbled Korean | Vegas Elysium.esp:00082a |
| 10 | 강철 위장 | Garbled | Garbled Korean | FalloutNV.esm:044ca9 |
| 11 | 균형 잡힌 짐 | Garbled | Garbled Korean + English | S6S Perks.esp:0192fa |
| 12 | 밤손님 | Garbled | Garbled Korean | FalloutNV.esm:165118 |
| 13 | 이야하압! | Garbled | Garbled Korean | FalloutNV.esm:14609c |
| 14 | 크리터 크런처 | Garbled | Garbled Korean | S6S Perks.esp:01828c |
| 15 | (설명할 수 없는) 페미니스트 의제 | Garbled | Garbled Korean | Vegas Elysium.esp:000821 |
| 16 | 둔기 외상 | Garbled | Garbled Korean | S6S Perks.esp:015140 |
| 17 | 재로 돌아가라 | Garbled | Garbled Korean | S6S Perks.esp:015141 |
| 18 | 고중량 | Garbled | Garbled Korean | DeadMoney.esm:011468 |
| 19 | 내 눈 속의 세상 | Garbled | Garbled Korean | EDGE TTW.esm:038fc5 |
| 20 | 런 앤 건 | Garbled | Garbled Korean | FalloutNV.esm:14609d |
| 21 | 발키리 | Garbled | Garbled Korean | S6S Perks.esp:009c5c |
| 22 | 숨겨진 무기 | Garbled | Garbled Korean | S6S Perks.esp:00082b |
| 23 | 신속 장전 | Garbled | Garbled Korean | FalloutNV.esm:1377fd |
| 24 | 아톰 밤 베이비 | Garbled | Garbled Korean | S6S Perks.esp:00291d |
| 25 | 파티광 | Garbled | Garbled Korean | Sweet Consumables.esp:00394c |
| 26 | 권총 명사수 | Garbled | Garbled Korean | S6S Perks.esp:000806 |
| 27 | 강력한 한 방 | Garbled | Garbled Korean | FalloutNV.esm:14609e |
| 28 | 관통 일격 | Garbled | Garbled Korean + English | FalloutNV.esm:14609f |
| 29 | 멈출 수 없는 힘 | Garbled | Garbled Korean | FalloutNV.esm:165447 |
| 30 | 무법자 | Garbled | Garbled Korean | S6S Perks.esp:01f2d6 |
| 31 | 생명력 부여 | Readable | Readable Korean + English | FalloutNV.esm:031db1 |
| 32 | 수작업가 | Garbled | Garbled Korean | FalloutNV.esm:16581b |
| 33 | 응용 탄도학 | Garbled | Garbled Korean | S6S Perks.esp:022422 |
| 34 | 특공대 | Garbled | Garbled Korean | FalloutNV.esm:099828 |
| 35 | 헤비 거너 | Garbled | Garbled Korean | S6S Perks.esp:00082c |
| 36 | 방사능 흡수 | Garbled | Garbled Korean | FalloutNV.esm:0e2c4a |
| 37 | 수학 천재 | Garbled | Garbled Korean + English | FalloutNV.esm:135ec3 |
| 38 | 질량중심 | Garbled | Garbled Korean | FalloutNV.esm:165182 |
| 39 | 악명 높은 악당 | Garbled | Garbled Korean | S6S Perks.esp:005a9e |
| 40 | 집중 사격 | Garbled | English (intentional) | FalloutNV.esm:044caf |
| 41 | 닌자 | Garbled | Garbled Korean | FalloutNV.esm:031dcc |
| 42 | 도살자 | Garbled | Garbled Korean | FalloutNV.esm:165446 |

## Specific exceptions / next inspection

- **#7:** 영어 DESC만 출력. NS QuickSelect.esp 카탈로그에는 한국어 DESC 존재.
- **#11:** 깨진 한국어 뒤 영어: Your backpack AP regen penalty....
- **#28:** 깨진 한국어 뒤 영어: Bleeding effects that....
- **#31:** 요구 조건·한국어 DESC 정상, 뒤에 영어 추가: Medicine and Survival....
- **#37:** 깨진 한국어 뒤 영어: Charging your Pip-Vision....
- **#40:** v1.0.5 의도적 영어 PERK/DESC, 요구 조건 깨짐. Concentrated Fire.
- **#42:** FalloutNV.esm:165446 우선 후보; Vegas Elysium.esp:00df9f도 동명 FULL.

## Root-cause implications

The translated list labels render normally while the same menu's details/requirements are damaged. This strongly prioritizes the **level-up UI's detail string construction, encoding boundary and renderer path** over rewriting 42 individual PERK translation mappings. `PERK/DESC` translation mappings do not independently explain dynamically composed requirements.

Compare static ESP record bytes, runtime GetFormDescription results, and the level-up UI rendering independently. Compare identical perks in Pip-Boy versus level-up screen using one cloned MO2 profile. Check actual loaded tNVSE.dll/INI and JIP versions, and the active provider for each override. A screenshot alone does not locate the first irreversible character loss. Do not modify the user's original modlist or release until the A/B test identifies the responsible path.

No change to translation strings or game files is proposed by this report.
