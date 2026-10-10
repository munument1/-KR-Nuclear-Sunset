# F: Drive localization dictionary audit (2026-10-10)

## Confirmed xTranslator SST sources
Directory: `F:\번역\프로그램\xTranslator\UserDictionaries\FalloutNV`

- 103 direct `*_en_ko.sst` files.
- 35 SST filenames match a plugin in the current Nuclear Sunset profile or the core master set.
- 7 readable SSU9 sources for Fallout 3/TTW core masters: Fallout3, Anchorage, BrokenSteel, PointLookout, Zeta, TaleOfTwoWastelands, YUPTTW.
- 101,158 translated-source candidate entries summed across these 7 SSTs, **not actual applied translations**. Entries may overlap across master override chains.
- **ThePitt** has no standalone `thepitt_en_ko.sst` in the top-level FalloutNV dictionary directory or its checked subfolders. Its strings might be covered by TTW SST overrides, but this has not been established.

## MCM findings
- `F:\번역\프로그램\SimpleMcmJsonTranslator\db` has 149 `.mcmdb` entries, primarily Fallout 4 and **not directly usable** as New Vegas MCM.
- The prior VNV `patcher/data/mcm_direct_mappings.json` is present: 3 files / 45 mapping rows. None of these 3 virtual MCM paths were present in the current Nuclear Sunset MO2 provider inventory.
- Active Nuclear Sunset loose providers include 24 `MCM/*.json` and 13 relevant `MCM/Translations/*.ini` or `config/*Translations.ini` paths, so this requires its own text mapping work.
- VNV SST-derived matching plugin filename results cannot be called applied translations before XEditLib verification.

## Audit command (read-only)
Run `py -3 tools/audit_local_dictionaries.py` from the `patcher/` folder. Result is written under ignored `.local/f-drive-audit.json`.

## Distribution constraints
These are local user translation sources. No original ESP/ESM/BSA or unverified third-party bundled resources have been committed to the GitHub branch. Do not set `translation_ready=true` or release until TTW plugin readback, translation accuracy, master order, and permission checks are complete.

## Confirmed alternate source: FO3 KR.esm (The Pitt)

User-provided/local translated plugin: `D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm`.

Compared read-only against the currently installed Nuclear Sunset TTW source:
`C:\Modlists\NuclearSunset\mods\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)\ThePitt.esm`.

- `FO3 KR.esm` includes `ThePitt.esm` in its TES4 master list.
- The original ThePitt.esm has 32,394 self-owned records (including records not necessarily containing translatable text).
- `FO3 KR.esm` has **3,344 ThePitt-owned overrides**, all 3,344 matched the original by FormID local ID and record signature.
- In the conservative binary field sample (`FULL`, `DESC`, `NAM1`), 2,993 text subfield pairs were comparable; 2,787 differed and contained Hangul. Repeated field tags were matched by tag and occurrence index.
- This confirms usable Korean The Pitt translation **exists in FO3 KR.esm**, even though a standalone `thepitt_en_ko.sst` is missing.
- It does **not** yet confirm complete dialogue/quest coverage, nor compatibility of every translation with the current TTW version. Do not copy/ship the source plugin; extract translation pairs from matching fields into the independent SST catalog only after native verification.

Reproduce: `py -3 tools/audit_fo3_kr_pitt.py --report .local/pitt-from-fo3-kr-audit.json`. The report stays local and is not committed.

## Confirmed: The Pitt translation in local FO3 KR.esm (2026-10-10)

Local source: D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\ttw\FO3 KR.esm

- FO3 KR.esm lists ThePitt.esm among its 12 masters.
- It includes 3,344 The Pitt-owned records (master index 08), including 1,585 INFO records.
- Every one of these 3,344 FormIDs and record signatures matches the installed Nuclear Sunset ThePitt.esm.
- 2,304 of these records contain UTF-8-decodable Korean syllables (record-level presence, NOT validated translation count).
- Therefore The Pitt translation entries can be reconstructed into a dedicated SST after field-level and source-text validation.
- Do not redistribute the full FO3 KR.esm or original game ESM files. Candidate text mappings remain local pending audit.

Verification: py -3 tools/verify_thepitt_in_fo3kr.py
