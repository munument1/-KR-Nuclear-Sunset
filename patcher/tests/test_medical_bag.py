"""Portable tests; no user installation or original third-party ESP needed."""
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def _plugin_fixture(self, already_translated=()):
        """Synthetic TES4/SCPT records: no proprietary game files required."""
        def sub(name, raw):
            return name + struct.pack('<H', len(raw)) + raw

        def rec(name, fid, raw):
            return struct.pack('<4sIIIII', name, len(raw), 0, fid, 0, 0) + raw

        scripts = ('SCPTUpdateDummyNamesCall', 'SCPTUpdateDummyNamesHandler')
        approved, records = {}, []
        for index, edid in enumerate(scripts):
            source, code = self.fixture()
            approved[edid] = medical.digest(source, code)
            if edid in already_translated:
                source, code, _ = medical.replace_literals(source, code)
            body = (sub(b'EDID', edid.encode('ascii') + b'\0')
                    + sub(b'SCHR', struct.pack('<5I', 1, 0, len(code), 1, 0))
                    + sub(b'SCDA', code) + sub(b'SCTX', source))
            records.append(rec(b'SCPT', 0x100 + index, body))
        return rec(b'TES4', 0, sub(b'HEDR', bytes(12))) + b''.join(records), approved

    def test_verified_previous_translation_is_byte_identical_on_repeat(self):
        original, approved = self._plugin_fixture()
        with patch.dict(medical.APPROVED, approved, clear=True):
            first, initial = medical.patch_bytes(original)
            self.assertNotEqual(first, original)
            self.assertEqual({row['status'] for row in initial.values()}, {'translated'})
            second, repeated = medical.patch_bytes(first)
            self.assertEqual(first, second)
            self.assertEqual({row['status'] for row in repeated.values()},
                             {'already_translated'})

    def test_mixed_original_and_prior_translation_is_safe(self):
        original, approved = self._plugin_fixture(
            already_translated=('SCPTUpdateDummyNamesCall',))
        with patch.dict(medical.APPROVED, approved, clear=True):
            updated, statuses = medical.patch_bytes(original)
            self.assertEqual(statuses['SCPTUpdateDummyNamesCall']['status'],
                             'already_translated')
            self.assertEqual(statuses['SCPTUpdateDummyNamesHandler']['status'],
                             'translated')
            self.assertEqual(medical.patch_bytes(updated)[0], updated)

    def test_unknown_script_changes_rejected_before_and_after_translation(self):
        original, approved = self._plugin_fixture()
        with patch.dict(medical.APPROVED, approved, clear=True):
            modified_original = original.replace(b'NEXT', b'BEXT', 1)
            with self.assertRaisesRegex(ValueError, 'Script hash changed'):
                medical.patch_bytes(modified_original)
            first, _ = medical.patch_bytes(original)
            changed_opcode = first.replace(b'NEXT', b'BEXT', 1)
            with self.assertRaisesRegex(ValueError, 'Script hash changed'):
                medical.patch_bytes(changed_opcode)
            partial_translation = first.replace(
                '회복량:  '.encode('utf-8'), b'Restores ', 1)
            with self.assertRaisesRegex(ValueError, 'Script hash changed'):
                medical.patch_bytes(partial_translation)

    def test_finalizer_accepts_prior_output_without_modifying_bytes(self):
        original, approved = self._plugin_fixture()
        with tempfile.TemporaryDirectory() as temp, patch.dict(
                medical.APPROVED, approved, clear=True):
            stage = Path(temp)
            relative = Path('mods') / medical.PROVIDER / medical.RELATIVE_PATH
            target = stage / relative
            target.parent.mkdir(parents=True)
            target.write_bytes(original)
            row = {'output_path': relative.as_posix(),
                   'provider': medical.PROVIDER, 'status': 'translated'}
            medical.finalize(None, stage, [row])
            first = target.read_bytes()
            self.assertNotEqual(first, original)
            medical.finalize(None, stage, [row])
            self.assertEqual(target.read_bytes(), first)
            self.assertIn('medical_bag_runtime_name_already_verified', row['status'])
            self.assertEqual(row['medical_bag_dynamic']['SCPTUpdateDummyNamesCall']['status'],
                             'already_translated')


if __name__ == '__main__':
    unittest.main()
