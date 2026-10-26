# Issue #18: challenge choices and chem-expiration composition

Status: included in v1.0.8. Same-save game validation remains pending.
The measurements below describe the initial isolated investigation.

## Evidence

- [Issue #18](https://github.com/munument1/-KR-Nuclear-Sunset/issues/18) reports garbled dialogue and healing-item expiration notifications after v1.0.7.
- The same reporter's [issue #17 screenshot](https://github.com/munument1/-KR-Nuclear-Sunset/issues/17) shows ordinary Jeremiah McDugal choices rendering correctly while Speech/Guns challenge choices are garbled.
- The v1.0.7 staged Output identifies the failed Speech choice as `Long15Reloaded.esm`, INFO local FormID `00C2FF`, RNAM `이봐. 감옥도 그렇게 나쁘진 않아.`. The success variant is `00C2FE`. Both reference AVSpeech through KNAM `000004BB`.
- RNAM is UTF-8. AVSpeech/FULL (`화술`) is CP949 after the existing perk display pass. The concatenation is invalid UTF-8 and does not decode to the intended Korean as CP949.
- `NSKR UI Strings.esp` supplies GMST `sChemsWornOff`, DATA `%s 효과가 사라졌습니다.` as UTF-8. The existing notification pass converts ALCH/SPEL names to CP949. Formatting that name into this template produces the same encoding mismatch.
- These are byte-level composition defects consistent with the reports. They do not prove the reporter's exact runtime path or establish that all healing notifications use this template.

## Change

`nskr_composed_display.py` runs after the existing notification finalizer:

- INFO/RNAM only when a non-null KNAM identifies an actor value or perk challenge.
- DIAL/FULL only for topics containing a challenge INFO. Topic identity includes the owning master and local FormID, so overrides in another plugin can identify the shared fallback without conflating equal numeric IDs from different owners.
- GMST/DATA only for `sChemsWornOff`.

All other fields retain their bytes, including INFO/NAM1 NPC responses, CTDA, KNAM, embedded SCDA/SCTX, and unrelated topic text. This pass does not rewrite bytecode. Unsupported CP949 characters remain unchanged and produce `composition_review_notes`. Converted fields record source/destination encoding and FormID under `composition_display`; the text report includes warnings and game-validation status.

## Validation

The saved v1.0.7 staged Output was scanned and a separate candidate overlay generated:

- 263 plugins scanned; 1,612 master-qualified challenge topics discovered.
- 82 changed plugins: 4,222 DIAL/FULL fields, 3,449 INFO/RNAM fields, one GMST/DATA field.
- Zero unsupported-character review notes.
- Independent readback compares all record metadata and subrecords, preserving opaque unrelated record payloads byte for byte. Only the three approved field types differ, by the exact encoding conversion.
- Reapplying the conversion produces identical bytes. Source files remain unchanged.

The initial full-suite run reproduced two baseline environmental failures: the installed NS.esp and Sweet Consumables.esp differ from the historical pinned English fixtures. The optional installed-fixture test now explicitly skips unavailable English fixtures; expected hashes and production acceptance gates are unchanged.

The initial candidate was derived from saved v1.0.7 Output. Release validation additionally rebuilds both executables and generates a complete Output using the packaged program. MO2 profiles remain read-only.

## Game checks still required

1. Jeremiah's Speech and Guns success/failure choices, ordinary choices, and NPC subtitles.
2. Stimpak/healing-item expiration notifications and item/effect names.
3. Existing perk requirements/descriptions and skill notifications.
4. A normal full patcher generation using the updated source and the user's exact current installation.

Do not close #18 or advertise runtime resolution from these byte-level checks alone.
