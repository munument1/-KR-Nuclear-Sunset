import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nskr_perk_display as p
from nskr_compiled_scpt import _slots,_decode_record

def sub(k,v): return k+struct.pack('<H',len(v))+v
def record(sig,body): return sig+struct.pack('<5I',len(body),0,0x800,0,0)+body
def plugin(rec): return record(b'TES4',sub(b'HEDR',b'\0'*12))+rec

class PerkDisplayTests(unittest.TestCase):
    def test_every_reviewed_translation_preserves_format_and_fits(self):
        for key,(old,new) in p.REPLACEMENTS.items():
            with self.subTest(key=key):
                self.assertEqual(p.TOKENS.findall(old),p.TOKENS.findall(new))
                self.assertLessEqual(len(new.encode('cp949')),len(old.encode('ascii')))

    def test_mixed_encoding_composition_and_payload_invariant(self):
        text='리볼버를 꺼낸 후 처음 적중시킨 공격입니다.'
        prefix='조건: 레벨 30\n'.encode('cp949')
        with self.assertRaises(UnicodeDecodeError):
            (prefix+text.encode()).decode('utf-8')
        untouched=sub(b'DATA',bytes(range(20)))+sub(b'ICON',b'perk/icon.dds\0')
        raw=plugin(record(b'PERK',sub(b'EDID',b'Target\0')+untouched+sub(b'DESC',text.encode()+b'\0')))
        out,changes=p.patch_bytes(raw,'Vegas Elysium.esp')
        self.assertEqual(len(changes),1)
        self.assertIn(untouched,out)
        self.assertIn(text.encode('cp949')+b'\0',out)
        self.assertEqual((prefix+text.encode('cp949')).decode('cp949'),'조건: 레벨 30\n'+text)
        self.assertEqual(p.patch_bytes(out,'Vegas Elysium.esp'),(out,[]))

    def test_compiled_suffix_preserves_budget_arguments_and_opcodes(self):
        key=('new blood.esp','SCPTNewBloodStartup','PiercingStrike')
        old,new=p.REPLACEMENTS[key];oldb=old.encode()
        code=b'OPCODE'+struct.pack('<H',len(oldb))+oldb+b'NEXTOP'
        sctx=('scn SCPTNewBloodStartup\r\nSetFormDescription PiercingStrike "'+old+'" someVariable\r\n').encode()
        raw=plugin(record(b'SCPT',sub(b'EDID',b'SCPTNewBloodStartup\0')+sub(b'SCHR',struct.pack('<5I',0,0,len(code),0,0))+sub(b'SCDA',code)+sub(b'SCTX',sctx)))
        out,changes=p.patch_bytes(raw,'New Blood.esp')
        self.assertEqual(len(changes),1)
        self.assertIn(b'OPCODE'+struct.pack('<H',len(oldb))+new.encode('cp949'),out)
        self.assertIn(b'NEXTOP',out)
        self.assertIn(new.encode('utf-8'),out)
        self.assertEqual(p.patch_bytes(out,'New Blood.esp'),(out,[]))

    def test_reject_wrong_compiled_length(self):
        old,new=p.REPLACEMENTS[('new blood.esp','SCPTNewBloodStartup','PiercingStrike')]
        code=b'OP'+struct.pack('<H',3)+old.encode()+b'NEXT'
        raw=plugin(record(b'SCPT',sub(b'EDID',b'SCPTNewBloodStartup\0')+sub(b'SCDA',code)+sub(b'SCTX',('SetFormDescription PiercingStrike "'+old+'"').encode())))
        with self.assertRaisesRegex(ValueError,'size prefix'):p.patch_bytes(raw,'New Blood.esp')

    def test_unsupported_character_is_not_replaced(self):
        with self.assertRaises(UnicodeEncodeError):p.display_bytes('한글😀'.encode())

    def test_cp949_dash_equivalent(self):
        self.assertEqual(p.display_bytes('한글—설명'.encode()).decode('cp949'),'한글―설명')

    def test_requirement_labels_skill_names_and_perk_names_match_body_encoding(self):
        pieces=[(b'GMST',b'sRequirementsText','조건',b'DATA'),
                (b'GMST',b'sRanksText','랭크',b'DATA'),
                (b'GMST',b'sLevelAbbrev','레벨',b'DATA'),
                (b'AVIF',b'Sneak','은신',b'FULL'),
                (b'PERK',b'OtherPerk','총기 애호가',b'FULL')]
        result=[]
        for sig,edid,text,key in pieces:
            raw=plugin(record(sig,sub(b'EDID',edid+b'\0')+sub(key,text.encode()+b'\0')))
            out,changes=p.patch_bytes(raw,'NSKR UI Strings.esp')
            self.assertEqual(len(changes),1)
            self.assertIn(text.encode('cp949')+b'\0',out)
            result.append(text.encode('cp949'))
            self.assertEqual(p.patch_bytes(out,'NSKR UI Strings.esp'),(out,[]))
        body='정상 설명'.encode('cp949')
        self.assertEqual((b': '.join(result)+b'\n'+body).decode('cp949'),
                         '조건: 랭크: 레벨: 은신: 총기 애호가\n정상 설명')

    def test_runtime_ui_final_pass_includes_requirement_gmst_and_updates_hash(self):
        import tempfile,hashlib
        from nskr_output import finalize_perk_display
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);target=root/'mods/UI/NSKR UI Strings.esp'
            target.parent.mkdir(parents=True)
            target.write_bytes(plugin(record(b'GMST',sub(b'EDID',b'sRequirementsText\0')+sub(b'DATA','조건'.encode()+b'\0'))))
            rows=[{'output_path':'mods/UI/NSKR UI Strings.esp','status':'runtime_mod_copy','output_sha256':'old'}]
            finalize_perk_display(root,rows)
            self.assertIn('조건'.encode('cp949')+b'\0',target.read_bytes())
            self.assertEqual(rows[0]['output_sha256'],hashlib.sha256(target.read_bytes()).hexdigest())

    def test_restore_concentrated_fire_only_on_exact_identity_and_source(self):
        for filename,(old,new) in p.CONCENTRATED_FIRE.items():
            rec=record(b'PERK',sub(b'EDID',b'ConcentratedFire\0')+sub(b'DESC',old.encode()+b'\0'))
            rec=rec[:12]+struct.pack('<I',0x044CAF)+rec[16:]
            raw=plugin(rec)
            out,changes=p.patch_bytes(raw,filename)
            self.assertEqual(len(changes),1)
            self.assertIn(new.encode('cp949')+b'\0',out)
            self.assertEqual(p.patch_bytes(out,filename),(out,[]))
            wrong=plugin(rec[:12]+struct.pack('<I',0x044CAE)+rec[16:])
            self.assertEqual(p.patch_bytes(wrong,filename),(wrong,[]))

if __name__=='__main__':unittest.main()
