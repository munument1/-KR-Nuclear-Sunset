"""Strict structural tests for the one-field GMST sOr candidate."""
import struct
import unittest

from tools.build_issue14_sor_candidate import (
    TARGET_ID, OLD_BYTES, RESTORED_BYTES, PROMPT_EDITOR, PROMPT_BYTES,
    _iter_records, _key_prompt, _sor, repair,
)

U16 = struct.Struct("<H")
U32 = struct.Struct("<I")


def field(name, value):
    return name + U16.pack(len(value)) + value


def record(sig, fid, body):
    return struct.pack("<4sIIIIHH", sig, len(body), 0, fid, 0, 15, 0) + body


def group(body):
    return b"GRUP" + U32.pack(len(body) + 24) + b"GMST" + bytes(12) + body


def plugin(sor=OLD_BYTES, prefix=PROMPT_BYTES, additional=False):
    head = record(b"TES4", 0, field(b"HEDR", struct.pack("<fII", 1.34, 4, 0x800)))
    data = record(b"GMST", TARGET_ID, field(b"EDID", b"sOr\0")
                  + field(b"DATA", sor))
    key = record(b"GMST", 0x000ABE4A, field(b"EDID", PROMPT_EDITOR)
                 + field(b"DATA", prefix))
    filler = record(b"GMST", 0x01000810, field(b"EDID", b"sNewGame\0")
                    + field(b"DATA", "새 게임\0".encode()))
    extra = record(b"GMST", TARGET_ID, field(b"EDID", b"sOr\0")
                   + field(b"DATA", sor)) if additional else b""
    return head + group(data + key + filler + extra)


class Issue14SorCandidateTests(unittest.TestCase):
    def test_exact_repair_preserves_every_other_record_and_key_prompt(self):
        original = plugin()
        reference = plugin(RESTORED_BYTES, b"\0")
        converted = repair(original, reference)
        self.assertEqual(_sor(converted), RESTORED_BYTES)
        self.assertEqual(_key_prompt(converted), PROMPT_BYTES)
        old, new = _iter_records(original), _iter_records(converted)
        self.assertEqual(len(old), 4)
        self.assertEqual(len(old), len(new))
        self.assertEqual(old[0], new[0])
        self.assertNotEqual(old[1], new[1])
        self.assertEqual(old[2:], new[2:])
        self.assertEqual(len(converted), len(original) + 2)
        self.assertEqual(U32.unpack_from(converted, len(old[0]) + 4)[0],
                         U32.unpack_from(original, len(old[0]) + 4)[0] + 2)

    def test_rejects_unexpected_current_original_or_key_prompt(self):
        reference = plugin(RESTORED_BYTES, b"\0")
        with self.assertRaisesRegex(ValueError, "CP949 sOr"):
            repair(plugin(RESTORED_BYTES), reference)
        with self.assertRaisesRegex(ValueError, "Reference v1.0.2 sOr"):
            repair(plugin(), plugin())
        with self.assertRaisesRegex(ValueError, "key-prompt bytes"):
            repair(plugin(prefix=b"other\0"), reference)
        with self.assertRaisesRegex(ValueError, "Reference release key-prompt"):
            repair(plugin(), plugin(RESTORED_BYTES, PROMPT_BYTES))

    def test_detects_duplicate_or_identity_changes(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            repair(plugin(additional=True), plugin(RESTORED_BYTES, b"\0"))
        changed_id = bytearray(plugin())
        needle = U32.pack(TARGET_ID)
        idx = changed_id.find(needle)
        self.assertGreater(idx, 0)
        changed_id[idx:idx+4] = U32.pack(TARGET_ID + 1)
        with self.assertRaisesRegex(ValueError, "sOr FormID"):
            repair(bytes(changed_id), plugin(RESTORED_BYTES, b"\0"))

    def test_corrupted_group_size_rejected(self):
        broken = bytearray(plugin())
        head_size = len(_iter_records(plugin())[0])
        U32.pack_into(broken, head_size + 4, 10)
        with self.assertRaisesRegex(ValueError, "Invalid"):
            repair(bytes(broken), plugin(RESTORED_BYTES, b"\0"))


if __name__ == "__main__":
    unittest.main()
