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

## 2026-11-02: active-profile audit and attribute fragments

`tools/audit_notification_composition.py` now resolves offline plugin winners
for the selected profile. In the actual active configuration, all AVIF/FULL
names are CP949, but the winning `NSKR UI Strings.esp` still supplies UTF-8
`sYour`, `sAttributeDamaged`, and `sAttributeDrained`, in addition to the four
inventory suffixes above. The existing `sChemsWornOff` and skill increase/decrease
strings already use CP949. Normalize only these three additional composition
fragments; do not convert unrelated GMSTs or all INI values wholesale.

- Current installed UI plugin input SHA is the same `268bc28e...` above.
- Seven-field candidate SHA-256:
  `8bf809d8e61a5872ebf6191f8bd5f8c644c24811f342c7a2a84f9eb350aff85b`.
- Full Python suite: **191 tests, 4 skipped, no failures**.
- A separate MO2 QA profile with local saves and a separate overriding mod
  reached the main menu with the seven-field candidate. Automated mouse/key
  input did not trigger save loading, so the acquisition/attribute notifications
  were **not visually tested**. The test game was closed.
- The source save and source UI plugin remained byte-identical. After testing,
  the QA mod/profile were archived outside the live MO2 installation, the original
  selected profile was restored, and MO2's temporary disabled-QA modlist entry was
  removed. The restored modlist matches the pre-test copied baseline byte-for-byte.
  No new release was published.

The first screenshot's exact notification producer and the remaining #29 fungus
screens still require runtime evidence. These changes remove verified mixed
composition inputs, but do not establish that every symptom is resolved.
