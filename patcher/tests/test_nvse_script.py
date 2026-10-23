"""Regression coverage for runtime PERK descriptions from Nuclear Sunset #11."""
from pathlib import Path
import hashlib
import json
import re
import tempfile
import unittest

import nskr
from nskr_nvse import builtin_perk_scripts, merge_script, validate_entry
from nskr_output import build_output


TAG_SOURCE = ('SetFormDescription Tag "The Tag! perk allows you to select a fourth skill to be a '
              'tag skill, which will double the rate at which that skill advances."')
ISSUE11_FIXTURES = (Path(__file__).resolve().parents[3] / 'nuclear-sunset'
                    / 'patcher/.local/issue11-nvse-scripts')
ORIGINAL_BULLET_SHA256 = 'd26401da3e60a84d4cfbc6ac1b9382fe5a48dd8c3d7dbab13924fcd3341390f5'


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

    def test_tag_previous_translation_upgrades_in_place(self):
        old = self.tag['mappings'][0]['previous_dests'][0]
        self.source.write_text(f'SetFormDescription Tag "{old}"', encoding='utf-8')
        updated, stats = merge_script(self.source, self.tag)
        self.assertEqual(stats['translated'], 1)
        self.assertEqual(stats['unmatched'], 0)
        self.assertEqual(updated.decode('utf-8'),
                         f'SetFormDescription Tag "{self.tag["mappings"][0]["dest"]}"')

    def test_installed_tag_script_is_exactly_translated_for_both_providers(self):
        for name in ('Tag-SSS.txt', 'Tag-Adjustment.txt'):
            path = ISSUE11_FIXTURES / name
            if not path.is_file():
                self.skipTest('Audited local Nuclear Sunset fixture unavailable')
            raw = path.read_bytes()
            self.assertEqual(raw, TAG_SOURCE.encode('ascii'))
            self.assertEqual(len(raw), 150)
            entry = self.tag if name == 'Tag-SSS.txt' else self.tag_other
            output, stats = merge_script(path, entry)
            self.assertEqual(stats['translated'], 1)
            self.assertEqual(stats['unmatched'], 0)
            self.assertEqual(output,
                             ('SetFormDescription Tag "' + entry['mappings'][0]['dest']
                              + '"').encode('utf-8'))
            self.assertEqual(path.read_bytes(), raw)

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
        self.assertEqual(output.count(b'if eval rRef != "44CAF"'), 0)
        self.assertEqual(output.count(b'if eval rR != "44CAF"'), 0)
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

    def test_bullet_pattern_revision_is_not_rewritten(self):
        for changed in ('Bullet Time|VATS|uncharted',
                        'Bullet Time|VATS|V\\.A\\.T\\.S'):
            raw = bullet_time_source().replace(
                'Bullet Time|VATS|V\\.A\\.T\\.S\\.(?!\\s[A-Z])|V\\.A\\.T\\.S',
                changed).encode('ascii')
            self.source.write_bytes(raw)
            output, report = merge_script(self.source, self.bullet)
            self.assertEqual(output, raw)
            self.assertEqual(report['unmatched'], 1)

    def test_bullet_partial_guard_is_rejected(self):
        self.source.write_bytes(bullet_time_source().encode('ascii'))
        full, _ = merge_script(self.source, self.bullet)
        # A missing guard or a single incomplete pair indicates manual edits.
        for changed in (full.replace(b'    endif\r\n', b'', 1),
                        full.replace(b'if eval Sv_RegexMatch', b'if Sv_RegexMatch', 1)):
            self.source.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, 'Partially guarded'):
                merge_script(self.source, self.bullet)

    def test_previous_known_form_exclusion_is_removed_for_english_perk(self):
        self.source.write_bytes(bullet_time_source().encode('ascii'))
        intended, _ = merge_script(self.source, self.bullet)
        lines = intended.decode('ascii').splitlines(keepends=True)
        for form in ('rRef', 'rR'):
            index = next(i for i, line in enumerate(lines)
                         if line.strip().startswith(f'if eval Sv_RegexMatch (GetFormDescription {form})'))
            indent = lines[index][:len(lines[index]) - len(lines[index].lstrip(' \t'))]
            newline = '\r\n'
            lines.insert(index, indent + f'if eval {form} != "44CAF"' + newline)
            lines.insert(index + 5, indent + 'endif' + newline)
        previous = ''.join(lines).encode('ascii')
        self.source.write_bytes(previous)
        upgraded, report = merge_script(self.source, self.bullet)
        self.assertEqual(report['translated'], 2)
        self.assertEqual(report['already_translated'], 1)
        self.assertEqual(upgraded, intended)
        self.assertEqual(self.source.read_bytes(), previous)

    def test_already_guarded_oversized_lambda_is_rejected(self):
        self.source.write_bytes(bullet_time_source().encode('ascii'))
        full, _ = merge_script(self.source, self.bullet)
        inflated = full.replace(b'CallAfter 0 (begin function',
                                b'CallAfter 0 (begin function' + b' ' * 600)
        self.source.write_bytes(inflated)
        with self.assertRaisesRegex(ValueError, '512-character limit'):
            merge_script(self.source, self.bullet)

    def test_original_1200_byte_bullet_script_keeps_gameplay_operations(self):
        source = ISSUE11_FIXTURES / 'Bullet-PerkDesc.txt'
        if not source.is_file():
            self.skipTest('Audited local Nuclear Sunset fixture unavailable')
        original = source.read_bytes()
        self.assertEqual(len(original), 1200)
        self.assertEqual(hashlib.sha256(original).hexdigest(), ORIGINAL_BULLET_SHA256)
        output, stats = merge_script(source, self.bullet)
        self.assertEqual(stats['translated'], 3)
        self.assertEqual(stats['unmatched'], 0)
        self.assertEqual(output.count(b'if eval Sv_RegexMatch'), 3)
        self.assertEqual(output.count(b'if eval rRef != "44CAF"'), 0)
        self.assertEqual(output.count(b'if eval rR != "44CAF"'), 0)
        self.assertEqual(output.count(b'Sv_RegexReplace'), 3)
        self.assertEqual(output.count(b'SetFormDescription'), 3)
        # Six guard lines are added and four blank lambda lines compacted.
        self.assertEqual(output.count(b'\r\n'), original.count(b'\r\n') + 2)
        self.assertFalse(output.endswith(b'\r\n'))
        self.assertNotIn(b'\n', output.replace(b'\r\n', b''))
        for statement in original.split(b'\r\n'):
            if b'Sv_RegexReplace' in statement or b'SetFormDescription' in statement:
                self.assertIn(statement.lstrip(), output)
        # Lambda whitespace is compacted for the documented 512-char NVSE
        # limit. The tutorial comment is moved just before the lambda; other
        # nonblank, non-guard source lines retain identical tokens and order.
        old_lines = [line.strip() for line in original.decode('ascii').splitlines() if line.strip()]
        new_lines = [line.strip() for line in output.decode('ascii').splitlines() if line.strip()]
        added_line_indices = set()
        for index, line in enumerate(new_lines):
            if line.startswith('if eval Sv_RegexMatch'):
                self.assertEqual(new_lines[index + 3], 'endif')
                added_line_indices.update((index, index + 3))
        self.assertEqual(len(added_line_indices), 6)
        new_surviving = [line for i, line in enumerate(new_lines)
                         if i not in added_line_indices]
        tutorial_comment = ';; Skip the tutorial messages'
        self.assertIn(tutorial_comment, old_lines)
        self.assertIn(tutorial_comment, new_surviving)
        old_lines.remove(tutorial_comment)
        new_surviving.remove(tutorial_comment)
        self.assertEqual(new_surviving, old_lines)
        self.assertIn(b';; Delay second loop to avoid a stutter', output)
        start = output.index(b'CallAfter 0 (begin function')
        stop = output.index(b'end) 1 aForms iCount') + len(b'end) 1 aForms iCount')
        self.assertLessEqual(stop - start, 512)
        self.assertEqual(stop - start, 506)
        pattern = re.search(rb'Sv_RegexMatch .*? "([^"]+)"', output).group(1).decode('ascii')
        self.assertTrue(re.fullmatch(pattern, 'Perk VATS description'))
        self.assertFalse(re.fullmatch(pattern, '집중 사격 V.A.T.S.'))
        # The original input remains untouched; rebuilding on the Output copy
        # must be idempotent without expanding the inline lambda.
        self.assertEqual(source.read_bytes(), original)
        self.source.write_bytes(output)
        replay, replay_stats = merge_script(self.source, self.bullet)
        self.assertEqual(replay, output)
        self.assertEqual(replay_stats['already_translated'], 3)

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
            self.assertIn('태그!'.encode('cp949'), target.read_bytes())
            self.assertEqual((mo2 / 'mods' / entry['provider'] / entry['path']).read_bytes(),
                             TAG_SOURCE.encode('ascii'))
        self.assertEqual(sum(x['translated'] for x in report['files']), 2)


if __name__ == '__main__':
    unittest.main()
