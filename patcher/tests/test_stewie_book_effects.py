import tempfile
import unittest
from pathlib import Path

import nskr_stewie_book_effects as b
import nskr_output as output


ORIGINAL = (
    b'[Tweaks]\r\n'
    b'bShowBookEffects=1\r\n'
    b'[Book Effects]\r\n'
    b'; skill prefix\r\n'
    b'sPrefix = ' + b.UTF8 + b'\r\n'
    b'[Other]\r\n'
    b'sPrefix = ' + '다른 설정'.encode('utf-8') + b'\r\n'
)


class StewieBookEffectsTests(unittest.TestCase):
    def test_one_section_only_utf8_to_cp949_and_idempotence(self):
        result, changes, issues = b.edit(ORIGINAL, to_display=True)
        self.assertEqual(len(changes), 1)
        self.assertEqual(issues, [])
        self.assertIn(b'sPrefix = ' + b.CP949 + b'\r\n', result)
        self.assertIn(b'sPrefix = ' + '다른 설정'.encode('utf-8') + b'\r\n', result)
        self.assertEqual(b.edit(result, to_display=True), (result, [], []))
        self.assertEqual(b.normalize_reused_input(result), ORIGINAL)

    def test_other_stewie_keys_and_unknown_prefix_unchanged(self):
        unknown = ORIGINAL.replace(b.UTF8, '맞춤 번역'.encode('utf-8'))
        out, changes, issues = b.edit(unknown, to_display=True)
        self.assertEqual(out, unknown)
        self.assertEqual(changes, [])
        self.assertEqual(issues[0]['reason'], 'unreviewed_prefix_value')
        self.assertEqual(b.edit(b'[Other]\nsPrefix=' + b.UTF8 + b'\n',
                                to_display=True)[1], [])

    def test_quotes_and_no_newline_are_preserved(self):
        source = b'[Book Effects]\nsPrefix =  "' + b.UTF8 + b'"  '
        out, changes, issues = b.edit(source, to_display=True)
        self.assertEqual(out, b'[Book Effects]\nsPrefix =  "' + b.CP949 + b'"  ')
        self.assertEqual(len(changes), 1)
        self.assertEqual(issues, [])

    def test_duplicate_prefix_fails_closed(self):
        source = b'[Book Effects]\nsPrefix=' + b.UTF8 + b'\nsPrefix=' + b.UTF8
        with self.assertRaises(ValueError):
            b.edit(source, to_display=True)

    def test_reused_unknown_cp949_rejected(self):
        raw = b'[Book Effects]\nsPrefix=' + '미확인'.encode('cp949') + b'\n'
        with self.assertRaises(ValueError):
            b.normalize_reused_input(raw)

    def test_real_merge_loose_with_repatch_input(self):
        entry = {'kind': 'ini', 'path': b.RELATIVE, 'mappings': [
            {'section': '[Book Effects]', 'key': 'sPrefix',
             'source': 'Permanent', 'dest': b.KOREAN},
        ]}
        first = (b'[Tweaks]\r\nbShowBookEffects=1\r\n'
                 b'[Book Effects]\r\nsPrefix = Permanent\r\n')
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / 'nvse_stewie_tweaks.ini'
            input_file.write_bytes(first)
            merged, detail = output.merge_loose(input_file, entry)
            self.assertEqual(detail['translated'], 1)
            self.assertIn(b.UTF8, merged)
            displayed, edits, issues = b.edit(merged, to_display=True)
            self.assertFalse(issues)
            self.assertEqual(len(edits), 1)
            input_file.write_bytes(displayed)
            repeated, detail2 = output.merge_loose(input_file, entry)
            self.assertEqual(detail2['already_translated'], 1)
            self.assertEqual(repeated, merged)
            displayed_again, edits2, issues2 = b.edit(repeated, to_display=True)
            self.assertEqual(displayed_again, displayed)
            self.assertEqual(len(edits2), 1)
            self.assertFalse(issues2)

    def test_finalizer_writes_only_staged_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / 'stage'
            target = stage / 'mods/StewieTweaks/nvse/plugins/nvse_stewie_tweaks.ini'
            target.parent.mkdir(parents=True)
            target.write_bytes(ORIGINAL)
            rows = [{'output_path': target.relative_to(stage).as_posix(),
                     'path': b.RELATIVE, 'status': 'translated',
                     'output_sha256': 'prior'}]
            b.finalize(stage, rows)
            self.assertEqual(target.read_bytes(), b.edit(ORIGINAL, to_display=True)[0])
            self.assertEqual(len(rows[0]['stewie_book_effects']), 1)
            self.assertIn('verified', rows[0]['status'])
            before = target.read_bytes()
            b.finalize(stage, rows)
            self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
