"""Regression tests for issue #11's deliberately unlocalized perk description."""
import copy
import unittest

import nskr_xedit
from nskr_output import (
    CONCENTRATED_FIRE_ENGLISH_SOURCE, preserve_english_concentrated_fire,
)


def perk_desc(plugin, *, source=None):
    return {
        'owner': 'falloutnv.esm', 'id': '044caf', 'signature': 'PERK',
        'field': 'DESC', 'path': 'DESC', 'field_occurrence': 0,
        'source': source or CONCENTRATED_FIRE_ENGLISH_SOURCE[plugin.casefold()],
        'dest': '집중 사격: 과거 한국어 퍽 설명', 'origin': 'sst_direct',
    }


class ConcentratedFireEnglishTests(unittest.TestCase):
    def test_two_source_variants_and_previous_korean_upgrade(self):
        files = [
            {'path': plugin, 'kind': 'plugin-records', 'mappings': [
                perk_desc(plugin),
                {'owner': 'falloutnv.esm', 'id': '044caf', 'signature': 'PERK',
                 'field': 'FULL', 'path': 'FULL', 'field_occurrence': 0,
                 'source': 'Concentrated Fire', 'dest': '집중 사격'}]}
            for plugin in ('FalloutNV.esm', 'S6S Base Game Perks Redux.esp')
        ]
        catalog = {'files': files}
        original = copy.deepcopy(catalog)
        revised, exceptions = preserve_english_concentrated_fire(catalog)
        self.assertEqual(catalog, original)
        self.assertEqual(len(exceptions), 2)
        for entry in revised['files']:
            target = entry['mappings'][0]
            self.assertEqual(target['source'], target['dest'])
            self.assertIn('집중 사격: 과거 한국어 퍽 설명', target['previous_dests'])
            self.assertEqual(entry['mappings'][1]['dest'], '집중 사격')
            nskr_xedit.validate_mapping(target)
        again, _ = preserve_english_concentrated_fire(revised)
        self.assertEqual(again, revised)

    def test_never_change_unknown_source_or_unrelated_field(self):
        plugin = 'S6S Base Game Perks Redux.esp'
        bad = perk_desc(plugin, source='Changed mod update English')
        catalog = {'files': [{'path': plugin, 'kind': 'plugin-records',
                              'mappings': [bad]}]}
        with self.assertRaisesRegex(ValueError, 'source changed'):
            preserve_english_concentrated_fire(catalog)
        self.assertEqual(catalog['files'][0]['mappings'][0], bad)
        other = {**perk_desc(plugin), 'id': '044cae'}
        revised, affected = preserve_english_concentrated_fire({
            'files': [{'path': plugin, 'kind': 'plugin-records', 'mappings': [other]}]})
        self.assertEqual(revised['files'][0]['mappings'][0], other)
        self.assertEqual(affected, [])


if __name__ == '__main__':
    unittest.main()
