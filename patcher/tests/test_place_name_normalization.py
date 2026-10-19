import copy
from pathlib import Path
import tempfile
import unittest

from tools.normalize_place_names import apply, normalize_catalog, restore


class PlaceNameNormalizationTests(unittest.TestCase):
    def rows(self):
        return {
            "target_modlist": "nuclear-sunset-ttw",
            "files": [
                {"path": "Sample.esm", "kind": "plugin-records", "mappings": [
                    {"owner": "sample.esm", "id": "000001", "signature": "INFO",
                     "field": "NAM1", "path": r"Responses\[0]\NAM1",
                     "source": "Go to New Vegas. <Alias=City>\r\n",
                     "dest": "뉴베가스로 간다. <Alias=City>\r\n", "origin": "gemini_candidate"},
                    {"owner": "sample.esm", "id": "000002", "signature": "CELL",
                     "field": "FULL", "path": "FULL",
                     "source": "Nipton Sewer", "dest": "닙턴 하수도"},
                    {"owner": "sample.esm", "id": "000003", "signature": "CELL",
                     "field": "FULL", "path": "FULL",
                     "source": "Nipton Sewer", "dest": "닙톤 하수도"},
                    {"owner": "sample.esm", "id": "000004", "signature": "MESG",
                     "field": "FULL", "path": "FULL",
                     "source": "Old Mormon Fort", "dest": "올드 몰몬 요새"},
                    {"owner": "sample.esm", "id": "000005", "signature": "REFR",
                     "field": "FULL", "path": r"XMRK\FULL",
                     "source": "Camp Golf", "dest": "골프 캠프"},
                    {"owner": "sample.esm", "id": "000006", "signature": "REFR",
                     "field": "FULL", "path": r"XMRK\FULL",
                     "source": "Other place", "dest": "뉴베가스와 닙턴은 예시"},
                    {"owner": "sample.esm", "id": "000007", "signature": "NOTE",
                     "field": "TNAM", "path": r"TNAM\Text",
                     "source": "Visiting Zion and Silver Rush",
                     "dest": "자이언과 실버 러쉬에 다녀왔다."},
                ]},
                {"path": "MCM/menu.json", "kind": "json", "mappings": [
                    {"source": "Go to New Vegas", "dest": "뉴베가스에 가기"}]},
            ]
        }

    def test_only_whitelisted_plugin_destinations_change(self):
        data = self.rows()
        original = copy.deepcopy(data)
        changes = normalize_catalog(data)
        self.assertEqual(len(changes), 5)
        mapping = data["files"][0]["mappings"]
        self.assertEqual(mapping[0]["dest"], "뉴 베가스로 간다. <Alias=City>\r\n")
        self.assertEqual(mapping[1]["dest"], "닙튼 하수도")
        self.assertEqual(mapping[2]["dest"], "닙튼 하수도")
        self.assertEqual(mapping[3]["dest"], "구 몰몬 요새")
        self.assertEqual(mapping[4]["dest"], "캠프 골프")
        self.assertEqual(mapping[5], original["files"][0]["mappings"][5])
        self.assertEqual(mapping[6], original["files"][0]["mappings"][6])
        self.assertEqual(data["files"][1], original["files"][1])
        for old, new in zip(original["files"][0]["mappings"], mapping):
            self.assertEqual({k: v for k, v in old.items() if k != "dest"},
                             {k: v for k, v in new.items() if k != "dest"})
        self.assertEqual(normalize_catalog(data), [])

    def test_reversible_backup_and_sha_guards(self):
        from tools.normalize_place_names import write_catalog, sha256_file
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            write_catalog(catalog, self.rows())
            before = sha256_file(catalog)
            result = apply(catalog, root / "backups", expected_count=5)
            self.assertEqual(result["status"], "applied")
            self.assertEqual(result["change_count"], 5)
            self.assertEqual(sha256_file(Path(result["backup"])), before)
            self.assertNotEqual(sha256_file(catalog), before)
            self.assertEqual(apply(catalog, root / "backups")["status"],
                             "already_normalized")
            restored = restore(catalog, Path(result["backup"]).parent / "manifest.json")
            self.assertEqual(restored["status"], "restored")
            self.assertEqual(sha256_file(catalog), before)

    def test_refuse_unexpected_target_and_counts(self):
        data = self.rows()
        data["target_modlist"] = "vnv"
        with self.assertRaises(ValueError):
            normalize_catalog(data)
        from tools.normalize_place_names import write_catalog
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "catalog.json"
            write_catalog(target, self.rows())
            with self.assertRaisesRegex(ValueError, "Expected 4"):
                apply(target, root / "backups", expected_count=4)
            self.assertFalse((root / "backups").exists())


if __name__ == "__main__":
    unittest.main()
