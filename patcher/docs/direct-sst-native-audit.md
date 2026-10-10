# Nuclear Sunset direct SST native verification (2026-10-10)

An isolated native XEditLib apply + fresh reload test was run against the installed Nuclear Sunset MO2 profile. All game plugin originals remained unchanged.

- Direct SST catalog targets: **38**
- Actually tested: **38** (pass: 38; pass without matched text: 0; failed: 0)
- Untested: **0**
- Candidate text mappings for tested targets: **225,311**
- Native applied and reloaded text fields: **212,850**
- Structurally verified changed records: **152,313**

The mapping count is a **candidate** count; 'applied' means text was actually written to a staging copy, reloaded and structurally verified. Neither measure is in-game string-coverage percentage. Observed unmatched fields refer to worker-field inspection and cannot be subtracted from the candidate count.

| Active plugin | Candidate fields | Native applied fields | Verified changed records | Status |
|---|---:|---:|---:|---|
| 3DNPCFNVBundle.esm | 3,739 | 3,554 | 2,658 | PASS |
| A World of Pain Revised.esm | 464 | 462 | 385 | PASS |
| Anchorage.esm | 1,996 | 1,989 | 1,492 | PASS |
| AutumnLeaves.esp | 4,296 | 4,266 | 1,783 | PASS |
| Bad Touch.esm | 3 | 3 | 3 | PASS |
| Better Brotherhood.esm | 122 | 122 | 83 | PASS |
| BrokenSteel.esm | 3,860 | 3,701 | 2,508 | PASS |
| CaravanPack.esm | 4 | 4 | 3 | PASS |
| ClassicPack.esm | 7 | 7 | 6 | PASS |
| DeadMoney.esm | 6,284 | 6,284 | 4,483 | PASS |
| DLC Enhancements.esp | 340 | 336 | 225 | PASS |
| DMT _Dead Money Tweaks_.esp | 549 | 549 | 397 | PASS |
| DMT TTW Patch.esp | 42 | 42 | 42 | PASS |
| DryWellsReloaded.esm | 2,025 | 1,946 | 1,005 | PASS |
| Enhanced Movement.esp | 18 | 18 | 18 | PASS |
| Fallout3.esm | 47,190 | 36,722 | 24,949 | PASS |
| FalloutNV.esm | 67,207 | 67,112 | 53,499 | PASS |
| Functional Post Game Ending.esm | 1,462 | 1,462 | 1,125 | PASS |
| Goodies.esp | 1,172 | 935 | 595 | PASS |
| GunRunnersArsenal.esm | 341 | 341 | 253 | PASS |
| HonestHearts.esm | 3,429 | 3,426 | 2,687 | PASS |
| JustAssortedMods.esp | 26 | 26 | 24 | PASS |
| LonesomeRoad.esm | 3,202 | 3,190 | 2,299 | PASS |
| Long15Reloaded.esm | 17,026 | 16,233 | 8,173 | PASS |
| MercenaryPack.esm | 3 | 3 | 2 | PASS |
| NewVegasBounties.esm | 1,077 | 1,024 | 709 | PASS |
| NewVegasKiller.esm | 554 | 549 | 272 | PASS |
| OldWorldBlues.esm | 4,848 | 4,830 | 3,475 | PASS |
| Placement Fixes.esm | 67 | 67 | 67 | PASS |
| PointLookout.esm | 3,269 | 3,256 | 2,412 | PASS |
| TaleOfTwoWastelands.esm | 30,077 | 29,930 | 22,389 | PASS |
| The Mod Configuration Menu.esp | 25 | 25 | 13 | PASS |
| ThePitt.esm | 3,200 | 3,200 | 2,283 | PASS |
| TLD_Travelers.esm | 470 | 464 | 438 | PASS |
| TribalPack.esm | 3 | 3 | 2 | PASS |
| YUPTTW.esm | 12,606 | 12,603 | 8,600 | PASS |
| Zeta.esm | 2,146 | 2,133 | 1,640 | PASS |
| ZionTrail.esm | 2,162 | 2,033 | 1,316 | PASS |

## Untested

None of the direct-SST plugins remains untested.

## Still required before release

- Validate per-record path/source ambiguity and official-base-master inheritance on the 48 identified fallback candidates; resolve candidates with no direct SST separately.
- Inventory and translate active MCM JSON, translations INI, UI strings and any radio/subtitle data not stored in plugin record fields.
- Test the end-to-end packaged installer and MO2 profile output, then test actual game rendering in the target TNVSE runtime.
- Confirm attribution and license restrictions on third-party translated data. No upstream game/mod plugins or original text assets are committed.
- Keep translation_ready=false until those gates are satisfied.
