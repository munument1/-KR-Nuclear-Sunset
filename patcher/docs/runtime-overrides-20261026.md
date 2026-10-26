# Runtime English override audit

The installed Nuclear Sunset profile was scanned offline for display setters in
SCPT/SCTX and enabled loose NVSE scripts. No computer-use automation was used.
The first pass returned 190 candidates. These include nested lookup arguments,
not just English display strings.

Reviewed corrections cover 17 compiled script identities (33 installed/saved
copies used to establish accepted hashes) and 15 loose script paths containing
49 display-operand edits. Punga and fast-travel corrections are in a separate
runtime-text finalizer. The complete reviewed plans are in
nskr_runtime_override_data.py and nskr_runtime_text.py.

Excluded candidates include EditorIDToFormID arguments, INI section/key names,
AuxVar identifiers, Generic NPC Namer event IDs, CharacterBuildPresets cache
names, Securitrons On Alert record lookups and Mk-label normalization, and
localized value lookups in Enhanced Movement, Titans, Wordle and wGames.
These strings are program identifiers or source selectors and must stay intact.
This audit establishes coverage of the scanned direct setters; indirect strings
and DLL-owned text can still require further reports.

The long key-required sentence in the screenshot is an engine literal, not a
script setter. The game executable is unchanged. An exact-prefix tNVSE handler
uses the reviewed dictionary entry and normalizes the appended key name.
The shorter companion lock/terminal errors are separate compiled script fixes.

Every compiled edit retains operand budgets, opcodes and branches. Whole-script
SCTX/SCDA hashes gate accepted inputs, including finalized variants. Unknown
variants produce override_review_notes. Loose edits target only the immediate
name-setting operand, preserving nested record lookup strings and search terms.
All reviewed plans are checked for bytecode invariance and idempotence.

Patcher regression suite: 166 tests, 164 passed, two unavailable pinned English
installation fixtures skipped. Native Win32 tests: 140 passed. The DLL exports
and runtime import set match the baseline. Actual same-save rendering remains
pending and issue #18 must remain open until the reporter confirms the result.

The packaged full-output run produced 408 files. Reapplying the latest complete
finalizer pipeline changed zero bytes and produced zero review notes in the new
override/composition/dynamic scopes. Nine preexisting notification literal-match
notes remain in the report across four files; these are not considered verified
translations by this release.
