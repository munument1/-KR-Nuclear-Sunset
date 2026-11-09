# Issue #35: inventory notification encoding

v1.1.2 normalizes `sAddItemtoInventory`, `sRemoveItemfromInventory`,
`sEquipItemOnPlayer` and `sUnequipItemOnPlayer` to CP949. AMMO and other
inventory FULL names remain UTF-8. The reported screenshot has a damaged
`.357` item name followed by readable `제거됨`.

The actual installed `FalloutNV.esm` provides UTF-8 names for
`Ammo357Magnum`, `Ammo357MagnumHollowPoint` and `Ammo357MagnumJFPHandLoad`.
Combining one of these names with the CP949 notification fragment fails
the renderer's whole-string UTF-8 check. v1.1.2's assertion that all inserted
item names were already CP949 was incorrect; only MGEF/ALCH/SPEL/BOOK names
were normalized by that pass.

The native converter now recognizes the four exact Korean inventory
fragments. It converts only an otherwise strictly valid UTF-8 item portion,
then rejoins it with the original CP949 fragment. Counts remain part of the
item portion. Fully CP949 strings and unrelated mixed strings are preserved;
unrepresentable text fails without lossy replacement. The UTF-8 option,
Korean code page and available glyph requirements still apply.

No FULL records, scripts, GMST values, translations, save data or INI flags
are changed. This keeps existing consumers of UTF-8 item names intact.

Validation on 2026-11-09:

- Actual Win32 conversion code: 178 checks passed, including acquisition,
  removal, equip/unequip, counts, CP949 names, unsupported characters,
  nonmatching fragments and disabled conversion modes.
- All 4,612 installed runtime dictionary translations remain representable.
- Patcher suite: 191 tests, four skipped, no failures.
- DLL rebuilt from the official v1.1.2 native source with only encoding.cpp
  and encoding.h replaced. Win32 PE32 and both NVSE exports verified;
  runtime import DLL names match the official v1.1.2 DLL.

Local CMake compiler detection crashed (exit 0xC0000409). The local build
used the existing VS2022 project configuration and matching dependency
libraries in a detached directory, with CMake regeneration disabled.
The accompanying workflow performs a fresh source/dependency build.

**Gameplay display has not been verified. This is a QA candidate, not a
published release, and #35 remains open.**
