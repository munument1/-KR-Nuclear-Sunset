import struct,unittest
from nskr_runtime_overrides import compiled_script,loose_edit
from nskr_runtime_override_data import COMPILED


class RuntimeOverrideTests(unittest.TestCase):
    def test_every_reviewed_plan_preserves_bytecode_and_is_idempotent(self):
        for key,plan in COMPILED.items():
            with self.subTest(key=key):
                source=b'\n'.join(b'LNSetName "'+old.encode()+b'" target' for old,new,enc in plan)
                code=b'HEAD'+b''.join(struct.pack('<H',len(old.encode()))+old.encode()+b'CMD' for old,new,enc in plan)
                s,c,changes,error=compiled_script(source,code,plan)
                self.assertIsNone(error)
                self.assertEqual(len(c),len(code))
                at=4
                for old,new,enc in plan:
                    size=len(old.encode())
                    self.assertEqual(c[at:at+2],code[at:at+2])
                    at+=2
                    self.assertEqual(c[at:at+size],new.encode(enc).ljust(size,b' '))
                    at+=size
                    self.assertEqual(c[at:at+3],b'CMD');at+=3
                self.assertEqual(compiled_script(s,c,plan),(s,c,[],None))

    def test_failure_rolls_back_whole_script(self):
        raw=b'LNSetName "A" foo\nLNSetName "B" bar'
        code=b'\1\0A\1\0B'
        self.assertEqual(compiled_script(raw,code,[('A','X','utf-8'),('B','too long','utf-8')])[:3],
                         (raw,code,[]))

    def test_notification_pass_preserves_utf8_companion_names(self):
        import nskr_notifications as notifications
        plan=COMPILED[('jip companions command & control.esp','JIPCCCUIScript')]
        old,new,encoding=plan[3]
        source=b'MessageEx "'+old.encode()+b'" actor'
        code=struct.pack('<H',len(old.encode()))+old.encode()
        s,c,changes,error=compiled_script(source,code,[(old,new,encoding)])
        self.assertIsNone(error)
        preserved=[new for old,new,enc in plan if enc=='utf-8']
        result=notifications.script_edit(s,c,[],preserve_utf8_literals=preserved)
        self.assertEqual(result,(s,c,[],[]))

    def test_identifiers_search_patterns_and_unknown_values_stay(self):
        provider='[ALT] - Misc Items and Crafting Tweaks'
        path='nvse/plugins/scripts/gr_p20MICrecipetincan.txt'
        raw=(b'LNSetName "Unbend Tin Can" (EditorIDToFormID "Unbend Tin Can")\n'
             b'Sv_Replace "Unbend Tin Can" "InternalValue"\n')
        output,changes,issues=loose_edit(raw,provider,path)
        self.assertIn(b'(EditorIDToFormID "Unbend Tin Can")',output)
        self.assertIn(b'Sv_Replace "Unbend Tin Can" "InternalValue"',output)
        self.assertEqual(len(changes),1)
        self.assertFalse(issues)
