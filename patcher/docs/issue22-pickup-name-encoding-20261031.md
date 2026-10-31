# Issue #22 — pickup item FULL encoding candidate (source-only)

## Why this change exists

Issue #22 reports broken top-left notifications, including one observed while
picking up an object. The v1.0.8 notification finalizer normalizes FULL strings
from ALCH/SPEL/BOOK/MGEF to CP949 to support composition with CP949 UI
fragments, but omitted three player-visible pickup item types: MISC, AMMO and
KEYM. A UTF-8 item name appended to a CP949 message can be mis-decoded.

This change **does not prove** the reported notification used one of these
record types, or that its originating HUD code uses CP949. The screenshot,
actual winning MO2 provider, output bytes and runtime call path have not yet
been conclusively linked.

## Minimal change

- Extend the **existing** notification FULL-name conversion to MISC, AMMO,
  KEYM; only strictly valid UTF-8 Korean text that losslessly roundtrips to
  CP949 may change.
- Preserve identifiers (EDID), binary data, other subrecords, script operands
  and non-target record types. Existing CP949 and English inputs are unchanged.
- Unsupported Unicode remains untouched and is reported in
  `notification_review_notes` with a reason.
- Fixture tests cover uncompressed/compressed plugins, preservation, repeated
  application and unmappable Unicode.

## Boundaries

No executable binary, tNVSE DLL, release TranslationData or user's installed
files are changed by this branch. No release is authorized by these tests.
The #20 missing translations and the exact `탄피` vs `탄피.` mapping still
require the v1.0.8 release catalog / generated Output / actual record identity.
Do not bulk-remove punctuation, mutate arbitrary notification strings or close
#20/#22 on the basis of this source-only candidate.

## Review checklist

1. Run `python -m unittest discover -s patcher/tests -p 'test_issue22_pickup_names.py'`
   in the repo's supported Python environment (imports require `patcher/` in
   the module path, like the existing tests).
2. Verify the generated v1.0.8+candidate Output does not alter unrelated record
   or script fields and there are no new notification review failures.
3. Compare screenshot's exact message, file owner, record type, FormID and
   MO2 winning provider; capture an A/B screenshot with the identical save.
4. Only if confirmed, integrate into the next numbered patcher release and
   update both GitHub and Nexus. Otherwise leave #22 open.
