# Nuclear Sunset xEditLib native translation verification — 2026-10-10

Scope: isolated local staging from the installed Nuclear Sunset MO2 profile. This is **not an in-game test** and not a public release. The sources in `C:\Modlists\NuclearSunset` were not changed.

| Target | Candidate SST mappings | xEditLib-applied fields | Modified records structurally verified | Saved output fresh readback |
|---|---:|---:|---:|---|
| AutumnLeaves.esp (Uncreative Edition) | 4,296 | 4,266 | 1,783 | PASS |
| ZionTrail.esm (Revised) | 2,162 | 2,033 | 1,316 | PASS |
| ThePitt.esm (FO3 KR.esm-derived) | 3,200 | 3,200 | 2,283 | PASS |
| **Total** | **9,658** | **9,499** | **5,382** | **3/3 PASS** |

The XEditLib engine creates translated plugin copies in an isolated Game/Data tree, then loads saved results afresh. It checks master names, header hash, record index and changed record structure. All three passed.

Importantly, `unmatched` in raw worker reports counts encountered text fields within candidate records which did not find an eligible exact mapping. It is **not** the difference between candidate SST entries and applied fields, and cannot be interpreted as number of untranslated candidate entries.

Local test artifacts:
- `patcher/.local/native-validation-20261010-v2/summary.json`
- `patcher/.local/native-validation-thepitt-20261010/result_summary.json`
- The user-provided KR ESP/ESM, SST binaries, catalog mappings and translated test plugins remain only under `patcher/.local/` and must not be pushed as program assets.

Current development sources: `patcher/tools/verify_nexus_sst_native.py` and `patcher/tools/verify_thepitt_native.py`. The tests temporarily reuse the user's locally installed VNV XEditLib executable and native backend, purely under ignored `patcher/.tools`. The production installer still needs its own built worker.

Open validation work before release:
1. Review translation conflicts and pathless/richer field cases for direct and inherited mappings.
2. Native apply/readback for the remaining relevant 35 direct-SST plugins and 48 fallback-only candidates.
3. MCM JSON / translation INI mapping plus actual in-game UI checks.
4. Check packaging permissions and correct attribution. Do not include original third-party game/mod ESM/ESP.
5. Full program integration and actual MO2 profile output verification.

The catalog remains `translation_ready=false`, not releasable.
