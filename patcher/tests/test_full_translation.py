import unittest
from types import SimpleNamespace

from nskr_xedit_worker import matching_rows, select_destination, unmatched_candidates
from nskr_output import output_catalog, original_installation
from tools.prepare_full_translation import pick, gemini_matches, canonical_text


class FullTranslationPolicyTests(unittest.TestCase):
    def test_test_overlay_is_ignored_without_mutating_original_inventory(self):
        original = SimpleNamespace(
            mods_enabled=['Original', 'Explicit Test'],
            providers={'test.esm': [{'provider': 'Original'}, {'provider': 'Explicit Test'}]})
        filtered = original_installation(original, ['Explicit Test'])
        self.assertEqual(filtered.providers['test.esm'], [{'provider': 'Original'}])
        self.assertEqual(original.mods_enabled, ['Original', 'Explicit Test'])
        self.assertEqual(len(original.providers['test.esm']), 2)

    def test_resolution_keeps_existing_translation_and_rejects_conflicts(self):
        old = {'dest': '기존 번역', 'origin': 'sst_direct'}
        new = {'dest': '새 번역', 'origin': 'gemini_candidate'}
        self.assertEqual(pick([(0, old), (1, new)]), old)
        self.assertIsNone(pick([(0, old), (0, new)]))
        self.assertEqual(canonical_text('a\r\nb'), 'a\nb')

    def test_gemini_occurrence_requires_exact_source_and_position(self):
        candidate = {'field': 'NAM1', 'source': 'Same text', 'occurrence': 1}
        item = {'field': 'NAM1', 'source': 'Same text', 'field_occurrence': 1}
        self.assertTrue(gemini_matches(candidate, item))
        self.assertFalse(gemini_matches(candidate, {**item, 'field_occurrence': 0}))
        self.assertFalse(gemini_matches(candidate, {**item, 'source': 'Changed text'}))

    def test_provenance_and_real_unmatched_candidates(self):
        row = {'field': 'FULL', 'path': 'FULL', 'source': 'Name',
               'dest': '이름', 'origin': 'gemini_candidate'}
        item = {'field': 'FULL', 'path': 'FULL', 'source': 'Name'}
        unrelated = {'field': 'DESC', 'path': 'DESC', 'source': ''}
        self.assertEqual(select_destination(item, [row], [], True),
                         ({'이름'}, 'gemini_candidate'))
        self.assertEqual(unmatched_candidates([item, unrelated], [row], True), [])
        changed = {**item, 'source': 'Different name'}
        self.assertEqual(unmatched_candidates([changed], [row], True), [row])
        self.assertEqual(matching_rows({**item, 'path': 'Other'}, [row], True), [])

    def test_full_unreleased_catalog_allows_only_resolved_sources(self):
        catalog = {'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
                   'channel': 'development', 'translation_ready': False,
                   'full_translation_catalog': True, 'strict_plugin_paths': True,
                   'files': [{'kind': 'plugin-records', 'path': 'Test.esm',
                              'review_status': 'source_matched_candidate',
                              'mappings': [{'path': 'FULL', 'origin': 'gemini_candidate'}]}]}
        self.assertEqual(len(output_catalog(catalog, True, {'plugins'})['files']), 1)
        with self.assertRaises(ValueError):
            output_catalog(catalog)
        catalog['files'][0]['mappings'][0]['path'] = ''
        with self.assertRaises(ValueError):
            output_catalog(catalog, True, {'plugins'})
