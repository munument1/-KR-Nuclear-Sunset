# Nuclear Sunset — existing SST inheritance first, then new translation (2026-10-10)

## Scope and method

A total of **204 plugins** remain in the manual translation/review workspace after previously excluding 38 direct-SST plugins and separating 10 files that do not need ordinary new record-string translation. Original MO2 game/mod files are untouched.

Source workspace: `D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010`

Translation memory uses the unreleased Nuclear Sunset local SST catalog, matching **owner master + six-digit local FormID + record signature + subrecord name + exact English text**. Actual application requires the additional hierarchical field path and is tested using isolated XEditLib copies. Files containing source strings and the user's SST/ESP content stay local, not in GitHub.

### Native inheritance verification added

Four plugins had already passed native fallback tests: `NS.esm`, `NS.esp`, `BraveNewWorld.esm`, and `TTW Dialogue and Interactions Expansion Overhaul.esp`.

This iteration validated **14 additional plugins**, all passing native save and fresh readback:

| Plugin | Native-applied inherited fields |
|---|---:|
| EDGE TTW.esp | 934 |
| STAR TTW 2.esp | 903 |
| Vanilla SWEEP.esp | 744 |
| Dynamic World and TODD Patch.esp | 559 |
| Sweet Consumables.esp | 500 |
| TTW NPC Overhaul.esm | 410 |
| Vanilla Enhancements.esm | 403 |
| Goodies - TTW.esp | 405 |
| NSNPCs.esp | 385 |
| ATMOS Ambient Overhaul.esp | 350 |
| [RWM]-Complete Added.esp | 336 |
| New Blood.esp | 326 |
| NavmeshOverhaul.esm | 295 |
| Mojave Raiders.esp | 235 |
| **Additional total** | **6,785** |

### Review queue after exact comparison with 204 staged CSVs

| Queue | Field rows | Meaning |
|---|---:|---|
| 01_신규번역_필요 | **42,021** | No matching existing SST source: prioritize translation, context review necessary |
| 02_상속번역_검증대기 | **4,502** | Dictionary candidate exists but was not *unambiguously* verified from saved native changes; test first |
| 03_상속번역_적용검증완료 | **12,339** | Existing SST field matched native XEditLib saved/readback evidence and uniquely matched staged CSV |
| **Total** | **58,862** | All 204 remaining plugin source-field candidates |

**18 of 204 plugin sources** now have a native fallback apply/readback result (14 newly tested and four earlier). The 12,339 fields is the conservative *uniquely reconciled staged CSV count*, not the total number of changes logged in native tests; repeated subrecords are not overcredited. Unverified does not mean untranslated.

The new local subfolder is:
`10_번역분리_신규와_기존상속`

- `00_플러그인별_분류결과.csv`: per-plugin counts and native test status
- `00_분류현황.json`: machine-readable totals
- `01_신규번역_필요`: 204 per-plugin human translation queues
- `02_상속번역_검증대기`: 157 per-plugin unresolved inheritance lists
- `03_상속번역_적용검증완료`: 18 per-plugin reference lists of verified inheritance
- `00_읽어주세요.md`: review instructions

The original 204 plugin CSVs were **not modified**. Newly generated translation fields remain blank; the reference Korean candidate appears separately for inherited translations.

## Pending

- Verify remaining 4,502 inherited candidate rows. Highest-volume untested plugins include `Hymn of The New West.esp`, `FO3_Optimization.esm`, `S6S Base Game Perks Redux.esp`, `TTW Reputations.esm`, `TTW New Vegas Speech Checks.esm`, `Party Banter 2.esm`.
- Translate and review the 42,021 new-source candidate fields, protecting game placeholders, quest context, speaker names and record identity.
- Test MCM JSON, translation INI, scripts, dialogue conditions and actual game UI.
- Rebuild a post-review SST catalog and test end-to-end installer/MO2 output; keep `translation_ready=false` until all conditions are met.

Tools: `patcher/tools/validate_manual_fallback_batch.py`, `patcher/tools/partition_manual_translation_csv.py`, and `patcher/tools/update_partition_workspace_summary.py`.
