"""Regression coverage for runtime PERK descriptions from Nuclear Sunset #11."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

import nskr
from nskr_nvse import builtin_perk_scripts, merge_script, validate_entry
from nskr_output import build_output


TAG_SOURCE = ('SetFormDescription Tag "The Tag! perk allows you to select a fourth skill to be a '
              'tag skill, which will double the rate at which that skill advances."')


def bullet_time_source(newline='\r\n'):
    return newline.join((
        'array_var aForms',
        'string_var svDescription',
        '',
        'aForms = GLTA 86',
        '    svDescription = Sv_RegexReplace (GetFormDescription rRef) "Bullet Time|VATS|V\\.A\\.T\\.S\\.(?!\\s[A-Z])|V\\.A\\.T\\.S"',
        '    SetFormDescription rRef "%z" svDescription',
        '',
        'aForms = GLTA 98',
        'CallAfter 0 (begin function { array_var aF, int iC}',
        '    svDescription = Sv_RegexReplace (GetFormDescription rR) "Bullet Time|VATS|V\\.A\\.T\\.S\\.(?!\\s[A-Z])|V\\.A\\.T\\.S"',
        '    SetFormDescription rR "%z" svDescription',
        'end) 1 aForms iCount',
        '',
        'svDescription = Sv_RegexReplace (GetFormDescription AVPerception) "Bullet Time|VATS"',
        'SetFormDescription AVPerception "%z" svDescription',
        'Sv_Destruct svDescription',
    ))


class NVSEScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'script.txt'
        self.tag, self.tag_other, self.bullet = builtin_perk_scripts()

    def test_tag_literal_only_changes_and_keeps_quoted_command(self):
        raw = (b'; other comment\r\n' + TAG_SOURCE.encode('ascii') + b'\r\n'
               + b'printf "The Tag! perk allows you to select a fourth skill"\r\n')
        self.source.write_bytes(raw)
        result, stats = merge_script(self.source, self.tag)
        self.assertEqual(stats['translated'], 1)
        self.assertEqual(stats['unmatched'], 0)
        self.assertIn(b'; other comment\r\n', result)
        self.assertIn(b'printf "The Tag! perk allows you to select a fourth skill"\r\n', result)
        self.assertTrue(result.split(b'\r\n')[1].startswith(b'SetFormDescription Tag "'))
        self.assertTrue(result.split(b'\r\n')[1].endswith(b'"'))
        self.assertEqual(self.source.read_bytes(), raw)
        self.source.write_bytes(result)
        same, second = merge_script(self.source, self.tag)
        self.assertEqual(same, result)
        self.assertEqual(second['already_translated'], 1)

    def test_bom_and_utf16_preserved(self):
        for encoding, header, payload in (
                ('utf-8-sig', b'\xef\xbb\xbf', TAG_SOURCE.encode('utf-8')),
                ('utf-16-le', b'\xff\xfe', TAG_SOURCE.encode('utf-16-le'))):
            entry = {**self.tag, 'encoding': encoding}
            self.source.write_bytes(header + payload)
            output, stats = merge_script(self.source, entry)
            self.assertTrue(output.startswith(header))
            self.assertEqual(stats['translated'], 1)
            self.assertEqual(output.decode(encoding if encoding == 'utf-8-sig' else 'utf-16'),
                             'SetFormDescription Tag "' + self.tag['mappings'][0]['dest'] + '"')
        with self.assertRaisesRegex(ValueError, 'encoding changed'):
            merge_script(self.source, self.tag)

    def test_nonmatching_revision_and_invalid_literals_fail_closed(self):
        self.source.write_text(TAG_SOURCE.replace('fourth skill', 'fifth skill'), encoding='utf-8')
        output, stats = merge_script(self.source, self.tag)
        self.assertEqual(output, self.source.read_bytes())
        self.assertEqual(stats['unmatched'], 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            validate_entry({**self.tag, 'mappings': [{**self.tag['mappings'][0],
                                                      'dest': 'invalid " injection'}]})

    def test_bullet_time_is_wrapped_once_and_original_commands_unchanged(self):
        original = bullet_time_source().encode('ascii')
        self.source.write_bytes(original)
        output, report = merge_script(self.source, self.bullet)
        self.assertEqual(report['translated'], 3)
        self.assertEqual(report['unmatched'], 0)
        self.assertEqual(output.count(b'Sv_RegexMatch'), 3)
        self.assertEqual(output.count(b'Sv_RegexReplace'), 3)
        self.assertEqual(output.count(b'SetFormDescription'), 3)
        self.assertEqual(output.count(b'\r\n'), original.count(b'\r\n') + 6)
        for statement in original.split(b'\r\n'):
            if b'Sv_RegexReplace' in statement or b'SetFormDescription' in statement:
                self.assertIn(statement + b'\r\n', output + b'\r\n')
        self.source.write_bytes(output)
        same, reread = merge_script(self.source, self.bullet)
        self.assertEqual(same, output)
        self.assertEqual(reread['already_translated'], 3)
        self.assertEqual(reread['translated'], 0)

    def test_unknown_bullet_revision_is_not_rewritten(self):
        raw = bullet_time_source().replace('aForms = GLTA 98', 'aForms = GLTA 99').encode()
        self.source.write_bytes(raw)
        output, report = merge_script(self.source, self.bullet)
        self.assertEqual(output, raw)
        self.assertEqual(report['unmatched'], 1)

    def test_bullet_time_inline_lambda_respects_512_character_limit(self):
        original = bullet_time_source().replace(
            '    SetFormDescription rR "%z" svDescription\r\n',
            '    SetFormDescription rR "%z" svDescription\r\n' + ('    \r\n' * 90))
        self.source.write_bytes(original.encode('ascii'))
        output, stats = merge_script(self.source, self.bullet)
        self.assertEqual(stats['translated'], 3)
        start = output.index(b'CallAfter 0 (begin function')
        stop = output.index(b'end) 1 aForms iCount') + len(b'end) 1 aForms iCount')
        self.assertLessEqual(stop - start, 512)
        self.assertEqual(output.count(b'SetFormDescription'), 3)

    def test_build_output_preserves_two_distinct_tag_providers(self):
        mo2 = self.root / 'MO2'
        (mo2 / 'Game/Data').mkdir(parents=True)
        for plugin in ('FalloutNV.esm', 'Fallout3.esm', 'TaleOfTwoWastelands.esm'):
            (mo2 / 'Game/Data' / plugin).write_bytes(b'')
        profile = mo2 / 'profiles/Test'
        profile.mkdir(parents=True)
        (mo2 / 'ModOrganizer.ini').write_text(
            '[General]\ngameName=TTW\nselected_profile=Test\ngamePath=' + str(mo2 / 'Game')
            + '\n', encoding='utf-8')
        (profile / 'modlist.txt').write_text(
            '+Tag Perk Description Adjustment\n+SSS - Sweets Simple Settings\n', encoding='utf-8')
        plugins = 'FalloutNV.esm\nFallout3.esm\nTaleOfTwoWastelands.esm\n'
        (profile / 'plugins.txt').write_text(plugins, encoding='cp1252')
        (profile / 'loadorder.txt').write_text(plugins, encoding='utf-8')
        for entry in (self.tag, self.tag_other):
            source = mo2 / 'mods' / entry['provider'] / entry['path']
            source.parent.mkdir(parents=True)
            source.write_bytes(TAG_SOURCE.encode('ascii'))
        catalog = self.root / 'TranslationData'
        catalog.mkdir()
        (catalog / 'catalog.json').write_text(json.dumps({
            'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
            'channel': 'development', 'translation_ready': False,
            'files': [self.tag, self.tag_other],
        }), encoding='utf-8')
        output = self.root / 'Output'
        report = build_output(nskr.Installation(mo2, 'Test'), catalog, output,
                              development=True, scopes={'plugins'})
        self.assertEqual(len(report['files']), 2)
        for entry in (self.tag, self.tag_other):
            target = output / 'mods' / entry['provider'] / entry['path']
            self.assertIn('태그!'.encode('utf-8'), target.read_bytes())
            self.assertEqual((mo2 / 'mods' / entry['provider'] / entry['path']).read_bytes(),
                             TAG_SOURCE.encode('ascii'))
        self.assertEqual(sum(x['translated'] for x in report['files']), 2)


if __name__ == '__main__':
    unittest.main()
