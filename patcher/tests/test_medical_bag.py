"""Portable tests; no user installation or original third-party ESP needed."""
import struct
import unittest

import nskr_medical_bag as medical


class MedicalBagDynamicTests(unittest.TestCase):
    def fixture(self):
        source = b'scn Sample\r\n'
        code = b'BEGIN'
        for original, _ in medical.PAIRS:
            for i in range(medical.COUNTS[original]):
                raw = original.encode('ascii')
                source += b'output "' + raw + b'"\r\n'
                code += b'OP' + struct.pack('<H', len(raw)) + raw + b'NEXT'
        source += b'end\r\n'
        return source, code

    def test_compiled_lengths_and_unrelated_bytes_remain_identical(self):
        src, code = self.fixture()
        new_src, new_code, counts = medical.replace_literals(src, code)
        self.assertEqual(counts, medical.COUNTS)
        self.assertEqual(len(new_code),len(code))
        self.assertEqual(new_code.count(b'OP'),code.count(b'OP'))
        self.assertEqual(new_code.count(b'NEXT'),code.count(b'NEXT'))
        self.assertEqual(new_src.count('한 부위의 체력 회복: '.encode()),1)
        self.assertEqual(new_code.count('회복량:  '.encode('cp949')),7)
        self.assertEqual(new_code.count('% (최대 체력)'.encode('cp949')),6)

    def test_rejects_unreviewed_literal_count(self):
        src, code = self.fixture()
        with self.assertRaisesRegex(ValueError,'Unapproved quoted source count'):
            medical.replace_literals(src.replace(b'output "Restores "',b'output "Not same "',1),code)

    def test_rejects_changed_compiled_operand(self):
        src, code = self.fixture()
        with self.assertRaisesRegex(ValueError,'Unapproved SCDA string operand count'):
            medical.replace_literals(src,code.replace(b'OP\x09\x00Restores ',b'OP\x08\x00Restores ',1))

    def test_translation_fits_original_byte_budgets(self):
        for original,dest in medical.PAIRS:
            with self.subTest(original=original):
                self.assertLessEqual(len(dest.encode('cp949')),len(original.encode('ascii')))


if __name__ == '__main__':
    unittest.main()
