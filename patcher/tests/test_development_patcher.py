import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import nskr
from nskr_output import build_output, output_catalog, stable_context
from nskr_xedit_worker import select_destination


class DevelopmentPolicyTests(unittest.TestCase):
    def catalog(self):
        return {
            'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
            'channel': 'development', 'translation_ready': False,
            'strict_plugin_paths': True,
            'files': [
                {'path': 'MCM/Test.json', 'kind': 'json', 'review_status': 'ui_reviewed'},
                {'path': 'Test.esp', 'kind': 'plugin-records',
                 'review_status': 'existing_sst_candidate',
                 'mappings': [{'path': 'FULL', 'origin': 'sst_direct'}]},
            ],
            'font_bundle': {'provider_strategy': 'separate_mod'},
        }

    def test_release_stays_blocked(self):
        catalog = self.catalog()
        with self.assertRaises(ValueError):
            output_catalog(catalog)
        catalog['translation_ready'] = True
        with self.assertRaises(ValueError):
            output_catalog(catalog)
        with self.assertRaises(ValueError):
            output_catalog(catalog, development=True)

    def test_default_excludes_plugins(self):
        catalog = self.catalog()
        selected = output_catalog(catalog, development=True)
        self.assertEqual([entry['kind'] for entry in selected['files']], ['json'])
        self.assertEqual(selected['selected_scopes'], ['fonts', 'ui'])
        self.assertEqual(len(catalog['files']), 2)

    def test_explicit_plugin_scope_and_name(self):
        selected = output_catalog(self.catalog(), True, {'plugins'}, ['Test.esp'])
        self.assertEqual([entry['path'] for entry in selected['files']], ['Test.esp'])
        self.assertNotIn('font_bundle', selected)
        with self.assertRaises(ValueError):
            output_catalog(self.catalog(), True, {'plugins'}, ['Unknown.esp'])
        with self.assertRaises(ValueError):
            output_catalog(self.catalog(), True, set())

    def test_unreviewed_and_pathless_rejected(self):
        catalog = self.catalog()
        catalog['files'][0]['review_status'] = 'AUTO_QA_PASS_NOT_HUMAN_APPROVED'
        with self.assertRaises(ValueError):
            output_catalog(catalog, True, {'ui'})
        catalog = self.catalog()
        catalog['files'][1]['mappings'][0]['path'] = ''
        with self.assertRaises(ValueError):
            output_catalog(catalog, True, {'plugins'})
        catalog['files'][1]['mappings'][0].update(path='FULL', origin='gemini')
        with self.assertRaises(ValueError):
            output_catalog(catalog, True, {'plugins'})

    def test_strict_record_paths(self):
        item = {'field': 'FULL', 'path': 'FULL', 'source': 'Settings'}
        candidate = {'field': 'FULL', 'path': 'Other/FULL', 'source': 'Settings', 'dest': '설정'}
        self.assertEqual(select_destination(item, [candidate], [], True), (set(), None))
        self.assertEqual(select_destination(item, [candidate], [])[0], {'설정'})
        candidate['path'] = 'FULL'
        self.assertEqual(select_destination(item, [candidate], [], True)[0], {'설정'})
        item['source'] = 'Changed'
        self.assertEqual(select_destination(item, [candidate], [], True), (set(), None))

    def test_runtime_ui_bundle_is_scoped_and_requires_known_source(self):
        catalog = self.catalog()
        catalog['runtime_mods'] = [{'review_status': 'validated_gmst_only_candidate',
                                    'mod': 'Korean UI', 'plugins': ['UI.esp'], 'files': []}]
        self.assertIn('runtime_mods', output_catalog(catalog, True, {'ui'}))
        self.assertNotIn('runtime_mods', output_catalog(catalog, True, {'fonts'}))
        catalog['runtime_mods'][0]['review_status'] = 'unknown'
        with self.assertRaises(ValueError):
            output_catalog(catalog, True, {'ui'})


class DevelopmentOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'MO2'
        profile = self.root / 'profiles/Test'
        profile.mkdir(parents=True)
        data = self.root / 'Game/Data'
        data.mkdir(parents=True)
        for name in ('FalloutNV.esm', 'Fallout3.esm', 'TaleOfTwoWastelands.esm'):
            (data / name).write_bytes(b'')
        (profile / 'modlist.txt').write_text('+Test Mod\n', encoding='utf-8')
        plugins = 'FalloutNV.esm\nFallout3.esm\nTaleOfTwoWastelands.esm\n'
        (profile / 'plugins.txt').write_text(plugins, encoding='cp1252')
        (profile / 'loadorder.txt').write_text(plugins, encoding='utf-8')
        (self.root / 'ModOrganizer.ini').write_text(
            '[General]\ngameName=TTW\nselected_profile=Test\ngamePath='
            + str(self.root / 'Game') + '\n', encoding='utf-8')
        self.source = self.root / 'mods/Test Mod/MCM/Test.json'
        self.source.parent.mkdir(parents=True)
        self.original = b'{\r\n "title": "Settings", "internal": "$Keep", "number": 1.00\r\n}\r\n'
        self.source.write_bytes(self.original)
        self.catalog = self.base / 'Catalog'
        self.catalog.mkdir()
        self.metadata = {
            'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
            'channel': 'development', 'translation_ready': False,
            'files': [{'path': 'MCM/Test.json', 'kind': 'json', 'provider': 'Test Mod',
                       'review_status': 'ui_reviewed',
                       'baseline_sha256': hashlib.sha256(self.original).hexdigest(),
                       'mappings': [{'context': stable_context(json.loads(self.original), ['title']),
                                     'source': 'Settings', 'dest': '설정'}]}]}
        (self.catalog / 'catalog.json').write_text(json.dumps(self.metadata), encoding='utf-8')
        self.installation = nskr.Installation(self.root)

    def test_detached_output_and_original_identity(self):
        target = self.base / 'Output'
        profile = self.root / 'profiles/Test'
        profile_before = {path.relative_to(profile): path.read_bytes()
                          for path in profile.rglob('*') if path.is_file()}
        report = build_output(self.installation, self.catalog, target,
                              development=True, scopes={'ui'})
        translated = target / 'mods/Test Mod/MCM/Test.json'
        self.assertEqual(translated.read_bytes(),
                         self.original.replace(b'Settings', '설정'.encode('utf-8')))
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(report['files'][0]['translated'], 1)
        self.assertFalse(report['translation_ready'])
        self.assertFalse(report['auto_inheritance']['enabled'])
        self.assertEqual(report['channel'], 'development')
        self.assertEqual({path.relative_to(profile): path.read_bytes()
                          for path in profile.rglob('*') if path.is_file()}, profile_before)
        self.assertFalse((target / 'profiles').exists())
        self.assertFalse(any(path.name in {'modlist.txt', 'plugins.txt', 'loadorder.txt'}
                             for path in target.rglob('*')))

    def test_version_mismatch_not_published(self):
        self.source.write_bytes(self.original.replace(b'1.00', b'2.00'))
        target = self.base / 'Output'
        with self.assertRaisesRegex(ValueError, 'No applicable translation'):
            build_output(self.installation, self.catalog, target,
                         development=True, scopes={'ui'})
        self.assertFalse(target.exists())

    def test_runtime_output_preserves_mod_structure_without_activating_plugin(self):
        payload = self.catalog / 'runtime/UI.esp'
        payload.parent.mkdir()
        payload.write_bytes(b'user supplied UI runtime')
        self.metadata['runtime_mods'] = [{
            'mod': 'Korean UI', 'review_status': 'validated_gmst_only_candidate',
            'plugins': ['UI.esp'], 'files': [{
                'path': 'UI.esp', 'payload': 'runtime/UI.esp',
                'payload_sha256': hashlib.sha256(payload.read_bytes()).hexdigest()}]}]
        (self.catalog / 'catalog.json').write_text(json.dumps(self.metadata), encoding='utf-8')
        profile = self.root / 'profiles/Test'
        before = {p.name: p.read_bytes() for p in profile.iterdir() if p.is_file()}
        target = self.base / 'Runtime-Output'
        report = build_output(self.installation, self.catalog, target,
                              development=True, scopes={'ui'})
        self.assertEqual((target / 'mods/Korean UI/UI.esp').read_bytes(), payload.read_bytes())
        self.assertEqual(report['runtime_mods']['plugins_requiring_activation'], ['UI.esp'])
        self.assertEqual({p.name: p.read_bytes() for p in profile.iterdir() if p.is_file()}, before)
        self.assertFalse((target / 'profiles').exists())

    def test_live_installation_and_existing_output_rejected(self):
        with self.assertRaises(ValueError):
            build_output(self.installation, self.catalog, self.root / 'mods/New Mod',
                         development=True, scopes={'ui'})
        target = self.base / 'Existing'
        target.mkdir()
        (target / 'keep.txt').write_text('keep', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            build_output(self.installation, self.catalog, target,
                         development=True, scopes={'ui'})
        self.assertEqual((target / 'keep.txt').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
