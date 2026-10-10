# Nuclear Sunset inherited base/DLC translation — native smoke test (2026-10-10)

The user's Nuclear Sunset MO2 profile was inspected **read-only**. These four plugins do **not** have direct SST dictionary files in the local direct-SST catalog. Instead, candidate translations were inherited from FalloutNV / Fallout 3 / DLC / TTW base-master translation mappings.

## Method

1. Build unambiguous base/DLC memory from the local SST catalog (**163,558** owner/FormID/field/source keyed items; **101,842** contain a nonempty hierarchical field path).
2. Scan each active target plugin's original records and select only candidates with the same originating master, local FormID, record signature, field name, and **exact original English text**.
3. Apply in the isolated XEditLib native worker. The worker only changes inherited fields when the **full hierarchical field path** also matches. It saves an isolated output plugin and reopens it for structural readback.
4. Do not modify installed originals, do not copy original ESM/ESP files to GitHub, and do not set `translation_ready`.

| Plugin | Exact path candidates | Applied and fresh-reloaded text fields | Changed records validated | Native status |
|---|---:|---:|---:|---|
| `NS.esm` | 723 | **723** | 651 | PASS |
| `NS.esp` | 1,439 | **1,439** | 1,291 | PASS |
| `BraveNewWorld.esm` | 3,247 | **3,226** | 2,879 | PASS |
| `TTW Dialogue and Interactions Expansion Overhaul.esp` | 192 | **192** | 171 | PASS |
| **Total** | **5,601** | **5,580** | **4,992** | **4/4 PASS** |

One initial `NS.esp` attempt did not run because the temporary folder name collided with `NS.esm`. The runner was corrected to retain the extension in the staging folder name, and **all four plugins passed on a clean v2 rerun**. The earlier collision was an audit-harness error, not a translation/readback failure.

Scripts: `patcher/tools/validate_fallback_smoke.py`. Local evidence remains at `patcher/.local/native-fallback-smoke-20261010-v2/summary.json` and isolated apply/verify JSON files.

## Limits and next work

- The findings validate **inherited text fields only**. Mod-specific text not found in the official dictionary remains in English. Notably Nuclear Sunset-specific records in `NS.esm`, `NS.esp` and `NSNPCs.esp` need dedicated Korean translation review.
- These **four** smoke-tested modules are not equivalent to all 48 identified fallback candidate plugins. The other plugins are not native-verified here.
- The MCM JSON, Translations INI, UI string, radio/subtitle coverage and in-game display have not been validated by this fallback test.
- A complete end-to-end packager/MO2 profile activation test, provenance and redistribution checks are still required before release.

**The release gate remains `translation_ready=false`.**
