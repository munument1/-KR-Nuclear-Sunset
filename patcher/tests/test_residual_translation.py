import unittest
from nskr_xedit_worker import normalize_cp1252_sources
from tools.prepare_remaining_translation_work import saved_translation_is_localized
from tools.residual_translation_validation import (
    validate, normalize_boundary_whitespace)


class ResidualValidationTests(unittest.TestCase):
    def test_english_rewording_is_not_a_completed_korean_translation(self):
        self.assertFalse(saved_translation_is_localized('First English note', 'Other English note'))
        self.assertTrue(saved_translation_is_localized('First English note', '첫 번째 메모'))
        self.assertTrue(saved_translation_is_localized('NCR', 'NCR'))

    def test_cp1252_normalization_requires_explicit_schema_and_exact_slot(self):
        items = [{'field': 'FULL', 'path': 'FULL', 'field_occurrence': 0,
                  'source': 'Cliff Briscoe�s Trunk'}]
        row = {'field': 'FULL', 'path': 'FULL', 'field_occurrence': 0,
               'source': 'Cliff Briscoe’s Trunk'}
        normalize_cp1252_sources(items, [row])
        self.assertEqual(items[0]['source'], 'Cliff Briscoe�s Trunk')
        normalize_cp1252_sources(items, [{**row, 'source_encoding': 'cp1252',
                                        'field_occurrence': 1}])
        self.assertEqual(items[0]['source'], 'Cliff Briscoe�s Trunk')
        normalize_cp1252_sources(items, [{**row, 'source_encoding': 'cp1252'}])
        self.assertEqual(items[0]['source'], row['source'])

    def test_engine_tokens_remain_required(self):
        self.assertEqual(validate('%s: %d%%<br>$Value', '%s: %d%%<br>$Value'), [])
        self.assertIn('protected_token_mismatch', validate('%d left', '남음'))
        self.assertIn('protected_token_mismatch', validate('<font=1>Yes</font>', '예'))

    def test_narrative_markers_and_percent_prose_are_not_format_tokens(self):
        self.assertEqual(validate('<<BEGIN FILE>>', '<<파일 시작>>'), [])
        self.assertEqual(validate('20% damage', '피해 20%'), [])

    def test_source_layout_is_preserved(self):
        self.assertEqual(normalize_boundary_whitespace('  Text\r\n', '문구'), '  문구\r\n')
        self.assertEqual(validate('Text\r\n', '문구\r\n'), [])
        self.assertIn('newline_count_mismatch', validate('One\nTwo', '하나 둘'))

    def test_message_budget_is_checked_in_bytes(self):
        self.assertIn('message_byte_budget_exceeded',
                      validate('Short', '가' * 342, 'MESG', 'DESC'))
        self.assertEqual(validate('Short', '가' * 341, 'MESG', 'DESC'), [])


if __name__ == '__main__':
    unittest.main()
