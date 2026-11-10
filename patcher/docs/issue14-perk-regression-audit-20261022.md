# Nuclear Sunset issue #14 — PERK regression audit (2026-10-22)

Issue: https://github.com/munument1/-KR-Nuclear-Sunset/issues/14

## Evidence and limits

The issue body links 42 distinct 3440 × 1440 screenshots and reports that some perks displayed properly in v1.0.2 but not v1.0.5. All 42 original PNG assets were subsequently downloaded in GitHub Actions run 39775199812 and inspected; each selected name was matched to the v1.0.5 PERK/FULL catalog. See [the complete 42-capture findings](issue14-42-capture-findings-20261022.md). 41/42 requirement strings and 39/42 descriptions show damaged Korean; this suggests a common detail-display string path.

The v1.0.5 tag points at commit d1593dc5. The comparison from v1.0.2 totals 15 commits. Important changed source files: nskr_xedit_worker.py (previous Korean destinations), nskr_nvse.py (Tag! and Bullet Time), nskr_compiled_scpt.py (Head Hunter and Fast Metabolism), and nskr_output.py (output integration and reporting).

The experimental nskr_perk_dictionary.py tNVSE dictionary overlay was removed from the final v1.0.5 source. It is not a shipping v1.0.5 component. An old manually installed experimental output is still a possibility to check in MO2.

## Read-only catalog and report comparison

Download the v1.0.2 and v1.0.5 TranslationData archives from GitHub Releases and extract them to different temporary directories. Generate v1.0.5 Output with its JSON report.

From the patcher directory, run this command (use your own paths):

    python tools/audit_issue14_perk_regression.py --previous "C:\audit\v1.0.2\TranslationData\catalog.json" --current "C:\audit\v1.0.5\TranslationData\catalog.json" --report "C:\audit\Output.report.json" --output "C:\audit\issue14-perk-comparison.csv"

The script never reads or writes game files, mods, savegames, or MO2 configuration. It creates a new CSV exclusively rather than replacing an existing file.

Rows are keyed by physical plugin/provider, master owner, lower FormID, field, exact path and occurrence. It detects added/removed mappings, changed source English, changed Korean destination, changed previous-translation history, and duplicate identities. It correlates PERK-specific unmatched_entries and documented English exceptions from the output report.

**A plugin-wide translated or already_translated count does not prove that a particular PERK was patched.** The status plugin_processed_field_unverified is not a PERK-level success. Catalog comparison does not prove anything about game rendering.

## Triage sequence

1. Read each of the 42 images individually and write down perk name, displayed text, and the specific defect: ASCII question marks, missing font glyphs, mixed Korean/English, full English, or incorrect mechanic.
2. Match each perk to the actual loaded plugin owner and FormID, not merely its translated display name.
3. Join that identity to the CSV. Start with mapping_unmatched, source_changed, removed_mapping, skipped and translation_changed.
4. Compare current translation data with the generated ESP (static data), then with what the game actually displays (runtime).
5. On a cloned MO2 profile, hold the tNVSE DLL, INI, fonts and JIP DLL constant; isolate the Bullet Time description script, and verify active NVSE providers plus stale test overlays.
6. Check start, save, load and subsequent visits for late runtime overwrites. Preserve game effects while testing translations.

## Known prior cases (issue #11)

- Head Hunter: NS.esp compiled script SCPTPatchForJBT rewrites the description.
- Tag!: two providers of gr_TagPerkDescriptionSetter.txt overwrite the description.
- Fast Metabolism: Sweet Consumables.esp startup script appends new text.
- Concentrated Fire: PERK/DESC at lower FormID 044CAF is intentionally English in v1.0.5 because Korean previously appeared as question marks after runtime processing; FULL remains translated.

These four are source-proven older examples; #14 now has a separate image-by-image classification. The broad requirement corruption cannot be explained by those four description writers alone.

## Gates before any release

- Each PERK match must preserve reviewed owner/FormID/path/occurrence identity.
- Unknown previous Korean strings and changed English sources must not be silently overwritten.
- Compiled SCPT output must pass byte/size/record verification and actual game checks.
- Runtime descriptions must retain correct effects and readable Korean across startup/load.
- Do not treat a successful unit test, CSV match, or plugin aggregate count as in-game proof.
