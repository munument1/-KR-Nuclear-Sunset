import hashlib
import struct
import unittest

import nskr_dynamic_display as d
import nskr_notifications as n
from test_composed_display import sub,record,plugin


class DynamicDisplayTests(unittest.TestCase):
    def fixture(self):
        source=('scn SCPTOnUseAidAddonMedkit\nstring_var sWho\n'
                'sWho = "당신: "\nMessageEx "%z메드킷이 필요하지 않습니다." sWho\n').encode()
        code=(b'ASSIGN'+struct.pack('<H',7)+'당신: '.encode('cp949')+b' '+
              b'MESSAGE'+struct.pack('<H',30)+'%z메드킷이 필요하지 않습니다.'.encode('cp949')+
              b' '*(30-len('%z메드킷이 필요하지 않습니다.'.encode('cp949')))+b'NEXT')
        return source,code

    def test_utf8_actor_name_and_player_prefix_have_one_encoding(self):
        source,code=self.fixture()
        out_source,out_code,changes,error=d.script_edit(source,code,(d.PLAYER,d.MEDKIT))
        self.assertIsNone(error)
        self.assertEqual(len(code),len(out_code))
        self.assertEqual(len(changes),2)
        self.assertIn('나: '.encode(),out_code)
        self.assertIn('%z치료 불필요.'.encode(),out_code)
        text='%z치료 불필요.'.encode().replace(b'%z','베로니카: '.encode())
        self.assertEqual(text.decode(),'베로니카: 치료 불필요.')
        self.assertEqual(d.script_edit(out_source,out_code,(d.PLAYER,d.MEDKIT)),(out_source,out_code,[],None))

    def test_pipeline_finalizer_can_recover_cp949_intermediate(self):
        source,code=self.fixture()
        s,c,_,error=d.script_edit(source,code,(d.PLAYER,d.MEDKIT))
        self.assertIsNone(error)
        s2,c2,_,issues=n.script_edit(s,c,[],preserve_utf8_literals=[d.PLAYER[1],d.MEDKIT[1]])
        self.assertFalse(issues)
        self.assertEqual(c2,c)
        self.assertEqual(d.script_edit(s2,c2,(d.PLAYER,d.MEDKIT))[:2],(s,c))

    def test_over_budget_leaves_entire_script_unchanged(self):
        source,code=self.fixture()
        result=d.script_edit(source,code,(d.PLAYER,(d.MEDKIT[0],'%z'+'길다'*40)))
        self.assertEqual(result,(source,code,[],'over_budget'))

    def test_wrong_operand_count_and_prefix_fail_closed(self):
        source,code=self.fixture()
        result=d.script_edit(source,code.replace(struct.pack('<H',30),b'\x01\x00'),(d.PLAYER,d.MEDKIT))
        self.assertEqual(result[2:],([],'compiled_literal_count_mismatch'))
        self.assertEqual(result[:2],(source,code.replace(struct.pack('<H',30),b'\x01\x00')))

    def test_arguments_and_menu_structure_cannot_change(self):
        source,code=self.fixture()
        with self.assertRaises(ValueError):d.script_edit(source,code,((d.MEDKIT[0],'치료 불필요.'),))
        with self.assertRaises(ValueError):d.script_edit(source,code,((d.MEDKIT[0],'%z치료|불필요.'),))

    def test_file_hash_gate_and_unrelated_record_preservation(self):
        source,code=self.fixture()
        untouched=sub(b'SCHR',bytes(range(20)))+sub(b'CTDA',bytes(range(28)))
        body=sub(b'EDID',b'SCPTOnUseAidAddonMedkit\0')+untouched+sub(b'SCTX',source)+sub(b'SCDA',code)
        other=record(b'MISC',sub(b'FULL','그대로 보존'.encode()+b'\0'))
        raw=plugin(record(b'SCPT',body)+other)
        denied=d.patch_bytes(raw,'Aid Addon.esp',{})
        self.assertEqual(denied[:2],(raw,[]))
        self.assertEqual(denied[2][0]['reason'],'unreviewed_dynamic_script_hash')
        allowed={'aid addon.esp/SCPTOnUseAidAddonMedkit':[list(d.digest(source,code))]}
        out,changes,issues=d.patch_bytes(raw,'Aid Addon.esp',allowed)
        self.assertFalse(issues)
        self.assertEqual(len(changes),2)
        self.assertIn(untouched,out)
        self.assertTrue(out.endswith(other))
        bad=raw.replace(b'NEXT',b'LAST')
        self.assertEqual(d.patch_bytes(bad,'Aid Addon.esp',allowed)[0],bad)

    def test_all_reviewed_mappings_preserve_format_and_choices(self):
        for key,mappings in d.PLAN.items():
            for old,new in mappings:
                with self.subTest(key=key,old=old):
                    self.assertEqual(n.args(old),n.args(new))
                    self.assertEqual(old.count('|'),new.count('|'))
                    self.assertEqual(old.count('^'),new.count('^'))
