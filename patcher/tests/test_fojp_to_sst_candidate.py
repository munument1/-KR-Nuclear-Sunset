"""Smoke-test the conservative FOJP pairing and candidate writer without game files."""
from pathlib import Path
import importlib.util,struct,sys,tempfile,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from tools.fojp_to_sst_candidate import discover_fojp_pairs,load_fojp_dictionary,match_plugin,write_sst
from nskr_sst import read_sst
class FoJpTest(unittest.TestCase):
    def test_synthetic_pair_and_sst(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            source=p/"extracted";source.mkdir()
            (source/"dialog_en.txt").write_text("Original conversation\nSame phrase\n",encoding="utf-8")
            (source/"dialog_ko.txt").write_text("원문 대화입니다\n같은 구절입니다\n",encoding="utf-8")
            pairs=discover_fojp_pairs(source)
            self.assertEqual(len(pairs),1)
            mapping,stats,files=load_fojp_dictionary(pairs)
            self.assertEqual(len(mapping),2)
            # Minimal TES4 game record with one plain English INFO/NAM1.
            plugin=p/"Example.esp"
            value=b"Original conversation\x00"
            sub=b"NAM1"+struct.pack("<H",len(value))+value
            record=b"INFO"+struct.pack("<I",len(sub))+struct.pack("<I",0)+struct.pack("<I",0x00000123)+b"\0"*8+sub
            plugin.write_bytes(b"TES4"+struct.pack("<I",0)+b"\0"*16+record)
            rows,counts,_,_=match_plugin(plugin,mapping,False)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["dest"],"원문 대화입니다")
            out=p/"Example_en_ko.sst"
            write_sst(out,[],rows)
            restored=read_sst(out)
            self.assertEqual(len(restored.entries),1)
            self.assertEqual(restored.entries[0].form_id,0x00000123)
    def test_conflicting_source_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/"a_en.txt").write_text("Duplicate\n",encoding="utf-8")
            (p/"a_ko.txt").write_text("번역 하나\n",encoding="utf-8")
            (p/"b_en.txt").write_text("Duplicate\n",encoding="utf-8")
            (p/"b_ko.txt").write_text("번역 둘\n",encoding="utf-8")
            mapping,stats,_=load_fojp_dictionary(discover_fojp_pairs(p))
            self.assertNotIn("Duplicate",mapping)
            self.assertEqual(stats["ambiguous_english_sources"],1)
if __name__=="__main__":unittest.main()
