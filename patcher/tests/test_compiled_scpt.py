"""Recompiled literal integrity checks, including exact installed-source copies."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from nskr_compiled_scpt import (
    HEADHUNTER_KO, FAST_SUFFIX_KO, _verify_output, translate_compiled_scpt,
)
from tools.audit_issue11_compiled_scripts import CASES, inspect_record


MODS = Path(r'C:\Modlists\NuclearSunset\mods')


def sub(name, data):
    return name.encode('ascii') + struct.pack('<H', len(data)) + data


def rec(name, fid, body, compressed=False):
    flags = 0x40000 if compressed else 0
    payload = struct.pack('<I', len(body)) + zlib.compress(body) if compressed else body
    return struct.pack('<4sIIIII', name.encode('ascii'), len(payload), flags,
                       fid, 0xA5A5A5A5, 0) + payload


def grp(body):
    return b'GRUP' + struct.pack('<I', 24 + len(body)) + b'SCPT' + bytes(range(12)) + body


def mock_plugin(spec, *, compressed=False, broken=False):
    fid = spec['record_formid']
    master_count = fid >> 24
    names = [f'Other{idx}.esm' for idx in range(
        master_count + (spec['record_owner'] != spec['filename']))]
    if spec['record_owner'] != spec['filename']:
        names[-1] = spec['record_owner']
    else:
        # Sweet's form ID 0x12 is its own record after 18 masters.
        names = names[:master_count]
    header = sub('HEDR', bytes(range(12)))
    for name in names:
        header += sub('MAST', name.encode('ascii') + b'\0') + sub('DATA', bytes(8))
    lit = spec['source_en'].encode('ascii')
    bytecode = b'\x15\x99\x10' + struct.pack('<H', len(lit)) + lit + b'\x7f\x08'
    sctx = (b'scriptname ' + spec['editor_id'].encode('ascii') + b'\r\n'
            + b'  SetFormDescription ' + spec['target'].encode('ascii') + b' "'
            + lit + b'"\r\nend\r\n')
    script = (sub('EDID', spec['editor_id'].encode('ascii') + b'\0')
              + sub('SCHR', struct.pack('<5I', 1, 0, len(bytecode) + (1 if broken else 0), 10, 0))
              + sub('SCDA', bytecode) + sub('SCTX', sctx)
              + sub('SLSD', bytes(range(24))))
    untouched = rec('MISC', 0x123, sub('FULL', b'Still original\0'), compressed=True)
    return rec('TES4', 0, header) + grp(grp(rec('SCPT', fid, script, compressed))) + untouched


class CompiledScriptSurgeryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _make(self, spec, *, compressed=False, broken=False):
        source = self.root / spec['filename']
        source.write_bytes(mock_plugin(spec, compressed=compressed, broken=broken))
        target = self.root / 'separate-output' / spec['filename']
        approved = {**spec, 'expected_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        return source, target, approved

    def test_both_reviewed_script_layouts_with_nested_groups(self):
        for spec in CASES:
            with self.subTest(spec=spec['name']):
                source, target, approved = self._make(spec)
                original = source.read_bytes()
                result = translate_compiled_scpt(source, target, approved)
                self.assertEqual(result['status'], 'translated')
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(result['output_sha256'], hashlib.sha256(target.read_bytes()).hexdigest())
                translated = HEADHUNTER_KO.replace('%', '%%') if spec == CASES[0] else '%z' + FAST_SUFFIX_KO
                self.assertIn(translated.encode('utf-8'), target.read_bytes())
                self.assertEqual(result['runtime_validation'], 'not_run')
                self.assertEqual(target.read_bytes().count(b'Still original'), 0)  # compressed and untouched
                source.unlink()
                target.unlink()

    def test_compressed_scpt_and_extra_record_survive(self):
        spec = CASES[1]
        source, target, approved = self._make(spec, compressed=True)
        before = source.read_bytes()
        translate_compiled_scpt(source, target, approved)
        after = target.read_bytes()
        self.assertNotEqual(after, before)
        self.assertEqual(before[-len(rec('MISC', 0x123, sub('FULL', b'Still original\0'), True)):],
                         after[-len(rec('MISC', 0x123, sub('FULL', b'Still original\0'), True)):])
        self.assertEqual(source.read_bytes(), before)

    def test_already_translated_copy_and_explicit_prior_sha(self):
        source, target, spec = self._make(CASES[0])
        first = translate_compiled_scpt(source, target, spec)
        output2 = self.root / 'next-version' / CASES[0]['filename']
        spec2 = {**spec, 'expected_sha256': first['output_sha256']}
        second = translate_compiled_scpt(target, output2, spec2)
        self.assertEqual(second['status'], 'already_translated')
        self.assertEqual(target.read_bytes(), output2.read_bytes())

    def test_source_sha_is_mandatory_and_target_is_exclusive(self):
        source, target, spec = self._make(CASES[1])
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            translate_compiled_scpt(source, target, {**spec, 'expected_sha256': '0' * 64})
        self.assertFalse(target.exists())
        with self.assertRaisesRegex(ValueError, 'distinct'):
            translate_compiled_scpt(source, source, spec)
        target.parent.mkdir(parents=True)
        target.write_bytes(b'do-not-touch')
        with self.assertRaises(FileExistsError):
            translate_compiled_scpt(source, target, spec)
        self.assertEqual(target.read_bytes(), b'do-not-touch')

    def test_fails_closed_on_wrong_compiled_size(self):
        source, target, spec = self._make(CASES[0], broken=True)
        with self.assertRaisesRegex(ValueError, 'compiled size'):
            translate_compiled_scpt(source, target, spec)
        self.assertFalse(target.exists())

    def test_readback_detects_unapproved_changes(self):
        source, target, spec = self._make(CASES[0])
        translate_compiled_scpt(source, target, spec)
        output = target.read_bytes()
        bad = output.replace(b'Other0.esm', b'Other1.esm', 1)
        with self.assertRaisesRegex(ValueError, 'Unrelated record bytes changed'):
            _verify_output(source.read_bytes(), bad, spec['record_formid'],
                           spec['source_en'].encode('ascii'), HEADHUNTER_KO.replace('%', '%%').encode('utf-8'))


class InstalledSourceTests(unittest.TestCase):
    def test_real_installed_plugins_exact_sha_roundtrip(self):
        for spec in CASES:
            with self.subTest(spec=spec['name']):
                source = MODS.joinpath(*spec['relative_plugin'].split('/'))
                if not source.is_file():
                    self.skipTest('Installed Nuclear Sunset originals unavailable')
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), spec['expected_sha256'])
                self.assertTrue(inspect_record(source, spec)['schr_compiled_size_matches_scda'])
                with tempfile.TemporaryDirectory() as temp:
                    target = Path(temp) / spec['filename']
                    report = translate_compiled_scpt(source, target, spec)
                    self.assertEqual(report['status'], 'translated')
                    self.assertNotEqual(target.read_bytes(), source.read_bytes())
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), spec['expected_sha256'])


if __name__ == '__main__':
    unittest.main()
