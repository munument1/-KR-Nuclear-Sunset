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
