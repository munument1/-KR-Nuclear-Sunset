"""Runtime text edits must preserve branches, lambdas, formats and source bytes."""
from copy import deepcopy
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import nskr_issue13 as fix
from nskr_nvse import merge_script, validate_entry
from test_compiled_scpt import sub, rec, grp


def fixture():
    row = {'source': '^Title^Original English message.%rPick.|Accept|Reject',
           'dest': '^제목^안내.%r선택.|수락|거부'}
    old = row['source'].replace('%r', '\n').encode()
    dest = row['dest'].replace('%r', '\n').encode()
    a, b = row['dest'].split('|', 1)
    row['dest'] = a + ' ' * (len(old) - len(dest)) + '|' + b
    # Deliberately include opaque branch offsets and a nested lambda sentinel.
    prefix = bytes.fromhex('16000c0001000800') + b'embedded-lambda'
    scda = prefix + struct.pack('<H', len(old)) + old + b'\x19\x00\x10\x00branch'
    sctx = b'begin function {}\r\n MessageBoxEx "' + row['source'].encode() + b'"\r\nend\r\n'
    case = {'plugin': 'Test.esp', 'owner': 'test.esp', 'formid': 0x01000800,
            'edid': 'RuntimePrompt', 'mappings': [row],
            'scda_sha256': fix.digest(scda), 'sctx_sha256': fix.digest(sctx),
            'translated_scda_sha256': fix.digest(scda.replace(old, row['dest'].replace('%r', '\n').encode())),
            'translated_sctx_sha256': fix.digest(sctx.replace(row['source'].encode(), row['dest'].encode()))}
    body = (sub('EDID', b'RuntimePrompt\0')
            + sub('SCHR', struct.pack('<5I', 0, 1, len(scda), 7, 0))
            + sub('SCDA', scda) + sub('SCTX', sctx) + sub('SCRO', b'\x12\x34\x56\x78'))
    plugin = rec('TES4', 0, sub('MAST', b'FalloutNV.esm\0') + sub('DATA', bytes(8)))
    plugin += grp(grp(rec('SCPT', case['formid'], body, compressed=True)))
    plugin += rec('MISC', 123, sub('FULL', b'Untouched\0'))
    return case, body, plugin


class Issue13RuntimeTests(unittest.TestCase):
    def test_dslc_transform_cannot_be_applied_to_other_files(self):
        entry = fix.name_entries()[-1]
        validate_entry(entry)
        for key, value in (('provider', 'Other mod'), ('path', 'nvse/plugins/scripts/gr_DSLC.txt')):
            bad = {**entry, key: value}
            with self.assertRaises(ValueError):
                validate_entry(bad)
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            fix.merge_stat_menu(b'Player.ModAV Health 100\r\n')

    def test_all_reviewed_text_preserves_format_and_compiled_budget(self):
        for case in fix.SCRIPT_CASES:
            for row in case['mappings']:
                old, new = fix.validate_mapping(row)
                self.assertEqual(len(old), len(new))
                if '|' in row['source']:
                    self.assertEqual(row['dest'].split('|')[1:], ['받아들임', '거부'])

    def test_compressed_nested_plugin_preserves_source_and_is_idempotent(self):
        case, _, plugin = fixture()
        with tempfile.TemporaryDirectory() as temp, patch.object(fix, 'SCRIPT_CASES', [case]):
            root = Path(temp)
            source = root / 'Test.esp'
            source.write_bytes(plugin)
            target = root / 'out/Test.esp'
            result = fix.translate_runtime_plugin(source, target)
            self.assertEqual(result['translated'], 1)
            self.assertEqual(source.read_bytes(), plugin)
            second = root / 'again/Test.esp'
            result = fix.translate_runtime_plugin(target, second)
            self.assertEqual(result['already_translated'], 1)
            self.assertEqual(target.read_bytes(), second.read_bytes())
            self.assertTrue(target.read_bytes().endswith(rec('MISC', 123, sub('FULL', b'Untouched\0'))))

    def test_modified_bytecode_with_same_visible_literal_is_rejected(self):
        case, body, _ = fixture()
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            fix._edit_record(body.replace(b'embedded-lambda', b'altered--lambda'), case)

    def test_mixed_source_and_compiled_translation_is_rejected(self):
        case, body, _ = fixture()
        row = case['mappings'][0]
        modified = body.replace(b'"' + row['source'].encode() + b'"', b'"' + row['dest'].encode() + b'"')
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            fix._edit_record(modified, case)

    def test_format_and_button_tampering_rejected(self):
        for replacement in ('other', '|extra', '%z'):
            row = deepcopy(fix.SCRIPT_CASES[0]['mappings'][0])
            row['dest'] += replacement
            with self.assertRaises(ValueError):
                fix.validate_mapping(row)

    def test_unknown_source_never_creates_output(self):
        case, _, plugin = fixture()
        with tempfile.TemporaryDirectory() as temp, patch.object(fix, 'SCRIPT_CASES', [case]):
            source = Path(temp) / 'Test.esp'
            source.write_bytes(plugin)
            target = Path(temp) / 'out.esp'
            bad = deepcopy(case)
            bad['owner'] = 'wrong.esm'
            with patch.object(fix, 'SCRIPT_CASES', [bad]), self.assertRaises(ValueError):
                fix.translate_runtime_plugin(source, target)
            self.assertFalse(target.exists())

    def test_name_operand_only_not_comments_or_form_identifiers(self):
        entry = deepcopy(fix.NAME_ENTRIES[2])
        row = next(r for r in entry['mappings'] if r['source'] == 'Metal Butter Knife')
        entry['mappings'] = [row]
        original = ('; LNSetName "Metal Butter Knife" Knife02\r\n'
                    'LNSetName "Metal Butter Knife" Knife02 ; keep comment\r\n'
                    'LNSetName "Metal Butter Knife" OtherKnife\r\n'
                    'SetFormDescription Knife02 "Metal Butter Knife"\r\n').encode()
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'script.txt'
            source.write_bytes(original)
            raw, stats = merge_script(source, entry)
            self.assertEqual(stats['translated'], 1)
            self.assertEqual(stats['unmatched'], 0)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(raw, original.replace(
                b'LNSetName "Metal Butter Knife" Knife02 ;',
                ('LNSetName "' + row['dest'] + '" Knife02 ;').encode()))
            source.write_bytes(raw)
            same, stats = merge_script(source, entry)
            self.assertEqual(stats['already_translated'], 1)
            self.assertEqual(same, raw)


if __name__ == '__main__':
    unittest.main()
