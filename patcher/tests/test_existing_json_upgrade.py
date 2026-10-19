"""Regression tests: rerunning the patcher on an already localized MCM JSON."""
import json
from pathlib import Path
import tempfile
import unittest

from nskr_output import merge_loose, stable_context


class ExistingKoreanJsonUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'Menu.json'
        self.context = stable_context({'title': 'Settings'}, ['title'])
        self.entry = {'kind': 'json', 'mappings': [{
            'context': self.context,
            'source': 'Settings',
            'dest': '설정',
        }]}

    def apply(self, text, *, entry=None, bom=False):
        self.path.write_bytes(text.encode('utf-8-sig' if bom else 'utf-8'))
        return merge_loose(self.path, entry or self.entry)

    def test_fresh_then_rerun_is_idempotent(self):
        original = '{"title":"Settings", "enabled":true}\r\n'
        converted, first = self.apply(original, bom=True)
        self.assertEqual(first['translated'], 1)
        self.assertEqual(first['already_translated'], 0)
        self.assertEqual(first['unmatched'], 0)
        self.assertTrue(converted.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(converted.decode('utf-8-sig'),
                         original.replace('Settings', '설정'))
        self.path.write_bytes(converted)
        again, second = merge_loose(self.path, self.entry)
        self.assertEqual(converted, again)
        self.assertEqual(second['translated'], 0)
        self.assertEqual(second['already_translated'], 1)
        self.assertEqual(second['unmatched'], 0)

    def test_reviewed_previous_korean_is_upgraded(self):
        entry = {'kind': 'json', 'mappings': [{
            'context': self.context, 'source': 'Settings',
            'dest': '새 설정', 'previous_dests': ['옛 설정'],
        }]}
        out, stats = self.apply('{"title":"옛 설정"}', entry=entry)
        self.assertEqual(json.loads(out)['title'], '새 설정')
        self.assertEqual(stats['translated'], 1)
        self.assertEqual(stats['unmatched'], 0)

    def test_unknown_custom_text_is_not_replaced(self):
        original = '{"title":"사용자가 바꾼 문구"}'
        out, stats = self.apply(original)
        self.assertEqual(out.decode(), original)
        self.assertEqual(stats['unmatched'], 1)
        self.assertEqual(stats['already_translated'], 0)

    def test_wrong_context_cannot_match_previous_translation(self):
        obj = {'title': '사용자 지정', 'nested': {'title': '설정'}}
        raw = json.dumps(obj, ensure_ascii=False)
        out, stats = self.apply(raw)
        self.assertEqual(out.decode(), raw)
        self.assertEqual(stats['already_translated'], 0)
        self.assertEqual(stats['unmatched'], 2)

    def test_conflicting_previous_alias_fails_closed(self):
        entry = {'kind': 'json', 'mappings': [
            {'context': self.context, 'source': 'Settings',
             'dest': '설정 A', 'previous_dests': ['옛 설정']},
            {'context': self.context, 'source': 'Preferences',
             'dest': '설정 B', 'previous_dests': ['옛 설정']},
        ]}
        out, stats = self.apply('{"title":"옛 설정"}', entry=entry)
        self.assertEqual(json.loads(out)['title'], '옛 설정')
        self.assertEqual(stats['unmatched'], 1)
        self.assertEqual(stats['unmatched_entries'][0]['reason'], 'ambiguous')

    def test_ini_already_translated_is_also_idempotent(self):
        entry = {'kind': 'ini', 'mappings': [{
            'section': '[UI]', 'key': 'sName', 'source': 'Settings',
            'dest': '설정',
        }]}
        self.path.write_text('[UI]\r\nsName = 설정\r\n', encoding='utf-8')
        raw = self.path.read_bytes()
        out, stats = merge_loose(self.path, entry)
        self.assertEqual(out, raw)
        self.assertEqual(stats['unmatched'], 0)
        self.assertEqual(stats['already_translated'], 1)


if __name__ == '__main__':
    unittest.main()
