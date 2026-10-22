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


## Additional confirmed constraint: only the perk selection screen (2026-10-22)

The reporter clarified that the corruption happens **only inside the perk-selection screen**. Other menus render Korean normally. Update the working hypothesis accordingly: do **not** assume general ESP corruption, a global FreeType font bug, or systemic loss of UTF-8 in every game UI.

### Relevant upstream implementation

- Fallout: New Vegas UI contributor Axonis explained that `Menus/levelup_menu.xml` / `LUM_SelectionText` receives **one engine-composed text string containing requirements, ranks and description**. Source: https://www.moddb.com/mods/vanilla-ui-plus/forum/thread/ui-bug-question
- Upstream tNVSE `tnvse/Src/dictionary/dictionary_perk.cpp` has a dedicated `TryTranslatePerkDescription` parser that splits `Req:`, `Ranks:`, `Source:` and the body. The related `dictionary_translate.cpp` route is conditional on dictionary configuration. Source: https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/dictionary/dictionary_perk.cpp and https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/dictionary/dictionary_translate.cpp
- The **published** v1.0.2 and v1.0.5 bundles both contain the **same** tNVSE INI flags: `uiEncoding=4`, `bUTF8=1`, `bEnableDictionaryTranslation=0`, `bEnableDictionaryPerkDescriptionTranslation=0`, and `bEnableDictionaryMixedSourceTranslation=0`. Therefore the upstream *dictionary PERK translation parser is disabled by default* in the shipped Korean package. It must not be blamed without evidence that a different active MO2 `tnvse.ini` overrides this.
- Source evidence and released flags: https://github.com/munument1/-KR-Nuclear-Sunset/actions/runs/39779348457

### Updated priority order

1. **P0**: Verify the *active MO2 providers* of `Menus/levelup_menu.xml`, `NVSE/plugins/tnvse.ini`, `tnvse.dll` and `tnvse_fonts.xml`. The read-only provider snapshot now explicitly watches the level-up XML. Note that a packed BSA fallback may not show up as a loose provider.
2. **P0**: On a **cloned** MO2 profile, display the same game-state PERK selection with the winning custom `levelup_menu.xml` versus a known-good UI provider, changing only that provider. Keep fonts, DLLs, plugins, save and game mechanics unchanged. Do not randomly toggle the entire localization stack.
3. **P1**: If both XML variants fail, compare the engine-composed `LUM_SelectionText` value before tNVSE's multibyte conversion to the string it actually renders. Identify whether `?` were already substituted in the input string or appear only after conversion.
4. **P1**: Check active `tnvse.ini`; if dictionary translation is *actually* enabled by an overriding mod, additionally disable only the perk-description dictionary route for one controlled A/B (cloned profile). Do **not** assume this applies to released defaults.
5. **P2**: Only for #7, #11, #28, #31 and #37, independently inspect dynamic text-appending scripts. These cannot explain 41/42 corrupted requirement strings on their own.

The older recommendation to establish whether Pip-Boy also corrupts was superseded by the report that the issue is **selection-window-specific**. A normally rendered Pip-Boy can still serve as the fixed control; there is no need to request the same fact again.

Do not merge/publish on static evidence alone; a real running game comparison is still absent.


### Targeted upstream tNVSE font/render pipeline source review (2026-10-22)

Upstream **tNVSE** sources identify a specific, testable encoding boundary:

1. `tnvse/Src/font/font_manager.cpp`: `FontManagerEx::PrepText` calls `TryPrepareRichTextInput` / `TryConvertRichTextInput`; `HasRichTextExtraGlyphs` checks whether **any** extra glyphs are available, not strictly the current XML text tile's font ID. The tile's font ID is useful rendering context but not, by itself, proof of why multibyte conversion did/didn't run.
2. `tnvse/Src/font/encoding.h`: `ConvertToMultiByte` runs only if `bUTF8`, East Asian UI mode and extra glyphs are enabled **and** `IsValidUTF8With3ByteMin(source)` is true for the **entire** supplied C-string. Otherwise the input is passed through without UTF-8-to-CP949 conversion.
3. `tnvse/Src/font/encoding.cpp`: `IsValidUTF8With3ByteMin` rejects invalid UTF-8 byte sequences. A level-up UI buffer constructed from a mix of UTF-8 PERK/DESC and legacy-encoded requirement/label pieces may fail that whole-string check, but this remains only a **hypothesis** until the actual pre-render byte sequence is dumped.
4. `tnvse/Src/game/game_hooks.cpp`: the general font preparation and rich-text parsing hooks include no obvious `LevelUpMenu` / `LUM_SelectionText`-specific call site. The first loss could occur in the game's own concatenation, a conflicting UI plugin, or another hook before tNVSE.
5. `Menus/levelup_menu.xml` differs between actual published UI mods: sample MUX has `LUM_SelectionText/font = 3`, a DarN UI example has `font = 1`. **These are reference examples, not evidence of the reporter's active XML.**

References: [tNVSE encoding.h](https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/font/encoding.h),
[tNVSE font_manager.cpp](https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/font/font_manager.cpp),
[tNVSE encoding.cpp](https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/font/encoding.cpp),
[tNVSE game_hooks.cpp](https://github.com/TIAIMM/tNVSE/blob/main/tnvse/Src/game/game_hooks.cpp).

The MO2 selected-profile inspector now includes the winning and overridden `Menus/levelup_menu.xml` providers' `LUM_SelectionText` literal font slot / expression, tile ID and fragment digest. It **does not** patch XML, force font substitution, touch VFS state or prove any game-time failure.

**Test priorities after offline profile snapshot:** compare unchanged game state on cloned UI XML providers, then identify the raw pre-render selection text bytes (before C-string conversion). Specifically distinguish (a) actual ASCII 0x3F substitution before font handling, (b) mixed UTF-8/CP949 input rejected by the whole-buffer validator, and (c) intact CP949 output that the chosen font slot cannot render. Seeing literal question marks alone does not distinguish these paths.

## Root-cause implications

The translated list labels render normally while the same menu's details/requirements are damaged. This strongly prioritizes the **level-up UI's detail string construction, encoding boundary and renderer path** over rewriting 42 individual PERK translation mappings. `PERK/DESC` translation mappings do not independently explain dynamically composed requirements.

Compare static ESP record bytes, runtime GetFormDescription results, and the level-up UI rendering independently. Compare identical perks in Pip-Boy versus level-up screen using one cloned MO2 profile. Check actual loaded tNVSE.dll/INI and JIP versions, and the active provider for each override. A screenshot alone does not locate the first irreversible character loss. Do not modify the user's original modlist or release until the A/B test identifies the responsible path.

No change to translation strings or game files is proposed by this report.


## Safe read-only MO2 provider evidence when an actual game PC is connected

The attached screenshots alone do **not** reveal the physical winners for the current selected MO2 profile. The new helper \`tools/audit_issue14_mo2_winners.py\` reads the selected profile's ModOrganizer.ini, modlist.txt, plugins.txt and loose provider files without changing them.

From the \`patcher\` directory:

\`\`\`powershell
python tools/audit_issue14_mo2_winners.py --mo2-root "C:\Modlists\NuclearSunset" --output "C:\NSKR-Issue14-Diagnostics\mo2-provider-snapshot.json"
\`\`\`

The output destination must be outside the MO2 and game directory. Save separately from the already-patched Output report. It records SHA-256 and low-to-high provider order for the exact DLL, INI, font XML, dictionary XML, two NVSE description scripts, and relevant plugin files. It also flags possible prior experimental "Korean Perk Runtime" / "NSKR Test" providers for manual inspection.

**Important:** This is an *offline VFS precedence inference*, not proof of which DLL a running process loaded or which plugin record won across the full load order. No game execution, Pip-Boy/level-up comparison, or xNVSE instrumentation has run. Do not mark issue #14 fixed on this evidence alone.

### In-game A/B matrix for the cloned test profile

| Check | Keep fixed | Change | Required evidence |
|---|---|---|---|
| A (baseline) | DLL, font XML, INI, save, plugin order | No changes | Same selected perk in level-up screen and Pip-Boy; note UI context |
| B (Script Runner) | Same as A | Disable only Bullet Time perk *description script* provider in cloned MO2 profile | Note change in each string, and verify game effects are unchanged |
| C (static translations) | Same as A | Verify generated ESP's original Korean PERK/DESC bytes read-only | Exact owner/FormID/field readback |
| D (DLL/renderer) | Same as A | Only after A-C, switch one controlled tNVSE/JIP configuration at a time | Identify first step that changes damaged to readable Korean |

Suggested representative screenshots are #1 (base-game perk), #3 (modded perk), #7 (all-English description), #31 (mixed Korean-English but readable), and #40 (Concentrated Fire English exception with damaged requirements).
