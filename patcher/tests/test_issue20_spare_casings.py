import copy
import unittest

import nskr_issue20_casings as c


def fixture():
    return {'version': '1.0.8', 'files': [
        {'path': 'SPARE.esp', 'kind': 'plugin-records',
         'mappings': [
             {'owner': owner, 'id': fid, 'signature': 'MISC', 'field': 'FULL',
              'path': 'FULL', 'source': english, 'dest': old}
             for owner, fid, english, old, new in c.SPARE_CASINGS
         ] + [
             {'owner': 'spare.esp', 'id': 'ffffff', 'signature': 'MISC',
              'field': 'FULL', 'path': 'FULL', 'source': 'Some other item',
              'dest': '다른 아이템'}
         ]},
        {'path': 'Unrelated.esp', 'kind': 'plugin-records',
         'mappings': [{'source': 'Case, .223', 'dest': '탄피, .223'}]},
    ]}


class Issue20CasingTests(unittest.TestCase):
    def test_seven_exact_rows_and_prior_upgrade_aliases(self):
        original = fixture()
        saved = copy.deepcopy(original)
        fixed, changes = c.align_spare_casings(original)
        self.assertEqual(original, saved)
        self.assertEqual(len(changes), 7)
        for i, entry in enumerate(fixed['files'][0]['mappings'][:7]):
            self.assertEqual(entry['dest'], c.SPARE_CASINGS[i][4])
            self.assertIn(c.SPARE_CASINGS[i][3], entry['previous_dests'])
        self.assertEqual(fixed['files'][0]['mappings'][7],
                         original['files'][0]['mappings'][7])
        self.assertEqual(fixed['files'][1], original['files'][1])
        self.assertEqual(c.align_spare_casings(fixed), (fixed, []))

    def test_source_or_context_drift_fails_closed(self):
        for key, value in (('source', 'Unreviewed English'),
                           ('field', 'DESC'), ('dest', '다른 값'),
                           ('signature', 'BOOK')):
            with self.subTest(key=key):
                data = fixture()
                data['files'][0]['mappings'][0][key] = value
                with self.assertRaises(ValueError):
                    c.align_spare_casings(data)

    def test_duplicate_identity_fails_closed(self):
        data = fixture()
        data['files'][0]['mappings'].append(
            copy.deepcopy(data['files'][0]['mappings'][0]))
        with self.assertRaises(ValueError):
            c.align_spare_casings(data)

    def test_absent_target_plugin_is_unchanged(self):
        data = {'files': [{'path': 'Unrelated.esp',
                           'kind': 'plugin-records', 'mappings': []}]}
        self.assertEqual(c.align_spare_casings(data), (data, []))


if __name__ == '__main__':
    unittest.main()
