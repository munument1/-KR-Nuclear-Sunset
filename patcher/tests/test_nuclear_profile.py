from pathlib import Path
import tempfile,unittest
import nskr,nskr_output
class TTWTests(unittest.TestCase):
    def test_masters(self):
        self.assertIn('fallout3.esm',nskr_output.BASE_TRANSLATION_MASTERS)
        self.assertIn('taleoftwowastelands.esm',nskr_output.BASE_TRANSLATION_MASTERS)
    def test_profile(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'profiles'/'Test').mkdir(parents=True)
            (root/'Game'/'Data').mkdir(parents=True)
            (root/'Game'/'Data'/'FalloutNV.esm').write_bytes(b'')
            (root/'profiles'/'Test'/'modlist.txt').write_text('')
            (root/'profiles'/'Test'/'plugins.txt').write_text('FalloutNV.esm\n')
            (root/'profiles'/'Test'/'loadorder.txt').write_text('FalloutNV.esm\n')
            (root/'ModOrganizer.ini').write_text('[General]\ngameName=TTW\nselected_profile=Test\ngamePath='+str(root/'Game')+'\n[Settings]\nbase_directory='+str(root)+'\n')
            inst=nskr.Installation(root)
            self.assertTrue(inst.is_ttw)
if __name__=='__main__': unittest.main()
