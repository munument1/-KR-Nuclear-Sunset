import tempfile,unittest,hashlib
from pathlib import Path
from types import SimpleNamespace
import nskr_runtime_text as r


class RuntimeTextTests(unittest.TestCase):
    def test_punga_setters_preserve_editorids_and_script_logic(self):
        raw=(b'if IsModLoaded "TaleOfTwoWastelands.esm"\r\n'
             b'\tLNSetName "Punga Fruit, Refined" (EditorIDToFormID "DLC04PungaRefined")\r\n'
             b'\tLNSetName "Punga Fruit" (EditorIDToFormID "DLC04PungaWild")\r\nendif\r\n')
        out,changes,issues=r.script_edit(raw,r.NAME_PATH)
        self.assertEqual(len(changes),2)
        self.assertIn('야생 펑가 열매'.encode('cp949'),out)
        self.assertIn('잘 익은 펑가 열매'.encode('cp949'),out)
        for text in (b'IsModLoaded "TaleOfTwoWastelands.esm"',b'"DLC04PungaRefined"',b'"DLC04PungaWild"'):
            self.assertIn(text,out)
        self.assertEqual(out.count(b'\r\n'),raw.count(b'\r\n'))
        second=r.script_edit(out,r.NAME_PATH)
        self.assertEqual(second,(out,[],issues))

    def test_free_travel_setting_preserves_command_and_variable(self):
        raw=b'\tSetStringSetting "sTravelQuestion" "Travel to"\n'
        out,changes,issues=r.script_edit(raw,r.CLICK_PATH)
        self.assertEqual(out,b'\tSetStringSetting "sTravelQuestion" "'+'이동할 장소:'.encode()+b'"\n')
        self.assertEqual(len(changes),1)
        self.assertFalse(issues)
        self.assertEqual(r.script_edit(out,r.CLICK_PATH),(out,[],[]))

    def test_unknown_custom_translation_and_changed_target_are_preserved(self):
        raw=b'SetStringSetting "sTravelQuestion" "My custom travel prompt"\n'
        self.assertEqual(r.script_edit(raw,r.CLICK_PATH)[0],raw)
        self.assertTrue(r.script_edit(raw,r.CLICK_PATH)[2])
        wrong=raw.replace(b'sTravelQuestion',b'sDifferentSetting')
        self.assertEqual(r.script_edit(wrong,r.CLICK_PATH)[0],wrong)
        duplicate=b'SetStringSetting "sTravelQuestion" "Travel to"\n'*2
        self.assertEqual(r.script_edit(duplicate,r.CLICK_PATH)[0],duplicate)

    def test_ini_only_display_values_change_and_quote_style_is_preserved(self):
        raw=(b';comment\r\n[Settings]\r\nbDogmeatFree = 1\r\nfCapPerPound = 0.5\r\n'
             b'sFastTravelMessage = "Hire help for %g caps to travel to" \r\n'
             b'sDogmeatMessage=Have %n take you to\r\n')
        out,changes,issues=r.ini_edit(raw)
        self.assertEqual(len(changes),2)
        self.assertFalse(issues)
        self.assertIn(b'fCapPerPound = 0.5\r\n',out)
        self.assertIn(b'bDogmeatFree = 1\r\n',out)
        self.assertIn(b'sFastTravelMessage = "'+r.MESSAGES['sFastTravelMessage'][1].encode()+b'" \r\n',out)
        self.assertIn(b'sDogmeatMessage='+r.MESSAGES['sDogmeatMessage'][1].encode()+b'\r\n',out)
        self.assertEqual(r.ini_edit(out),(out,[],[]))

    def test_unreviewed_ini_value_and_other_section_are_untouched(self):
        raw=b'[Other]\nsFastTravelMessage = Hire help for %g caps to travel to\n[Settings]\nsDogmeatMessage = Custom %n\n'
        out,changes,issues=r.ini_edit(raw)
        self.assertEqual(out,raw)
        self.assertFalse(changes)
        self.assertEqual(issues[0]['key'],'sDogmeatMessage')

    def test_startup_default_keeps_cached_ini_key_and_path(self):
        raw=(b'Goo1.AuxVarSetStr "*svFastTravelExpensesDogmeatMessage" '
             b'(GetINIString_Cached "Settings:sDogmeatMessage" "Fast Travel Expenses/Fast Travel Expenses.ini" "Have %n take you to")\r\n')
        out,changes,issues=r.script_edit(raw,r.START_PATH)
        self.assertEqual(len(changes),1)
        self.assertIn(b'"Settings:sDogmeatMessage" "Fast Travel Expenses/Fast Travel Expenses.ini"',out)
        self.assertIn(r.MESSAGES['sDogmeatMessage'][1].encode(),out)
        self.assertEqual(r.script_edit(out,r.START_PATH),(out,[],issues))

    def test_finalizer_adds_enabled_source_and_updates_hash_without_live_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);mods=root/'mods';stage=root/'stage'
            path=mods/r.FTE/r.CLICK_PATH;path.parent.mkdir(parents=True)
            raw=b'SetStringSetting "sTravelQuestion" "Travel to"\n';path.write_bytes(raw)
            install=SimpleNamespace(mods=mods,mods_enabled=[r.FTE])
            files=[];r.finalize(install,stage,files)
            self.assertEqual(len(files),1)
            out=(stage/files[0]['output_path']).read_bytes()
            self.assertEqual(files[0]['output_sha256'],hashlib.sha256(out).hexdigest())
            self.assertEqual(path.read_bytes(),raw)
            r.finalize(install,stage,files)
            self.assertEqual((stage/files[0]['output_path']).read_bytes(),out)
            self.assertEqual(r.edit(raw,'Other mod',r.CLICK_PATH),(raw,[],[]))
