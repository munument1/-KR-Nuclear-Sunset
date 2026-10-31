"""Regression tests for narrowly scoped item FULL normalization (#22)."""
import struct
import unittest
import zlib

import nskr_notifications as notifications
from nskr_compiled_scpt import _decode_record, _slots


def sub(tag, value):
    return tag + struct.pack('<H', len(value)) + value


def record(sig, name, *, compressed=False, tail=b'1234'):
    # These are synthetic plugin records, not evidence of an in-game fix.
    body = (sub(b'EDID', b'ExampleItem\0') +
            sub(b'FULL', name) +
            sub(b'MODL', tail))
    payload = struct.pack('<I', len(body)) + zlib.compress(body) if compressed else body
    return sig + struct.pack('<5I', len(payload), 0x40000 if compressed else 0,
                             0x00800000, 0, 0) + payload


def fields(raw):
    return {field: value for field, _, value in _slots(_decode_record(raw[:24], raw[24:]))}


class PickupNameTests(unittest.TestCase):
    def test_pickup_name_conversion_is_scoped_and_lossless(self):
        name = '낡은 탄피'.encode('utf-8') + b'\0'
        for sig in (b'MISC', b'AMMO', b'KEYM'):
            with self.subTest(signature=sig):
                before = record(sig, name)
                after, changes, issues = notifications.patch_bytes(before, 'NS.esp', [])
                self.assertFalse(issues)
                self.assertEqual(fields(after)[b'FULL'], '낡은 탄피'.encode('cp949') + b'\0')
                self.assertEqual(fields(after)[b'EDID'], b'ExampleItem\0')
                self.assertEqual(fields(after)[b'MODL'], b'1234')
                self.assertEqual(changes, [{'edid': 'ExampleItem',
                                            'kind': sig.decode() + '/FULL CP949'}])
                self.assertEqual(notifications.patch_bytes(after, 'NS.esp', []),
                                 (after, [], []))

    def test_other_record_types_and_english_names_unchanged(self):
        before = record(b'WEAP', '정상 이름'.encode('utf-8') + b'\0')
        self.assertEqual(notifications.patch_bytes(before, 'NS.esp', []),
                         (before, [], []))
        for sig in (b'MISC', b'AMMO', b'KEYM'):
            before = record(sig, b'Empty casing\0')
            self.assertEqual(notifications.patch_bytes(before, 'NS.esp', []),
                             (before, [], []))

    def test_compressed_pickup_record_preserves_unrelated_bytes(self):
        before = record(b'MISC', '녹슨 열쇠'.encode('utf-8') + b'\0',
                        compressed=True, tail=b'\x00\xff\x80')
        after, changes, issues = notifications.patch_bytes(before, 'NS.esp', [])
        self.assertFalse(issues)
        self.assertEqual(len(changes), 1)
        self.assertEqual(fields(after)[b'MODL'], b'\x00\xff\x80')
        self.assertEqual(fields(after)[b'FULL'], '녹슨 열쇠'.encode('cp949') + b'\0')
        self.assertEqual(notifications.patch_bytes(after, 'NS.esp', []),
                         (after, [], []))

    def test_unsupported_glyph_is_reported_without_question_mark_loss(self):
        before = record(b'MISC', '빛나는 🚀'.encode('utf-8') + b'\0')
        after, changes, issues = notifications.patch_bytes(before, 'NS.esp', [])
        self.assertEqual(before, after)
        self.assertEqual(changes, [])
        self.assertEqual(issues, [{'edid': 'ExampleItem',
                                   'reason': 'unsupported_cp949',
                                   'field': 'FULL'}])


if __name__ == '__main__':
    unittest.main()
