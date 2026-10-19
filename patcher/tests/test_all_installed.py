import struct
import tempfile
import unittest
from pathlib import Path

import nskr
from nskr_output import installed_catalog
from nskr_xedit import _session_plugins


def plugin(path, master=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b''
    if master:
        value = master.encode('ascii') + b'\0'
        payload = b'MAST' + struct.pack('<H', len(value)) + value
    path.write_bytes(b'TES4' + struct.pack('<I', len(payload)) + bytes(16) + payload)


class AllInstalledTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        game = self.root / 'Game'
        plugin(game / 'Data/FalloutNV.esm')
        plugin(self.root / 'mods/Variant A/Shared.esp', 'FalloutNV.esm')
        plugin(self.root / 'mods/Variant B/Shared.esp', 'FalloutNV.esm')
        plugin(self.root / 'mods/Disabled/Other.esp', 'Shared.esp')
        plugin(self.root / 'mods/Excluded/Shared.esp', 'FalloutNV.esm')
        (self.root / 'ModOrganizer.ini').write_text(
            f'[General]\ngameName=TTW\ngamePath={game}\nselected_profile=Nonexistent\n',
            encoding='utf-8')

    def test_no_profile_required_and_disabled_mods_are_included(self):
        installation = nskr.Installation(self.root, all_installed=True)
        self.assertIn('other.esp', installation.active_keys)
        self.assertEqual(installation.profile, '')
        self.assertFalse((self.root / 'profiles').exists())

    def test_every_physical_variant_and_master_order(self):
        installation = nskr.Installation(self.root, all_installed=True)
        entries = [{'path': 'Shared.esp', 'provider': 'Variant A',
                    'kind': 'plugin-records', 'mappings': []},
                   {'path': 'Other.esp', 'provider': 'Disabled',
                    'kind': 'plugin-records', 'mappings': []}]
        selected, catalog = installed_catalog(installation, {
            'files': entries, 'excluded_test_providers': ['Excluded']})
        variants = [e for e in catalog['files'] if e['path'] == 'Shared.esp']
        self.assertEqual({e['provider'] for e in variants}, {'Variant A', 'Variant B'})
        self.assertEqual(selected.source('Shared.esp'),
                         self.root / 'mods/Variant A/Shared.esp')
        self.assertEqual(_session_plugins(selected, [entries[1]], None),
                         ['FalloutNV.esm', 'Shared.esp', 'Other.esp'])
        self.assertEqual(_session_plugins(selected, [entries[0]], {
            'Shared.esp': self.root / 'mods/Variant B/Shared.esp'}),
            ['FalloutNV.esm', 'Shared.esp'])
        self.assertEqual(len(installation.providers['shared.esp']), 3)

    def test_variant_specific_mapping_wins_without_changing_primary_source(self):
        installation = nskr.Installation(self.root, all_installed=True)
        base = {'path': 'Shared.esp', 'provider': 'Variant A',
                'kind': 'plugin-records', 'mappings': [{'source': 'Primary'}]}
        variant = {**base, 'optional': True, 'provider': 'Variant B',
                   'mappings': [{'source': 'Variant'}]}
        selected, catalog = installed_catalog(installation, {
            'files': [base, variant], 'excluded_test_providers': ['Excluded']})
        self.assertEqual(len(catalog['files']), 2)
        by_provider = {entry['provider']: entry for entry in catalog['files']}
        self.assertEqual(by_provider['Variant B']['mappings'], [{'source': 'Variant'}])
        self.assertTrue(by_provider['Variant B']['optional'])
        self.assertFalse(by_provider['Variant A'].get('optional', False))
        self.assertEqual(selected.source('Shared.esp'), self.root / 'mods/Variant A/Shared.esp')


if __name__ == '__main__':
    unittest.main()
