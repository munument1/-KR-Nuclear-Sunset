import struct,unittest,tempfile
from pathlib import Path
import nskr_notifications as n
from nskr_notification_data import PLAN,INI_TRANSLATIONS

class NotificationTests(unittest.TestCase):
    def test_reviewed_format_and_choices(self):
        for row in PLAN:
            with self.subTest(edid=row['edid'],source=row['old']):
                self.assertEqual(n.args(row['old']),n.args(row['new']))
                self.assertEqual(row['old'].count('|'),row['new'].count('|'))
                self.assertEqual(row['old'].count('^'),row['new'].count('^'))
                row['new'].encode('cp949')

    def test_compiled_printf_operand_and_idempotence(self):
        old='Healing complete for %z: %.0f%%.';new='%z: %.0f%% 치료 완료.'
        literal=old.encode();code=b'OP'+struct.pack('<H',len(literal))+literal+b'END'
        result,ledger,status=n.compiled_edit(code,old,new)
        self.assertEqual(status,'changed');self.assertEqual(len(code),len(result))
        self.assertEqual(result[:4],code[:4]);self.assertTrue(result.endswith(b'END'))
        self.assertIn(new.encode('cp949'),result)
        self.assertEqual(n.compiled_edit(result,new,new),(result,[],'already'))

    def test_actual_newline_compiler_variant(self):
        old='Current value:%r%.2f%%';new='현재:%r%.2f%%'
        literal=old.replace('%r','\n').encode()
        code=struct.pack('<H',len(literal))+literal
        result,_,status=n.compiled_edit(code,old,new)
        self.assertEqual(status,'changed');self.assertIn(b'\n%.2f%%',result)

    def test_wrong_prefix_and_budget_fail_closed(self):
        self.assertEqual(n.compiled_edit(b'XXHi','Hi','안녕')[2],'compiled_literal_not_found')
        code=struct.pack('<H',2)+b'Hi'
        self.assertEqual(n.compiled_edit(code,'Hi','안녕하세요'),(code,[],'over_budget'))

    def test_duplicate_calls_source_and_compiled_sync(self):
        old='You cannot use this in combat!';new='전투 중 사용 불가!'
        literal=old.encode();operand=struct.pack('<H',len(literal))+literal
        code=b'COMMAND'+operand+b'BRANCH'+operand+b'END'
        source=('MessageEx "'+old+'"\r\nMessageBoxEx "'+old+'"\r\n').encode()
        mapping=[{'old':old,'new':new}]
        out,compiled,changes,issues=n.script_edit(source,code,mapping)
        self.assertFalse(issues);self.assertEqual(out.count(new.encode()),2)
        self.assertEqual(compiled.count(new.encode('cp949')),2)
        self.assertEqual(n.script_edit(out,compiled,mapping),(out,compiled,[],[]))

    def test_unreviewed_internal_paths_and_comments_untouched(self):
        raw=b'; MessageEx "Some English text"\nSetEventHandler "Some English text" handler\n'
        self.assertEqual(n.script_edit(raw,b'unchanged',[]),(raw,b'unchanged',[],[]))

    def test_quoted_assignment_scoped_to_reviewed_mapping(self):
        old='|Head:';new='|머리:';literal=old.encode()
        source=b'sDocString = "'+literal+b'" + $health\n'
        code=b'EXPR'+struct.pack('<H',len(literal))+literal+b'END'
        out,compiled,_,errors=n.script_edit(source,code,[{'old':old,'new':new}])
        self.assertFalse(errors);self.assertIn(b' + $health',out)
        self.assertEqual(len(compiled),len(code))

    def test_ini_controls_numbers_and_comments_unchanged(self):
        raw=b';comment\r\n[Controls]\r\nsEnter=enter\r\n[Messages]\r\nsGreeting=Type your guess!\r\n[Settings]\r\niValue=20\r\n'
        out,changes=n.ini_edit(raw,'lang_en.ini',INI_TRANSLATIONS)
        self.assertEqual(len(changes),1)
        self.assertIn(b'sEnter=enter\r\n',out);self.assertIn(b'iValue=20\r\n',out)
        self.assertEqual(n.ini_edit(out,'lang_en.ini',INI_TRANSLATIONS),(out,[]))
        self.assertEqual(n.ini_edit(raw,'unrelated.ini',INI_TRANSLATIONS),(raw,[]))

    def test_conditional_format_tokens_are_not_literal_percent(self):
        self.assertNotEqual(n.args('%{Melee%}%{Ranged%}'),n.args('%%{Melee%%}%%{Ranged%%}'))

    def test_wordle_english_plural_suppressed_without_escape_text(self):
        row=next(x for x in PLAN if x['edid']=='WordleHackLangComputerWhizDescriptionUDF' and x['old']=='es')
        self.assertEqual(row['new'],'')
        code=b'EXPR'+struct.pack('<H',2)+b'es'+b'END'
        result,_,status=n.compiled_edit(code,row['old'],row['new'])
        self.assertEqual(status,'changed');self.assertEqual(result,b'EXPR\x02\x00  END')

    def test_loose_roundtrip_only_known_provider(self):
        row=next(x for x in PLAN if x['signature']=='loose' and any('\uac00'<=c<='\ud7a3' for c in x['new']))
        provider,path=row['file'].split('/',1)
        raw=b'MessageEx "'+row['old'].encode()+b'"\n'
        out,_=n.loose_edit(raw,[row])
        normalized=n.normalize_loose_input(out,provider,path)
        self.assertIn(row['new'].encode('utf-8'),normalized)
        with self.assertRaises(UnicodeDecodeError):n.normalize_loose_input(out,'unreviewed',path)

if __name__=='__main__':unittest.main()
