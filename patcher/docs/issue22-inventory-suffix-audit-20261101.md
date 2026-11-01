# Issue #22: inventory notification composition audit

The v1.0.8 full Output retained UTF-8 DATA strings in the following four
GMSTs of `NSKR UI Strings.esp`, while its item FULL names and the
`TTWGlowingMushroom` runtime name use CP949:

| GMST | Korean text |
| --- | --- |
| sAddItemtoInventory | 추가됨 |
| sRemoveItemfromInventory | 제거됨 |
| sEquipItemOnPlayer | 장착되었습니다. : (trailing space retained) |
| sUnequipItemOnPlayer | 장착해제 되었습니다. : (trailing space retained) |

The same omission exists in the current source's explicit composition allowlist.
Extend only that allowlist to normalize these four strings during normal Output
generation. Preserve their wording and all non-target fields. This addresses a
concrete mixed-encoding input to inventory notifications; it is a candidate
for the acquisition screenshot, not proof of the entire issue's root cause.

## Verification

- Actual full-Output UI plugin before SHA-256:
  `268bc28ef7a1509d123eabacb594a376d881595eacadce9a0189d10874c9fce3`.
- Patched in-memory SHA-256:
  `474a1e5e6d4bfeb5a9cc019d9723ef861252d2abfd54fac47913cba9b3dc57bd`.
- Exactly four GMST/DATA changes, no review notes, second pass byte-identical.
- Existing record restoration checks verify all other subrecord payloads remain
  unchanged; a regression test preserves an unrelated GMST verbatim and checks
  composition with the CP949 `발광 버섯` name.
- Full Python suite: 190 tests, 4 skipped, no failures (2026-11-01).
- The active local profile's winning `gr_p20MICingestiblenames.txt` already passes
  the exact runtime-name rules without changes or warnings. This confirms that
  file's translation, not every possible in-game fungus display path.

## Remaining

No live mod files were changed and no new release was published. The unrelated
attribute/skill notifications in the first screenshot still need their precise
runtime producer identified. The old Output's nine notification review notes
are in other scripts and do not by themselves identify that producer. Issue #22
and the remaining paths in #29 must stay open pending game verification.
