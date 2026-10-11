"""Regression tests for synchronizing shared VNV/Nuclear Sunset code."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import sync_vnv_shared_core as shared


class SyncSharedEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.vnv=self.base/"vnv"
        self.ns=self.base/"nuclear"
        self.vnv.mkdir()
        self.ns.mkdir()
        for module in shared.CORE_MODULES:
            content=f'"""VNV test {module}"""\nVALUE = 1\n'
            if module=="xedit":
                content+='import vnvkr\nWORKER="VNVKRXEditWorker.exe"\n'
            if module=="xedit_worker":
                content+='ENV="VNVKR_XEDIT_RUNTIME"\n'
            (self.vnv/f"vnvkr_{module}.py").write_text(content,encoding="utf-8")
            (self.ns/f"nskr_{module}.py").write_text(
                shared.canonical_source(content,module),encoding="utf-8")

    def test_all_shared_modules_identical(self):
        report=shared.run(self.vnv,self.ns,False)
        self.assertEqual(report["identical"],4)
        self.assertEqual(report["out_of_sync"],[])
        self.assertEqual(report["mode"],"CHECK_ONLY")
        self.assertEqual(shared.canonical_source('import vnvkr\n','xedit'),'import nskr\n')
        self.assertEqual(shared.canonical_source('VNVKR_XEDIT_RUNTIME','xedit_worker'),'NSKR_XEDIT_RUNTIME')

    def test_refuse_unsafe_unbacked_overwrite(self):
        edited=self.ns/"nskr_sst.py"
        before=edited.read_bytes()+b"# nuclear-specific change\n"
        edited.write_bytes(before)
        check=shared.run(self.vnv,self.ns,False)
        self.assertEqual(check["out_of_sync"],["sst"])
        with self.assertRaises(RuntimeError):
            shared.run(self.vnv,self.ns,True)
        self.assertEqual(edited.read_bytes(),before)

    def test_apply_requires_clean_backup(self):
        edited=self.ns/"nskr_sst.py"
        before=edited.read_text(encoding="utf-8")+"# local patch\n"
        edited.write_text(before,encoding="utf-8")
        backup=self.base/"backup"
        report=shared.run(self.vnv,self.ns,True,backup)
        self.assertEqual(report["mode"],"APPLIED_WITH_BACKUP")
        self.assertEqual((backup/edited.name).read_text(encoding="utf-8"),before)
        self.assertEqual(edited.read_text(encoding="utf-8"),
                         (self.vnv/"vnvkr_sst.py").read_text(encoding="utf-8"))
        edited.write_text(before,encoding="utf-8")
        with self.assertRaises(FileExistsError):
            shared.run(self.vnv,self.ns,True,backup)

if __name__=="__main__":
    unittest.main()
