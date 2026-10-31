"""Bounded and readonly .fos save title regression fixtures."""
import struct
import unittest
from tools.audit_save_title_header import inspect_header, decode_checks


def sample(title: bytes, name: bytes = b'Courier', level: int = 12):
    buf = bytearray(b'FO3SAVEGAME' + b'\0' * 8 + b'|')
    buf += b'ENGLISH'.ljust(64, b'\0')
    for value in (512, 288, 123):
        buf += struct.pack('<I', value) + b'|'
    def string(v):
        return struct.pack('<H', len(v)) + b'|' + v + b'|'
    buf += string(name)
    buf += string(title)
    buf += struct.pack('<I', level) + b'|'
    buf += string(b'Mojave Wasteland')
    buf += string(b'000.24.41')
    struct.pack_into('<I', buf, 11, len(buf) - 15)
    struct.pack_into('<I', buf, 15, 0x30)
    return bytes(buf)


class SaveHeaderTests(unittest.TestCase):
    def test_cp949_and_utf8_distinguished(self):
        name = '쿠리어'.encode('cp949')
        for enc in ('utf-8', 'cp949'):
            with self.subTest(enc=enc):
                title = '황무지의 방랑자'.encode(enc)
                report = inspect_header(sample(title, name=name))
                self.assertEqual(report['level'], 12)
                self.assertEqual(report['title']['hex'], title.hex())
                self.assertTrue(report['title']['encoding_check'][enc]['valid'])
                self.assertTrue(report['name_is_non_ascii'])
                self.assertNotIn('쿠리어', repr(report))
                self.assertEqual(report['screen_dimensions'], [512, 288])

    def test_english_title_and_invalid_bytes(self):
        plain = inspect_header(sample(b'Drifter'))
        self.assertFalse(plain['title']['has_non_ascii'])
        self.assertTrue(plain['title']['encoding_check']['utf-8']['valid'])
        corrupt = inspect_header(sample(b'\x81'))
        self.assertFalse(corrupt['title']['encoding_check']['utf-8']['valid'])

    def test_invalid_magic_version_and_truncation(self):
        data = sample(b'Drifter')
        with self.assertRaises(ValueError):
            inspect_header(b'Other'+data[5:])
        with self.assertRaises(ValueError):
            inspect_header(data[:-1])
        bad = bytearray(data)
        struct.pack_into('<I', bad, 15, 0x25)
        with self.assertRaises(ValueError):
            inspect_header(bad)


if __name__ == '__main__':
    unittest.main()
