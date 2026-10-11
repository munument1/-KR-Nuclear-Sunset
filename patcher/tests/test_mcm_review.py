import json
from pathlib import Path
import tempfile
import unittest

from nskr_output import check_pair, merge_loose, stable_context, translation_companion
from types import SimpleNamespace
from tools.loose_translation import render_json


class MCMReviewTests(unittest.TestCase):
    def test_translation_companion_preserves_only_corresponding_json(self):
        installation = SimpleNamespace(providers={
            'mcm/translations/itemcards.ini': [{'path': 'MCM/Translations/ItemCards.ini'}]})
        self.assertEqual(translation_companion(installation, 'MCM/ItemCards.json'),
                         'MCM/Translations/ItemCards.ini')
        self.assertIsNone(translation_companion(installation, 'MCM/Other.json'))
        self.assertIsNone(translation_companion(installation, 'config/ItemCards.json'))
        self.assertIsNone(translation_companion(installation, 'MCM/Translations/ItemCards.ini'))

    def test_lossless_json(self):
        text = '{\r\n\t"title": "Settings", "value": 1.00, "vars": ["$BlendTime"],\r\n "strings": ["On", "Off"]\r\n}'
        result = render_json(text, {('title',): '설정', ('strings', 0): '켬'})
        self.assertEqual(result, text.replace('"Settings"', '"설정"').replace('"On"', '"켬"'))
        self.assertEqual(json.loads(result)['vars'], ['$BlendTime'])

    def test_tokens(self):
        check_pair('%re.g. %.0f', '%r예: %.0f')
        check_pair('%qToggle%q', '%q전환%q')
        with self.assertRaises(ValueError):
            check_pair('%qToggle%q', '전환')
        for dest in ('%r예: %f', '예: %.0f'):
            with self.assertRaises(ValueError):
                check_pair('%re.g. %.0f', dest)
        with self.assertRaises(ValueError):
            check_pair('$BlendTime %.0f', '$Other %.0f')

    def test_merge_preserves_bom_and_ini(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.ini'
            source = '; comment\r\n[UI]\r\n $Key = "Settings"  \r\n[Other]\r\n$Key=Settings\r\n'
            path.write_bytes(source.encode('utf-8-sig'))
            result, stats = merge_loose(path, {'kind': 'ini', 'mappings': [
                {'section': '[UI]', 'key': '$Key', 'source': 'Settings', 'dest': '설정'},
                {'section': '[Other]', 'key': '$Key', 'source': 'Settings', 'dest': '다른 설정'}]})
            self.assertEqual(result.decode('utf-8-sig'), source.replace('"Settings"', '"설정"').replace('$Key=Settings', '$Key=다른 설정'))
            self.assertTrue(result.startswith(b'\xef\xbb\xbf'))
            self.assertEqual(stats['translated'], 2)

    def test_display_only_ini_ignores_settings_but_detects_changed_display_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.ini'
            text = '[UI]\nsLabel = Permanent\nnValue = 1\nsSound = SoundID\n'
            path.write_bytes(text.encode('utf-8'))
            entry = {'kind': 'ini', 'display_mappings_only': True, 'mappings': [
                {'section': '[UI]', 'key': 'sLabel', 'source': 'Permanent', 'dest': '영구'}]}
            raw, stats = merge_loose(path, entry)
            self.assertEqual(raw.decode('utf-8'), text.replace('Permanent', '영구'))
            self.assertEqual(stats['translated'], 1)
            self.assertEqual(stats['unchanged_by_design'], 2)
            self.assertEqual(stats['unmatched'], 0)
            path.write_bytes(text.replace('Permanent', 'Temporary').encode('utf-8'))
            raw, stats = merge_loose(path, entry)
            self.assertEqual(stats['unmatched'], 1)

    def test_merge_exact_context(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.json'
            source = '{"title":"Settings", "nested":{"title":"Settings"}, "internal":"Settings"}\r\n'
            path.write_bytes(source.encode('utf-8'))
            obj = json.loads(source)
            result, stats = merge_loose(path, {'kind': 'json', 'mappings': [
                {'context': stable_context(obj, ['title']), 'source': 'Settings', 'dest': '설정'}]})
            self.assertEqual(result.decode(), source.replace('"title":"Settings"', '"title":"설정"', 1))
            self.assertEqual(stats['unmatched'], 1)


if __name__ == '__main__':
    unittest.main()
