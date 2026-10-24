import hashlib,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import nskr_runtime_variants as v

class FinalizedIdentityTests(unittest.TestCase):
    def test_both_source_and_bytecode_hash_must_match(self):
        bytecode,source=b'bytecode',b'source'
        pair=tuple(hashlib.sha256(x).hexdigest() for x in (bytecode,source))
        with patch.dict(v.FINALIZED,{'test':pair}):
            self.assertTrue(v.is_reviewed_finalized('test',bytecode,source))
            self.assertFalse(v.is_reviewed_finalized('test',bytecode+b'!',source))
            self.assertFalse(v.is_reviewed_finalized('test',bytecode,source+b'!'))
            self.assertFalse(v.is_reviewed_finalized('other',bytecode,source))

    def test_hash_manifest_has_only_complete_sha256_pairs(self):
        self.assertEqual(len(v.FINALIZED),15)
        for pair in v.FINALIZED.values():
            self.assertEqual(len(pair),2)
            for digest in pair:self.assertRegex(digest,r'^[0-9a-f]{64}$')

    @unittest.skipUnless(Path(r'C:\Modlists\NuclearSunset\mods').is_dir(),'Local finalized installation unavailable')
    def test_finalized_plugins_repeat_without_changing_bytes(self):
        from tools.audit_issue11_compiled_scripts import CASES
        from nskr_compiled_scpt import translate_compiled_scpt
        from nskr_issue13 import translate_runtime_plugin
        root=Path(r'C:\Modlists\NuclearSunset\mods')
        with tempfile.TemporaryDirectory() as tmp:
            for case in CASES:
                source=root/case['relative_plugin'];target=Path(tmp)/source.name
                current=source.read_bytes()
                result=translate_compiled_scpt(source,target,{**case,'expected_sha256':hashlib.sha256(current).hexdigest()})
                self.assertEqual(result['status'],'already_translated')
                self.assertEqual(target.read_bytes(),current)
            providers={p.name.casefold():p for p in root.glob('*/*.esp')}
            for name in ('Vegas Elysium.esp','S6S Base Game Perks Redux.esp'):
                source=providers[name.casefold()];target=Path(tmp)/source.name
                translate_runtime_plugin(source,target)
                self.assertEqual(target.read_bytes(),source.read_bytes())
