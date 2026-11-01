"""Test all reviewed B42 INI translations without modifying the modlist."""
import hashlib
from pathlib import Path
import tempfile
import types
import unittest

import nskr_b42_descriptions as mod
from nskr_b42_data import DATA


SOURCE = Path(r'C:\Modlists\NuclearSunset\mods')
STANDALONE = Path(r'D:\Codex_Trans\_NS_SaveTitle_Investigation\b42_completion\Output\mods')


class B42FullTests(unittest.TestCase):
    def test_bundled_data_coverage(self):
        self.assertEqual(len(DATA),118)
        self.assertEqual(sum(len(d['rows']) for d in DATA),2992)
        providers={d['provider'] for d in DATA}
        self.assertEqual(len(providers),12)
        self.assertIn('B42 Descriptions Revised',providers)
        self.assertNotIn('[OP] - B42 Descriptions',providers)
        self.assertNotIn('B42 Descriptions - New Vegas Bounties I LE',providers)

    def test_edit_all_known_files_exact_staging_hash(self):
        for data in DATA:
            rel=Path(data['provider'])/data['path']
            original=(SOURCE/rel).read_bytes()
            after=mod.patch_ini(original,data)
            self.assertEqual(after,(STANDALONE/rel).read_bytes())
            self.assertNotEqual(original,after)

    def test_rejects_unreviewed_input(self):
        data=DATA[0]
        source=(SOURCE/data['provider']/data['path']).read_bytes()
        with self.assertRaisesRegex(ValueError,'SHA'):
            mod.patch_ini(source+b'\n; source changed',data)

    def test_production_finalizer_matches_standalone_118_files(self):
        install=types.SimpleNamespace(
            mods=SOURCE,
            mods_enabled=[d['provider'] for d in DATA],
        )
        with tempfile.TemporaryDirectory(prefix='nskr_b42_') as folder:
            root=Path(folder)
            report=[]
            result=mod.finalize(install,root,report)
            self.assertEqual(result['files'],118)
            self.assertEqual(result['translated'],2992)
            self.assertEqual(result['skipped'],[])
            self.assertEqual(len(report),118)
            for row in report:
                staged=root/row['output_path']
                self.assertEqual(staged.read_bytes(),
                    (STANDALONE/row['provider']/row['path']).read_bytes())
                self.assertEqual(hashlib.sha256(staged.read_bytes()).hexdigest(),
                                 row['output_sha256'])


if __name__=='__main__':
    unittest.main()
