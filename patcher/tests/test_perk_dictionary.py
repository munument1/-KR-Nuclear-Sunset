"""Compiled description translation through tNVSE's verified overlay paths."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import nskr
import nskr_perk_dictionary as perk


INI = (b'[Multibyte]\r\nbEnableMultibyteFontHook = 1\r\n'
       b'[Dictionary]\r\nbEnableDictionaryTranslation = 1\r\n'
       b'bEnableDictionaryWildcardTranslation = 1\r\n'
       b'bEnableDictionaryRegexTranslation = 0\r\n'
       b'bEnableDictionaryPerkDescriptionTranslation = 0\r\n'
       b'bEnableDictionaryMixedSourceTranslation = 0\r\n')
XML = (b'<tNVSE><dictionary><json path="Data/nvse/plugins/NSKR_UI_Translations.json" '
       b'priority="50"/></dictionary></tNVSE>')
EMPTY = json.dumps([{'original': 'Other UI', 'translation': '안내'}],
                   ensure_ascii=False).encode('utf-8')


class StubInstallation:
    def __init__(self, root):
        self.game = root / 'game'
        self.mods = root / 'mods'
        self.mods_enabled = []
        self.providers = {}
        self.virtual = root / 'active'
        (self.virtual / 'NVSE/plugins').mkdir(parents=True)
        for name, payload in [('tnvse.ini', INI), ('tnvse_dictionary.xml', XML),
                              ('NSKR_UI_Translations.json', EMPTY)]:
            (self.virtual / 'NVSE/plugins' / name).write_bytes(payload)

    def source(self, relative):
        return self.virtual / relative


class CompiledPerkDictionaryTests(unittest.TestCase):
    def test_source_verified_full_headhunter_and_bounded_suffix_only(self):
        entries = perk.dictionary_entries()
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]['original'], perk.CASES[0]['source_en'].replace('%%', '%'))
        self.assertEqual(entries[1]['original'], perk.CASES[0]['source_en'])
        self.assertIn('재장전 속도가 25%', entries[0]['translation'])
        self.assertEqual(entries[2]['original'], '[%]' + perk.FAST_SUFFIX_EN)
        self.assertEqual(entries[2]['translation'], '[%]' + perk.FAST_SUFFIX_KO)
        self.assertNotIn(perk.FAST_BASE_KO + perk.FAST_SUFFIX_EN,
                         {e['original'] for e in entries})

    def test_ini_switch_only_and_xml_addition_idempotent(self):
        ini = perk.render_ini_overlay(INI)
        self.assertEqual(ini, INI.replace(b'MixedSourceTranslation = 0', b'MixedSourceTranslation = 1'))
        self.assertEqual(perk.render_ini_overlay(ini), ini)
        xml = perk.render_xml_overlay(XML)
        self.assertEqual(xml.count(b'NSKR_Perk_Descriptions.json'), 1)
        self.assertIn(b'NSKR_UI_Translations.json', xml)
        self.assertEqual(perk.render_xml_overlay(xml), xml)

    def test_reject_preexisting_wildcard_and_global_regex(self):
        with self.assertRaisesRegex(ValueError, 'wildcard'):
            perk.render_dictionary_overlay(INI, XML, b'[{"original":"[%] warning","translation":"x"}]')
        with self.assertRaisesRegex(ValueError, 'regex'):
            perk.render_ini_overlay(INI.replace(b'RegexTranslation = 0', b'RegexTranslation = 1'))
        with self.assertRaisesRegex(ValueError, 'wildcard support'):
            perk.render_ini_overlay(INI.replace(b'WildcardTranslation = 1', b'WildcardTranslation = 0'))

    def test_stage_prefers_new_korean_fonts_ini_and_staged_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            install = StubInstallation(root)
            stage = root / 'stage'
            fonts = stage / 'mods' / 'Nuclear Sunset - Korean Fonts for tNVSE' / 'NVSE/plugins'
            fonts.mkdir(parents=True)
            # The stage owns a newer Korean font configuration: preserve this
            # entirely except the mixed-source switch.
            font_ini = INI + b';fresh-font-provider\r\n'
            (fonts / 'tnvse.ini').write_bytes(font_ini)
            staged_old = stage / 'mods' / 'NSKR Test' / 'NVSE/plugins'
            staged_old.mkdir(parents=True)
            (staged_old / 'NSKR_UI_Translations.json').write_bytes(EMPTY)

            with patch.object(perk, '_source_matches', return_value=(True, 'source_literals_verified')):
                rows, status = perk.build_perk_dictionary(install, stage, set())
            self.assertEqual(len(rows), 3)
            self.assertEqual(status['dictionary_entries'], 4)
            self.assertTrue(status['enabled_global_mixed_source_matching'])
            output = stage / 'mods' / perk.MOD_NAME / 'NVSE/plugins'
            self.assertIn(b';fresh-font-provider', (output / 'tnvse.ini').read_bytes())
            self.assertIn(b'MixedSourceTranslation = 1', (output / 'tnvse.ini').read_bytes())
            self.assertEqual((fonts / 'tnvse.ini').read_bytes(), font_ini)
            self.assertEqual((staged_old / 'NSKR_UI_Translations.json').read_bytes(), EMPTY)
            contents = json.loads((output / perk.DICT_FILENAME).read_text(encoding='utf-8'))
            self.assertEqual(contents, perk.dictionary_entries())

    def test_no_existing_dictionary_xml_generates_minimal_overlay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            install = StubInstallation(root)
            (install.virtual / 'NVSE/plugins/tnvse_dictionary.xml').unlink()
            old_source = install.source

            def source(relative):
                if relative.endswith('tnvse_dictionary.xml'):
                    raise ValueError('No active XML provider')
                return old_source(relative)

            install.source = source
            with patch.object(perk, '_source_matches', return_value=(True, 'source_literals_verified')):
                rows, status = perk.build_perk_dictionary(install, root / 'stage', set())
            self.assertEqual(len(rows), 3)
            self.assertEqual(status['status'], 'generated')
            xml = (root / 'stage/mods' / perk.MOD_NAME / 'NVSE/plugins/tnvse_dictionary.xml').read_text()
            self.assertIn('NSKR_Perk_Descriptions.json', xml)

    def test_gui_all_installed_resolves_selected_profile_not_alphabetical_provider(self):
        """A disabled tNVSE config sorts last in all-installed inventory."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'game/Data').mkdir(parents=True)
            (root / 'game/Data/FalloutNV.esm').write_bytes(b'TES4')
            good = root / 'mods/Good Korean UI/NVSE/plugins'
            bad = root / 'mods/tNVSE Default Config/NVSE/plugins'
            good.mkdir(parents=True)
            bad.mkdir(parents=True)
            for path in (good, bad):
                (path / 'tnvse.ini').write_bytes(INI)
            (good / 'tnvse_dictionary.xml').write_bytes(XML)
            (good / 'NSKR_UI_Translations.json').write_bytes(EMPTY)
            (bad / 'tnvse_dictionary.xml').write_bytes(
                b'<tNVSE><dictionary><json path="Data/nvse/plugins/first.json"/>'
                b'<json path="Data/nvse/plugins/second.json"/></dictionary></tNVSE>')
            profile = root / 'profiles/KR Test'
            profile.mkdir(parents=True)
            (profile / 'modlist.txt').write_text(
                '-tNVSE Default Config\n+Good Korean UI\n', encoding='utf-8')
            (profile / 'plugins.txt').write_text('', encoding='utf-8')
            (root / 'ModOrganizer.ini').write_text(
                f'[General]\ngameName=Fallout New Vegas\n'
                f'gamePath={root / "game"}\nselected_profile=KR Test\n'
                f'[Settings]\nbase_directory={root}\n', encoding='utf-8')

            all_installation = nskr.Installation(root, all_installed=True)
            self.assertTrue(all_installation.all_installed)
            self.assertEqual(all_installation.source('NVSE/plugins/tnvse_dictionary.xml'),
                             bad / 'tnvse_dictionary.xml')
            selected_installation = nskr.Installation(root)
            self.assertEqual(selected_installation.source('NVSE/plugins/tnvse_dictionary.xml'),
                             good / 'tnvse_dictionary.xml')

            with patch.object(perk, '_source_matches', return_value=(True, 'source_literals_verified')):
                files, status = perk.build_perk_dictionary(all_installation, root / 'stage', set())
            self.assertEqual(len(files), 3)
            self.assertEqual(status['status'], 'generated')
            self.assertEqual(status['source_profile'], 'KR Test')
            result_dir = root / 'stage/mods' / perk.MOD_NAME / 'NVSE/plugins'
            xml = (result_dir / 'tnvse_dictionary.xml').read_text(encoding='utf-8')
            self.assertIn('NSKR_UI_Translations.json', xml)
            self.assertNotIn('first.json', xml)
            self.assertNotIn('second.json', xml)
            self.assertEqual(all_installation.source('NVSE/plugins/tnvse_dictionary.xml'),
                             bad / 'tnvse_dictionary.xml')


if __name__ == '__main__':
    unittest.main()
