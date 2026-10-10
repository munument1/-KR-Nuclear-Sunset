from pathlib import Path
import tempfile, unittest
from tools.extract_thepitt_sst import write_sst
from nskr_sst import read_sst

class SSTOwnerRoundtrip(unittest.TestCase):
    def test_master_and_own_record_owners_are_distinct(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"Example_en_ko.sst"
            rows=[
                {"owner":"falloutnv.esm","id":"012345","signature":"NPC_","field":"FULL",
                 "source":"Test Name","dest":"시험 인물","rec_id":0,"rec_id_max":1,"string_id":0},
                {"owner":"example.esp","id":"067890","signature":"INFO","field":"NAM1",
                 "source":"Good morning","dest":"좋은 아침","rec_id":0,"rec_id_max":1,"string_id":0}
            ]
            write_sst(out,["FalloutNV.esm"],rows,target_name="Example.esp")
            restored=read_sst(out)
            self.assertEqual(len(restored.entries),2)
            self.assertEqual(restored.entries[0].form_id,0x00012345)
            self.assertEqual(restored.entries[1].form_id,0x01067890)
            self.assertEqual(restored.entries[0].dest,"시험 인물")
            self.assertEqual(restored.entries[1].dest,"좋은 아침")
if __name__=="__main__":unittest.main()
