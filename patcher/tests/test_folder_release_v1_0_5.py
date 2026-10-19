import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.build_v1_0_5_folder_release import (
    checked_path, checked_zip, keep_identity, overlay_tree, unpack,
    sync_local_payloads, validate_payloads, verify_previous_destinations,
)


class FolderReleaseV105Tests(unittest.TestCase):
    def catalog(self):
        return {
            "schema_version": 1, "target_modlist": "nuclear-sunset-ttw",
            "version": "1.0.4", "packaging": "folder",
            "font_bundle": {"assets": []},
            "runtime_mods": [],
            "files": [
                {"path": "Plugin.esm", "kind": "plugin-records", "mappings": [
                    {"owner": "plugin.esm", "id": "000001", "signature": "CELL",
                     "field": "FULL", "path": "FULL", "source": "Nipton Sewer",
                     "dest": "닙톤 하수도"},
                ]},
                {"path": "Plugin.esm", "provider": "Second provider",
                 "kind": "plugin-records", "mappings": [
                     {"owner": "plugin.esm", "id": "000001", "signature": "CELL",
                      "field": "FULL", "path": "FULL", "source": "Nipton Sewer",
                      "dest": "닙톤 하수도"},
                 ]},
            ],
        }

    def test_catalog_overlay_retains_duplicates_and_future_translations(self):
        base = self.catalog()
        stage = copy.deepcopy(base)
        for entry in stage["files"]:
            entry["mappings"][0]["dest"] = "닙튼 하수도"
            entry["mappings"][0]["previous_dests"] = ["닙톤 하수도"]
        stage["files"][0]["mappings"].append({
            "owner": "plugin.esm", "id": "000002", "signature": "INFO",
            "field": "NAM1", "path": r"Responses\[0]\NAM1",
            "source": "New Town", "dest": "새 마을"})
        stage["runtime_mods"].append({"mod": "new nvse", "files": []})
        stage.pop("version")
        stage.pop("packaging")
        result = keep_identity(base, stage)
        self.assertEqual(result["version"], "1.0.5")
        self.assertEqual(result["packaging"], "folder")
        self.assertEqual(len(result["files"][0]["mappings"]), 2)
        self.assertEqual(len(result["files"][1]["mappings"]), 1)
        self.assertEqual(result["runtime_mods"][0]["mod"], "new nvse")
        self.assertEqual(verify_previous_destinations(base, result),
                         {"v1_0_4_changed_destinations": 2,
                          "covered_by_previous_dests": 2})

    def test_unchanged_staging_build_adds_strict_historic_upgrade_aliases(self):
        baseline = self.catalog()
        changed = copy.deepcopy(baseline)
        changed["files"][0]["mappings"][0]["dest"] = "닙튼 하수도"
        result = keep_identity(baseline, changed)
        self.assertEqual(result["files"][0]["mappings"][0]["previous_dests"],
                         ["닙톤 하수도"])
        self.assertNotIn("previous_dests", result["files"][1]["mappings"][0])
        self.assertNotIn("previous_dests", changed["files"][0]["mappings"][0])
        self.assertEqual(verify_previous_destinations(baseline, result),
                         {"v1_0_4_changed_destinations": 1,
                          "covered_by_previous_dests": 1})

    def test_bad_historical_tokens_fail_closed(self):
        baseline = self.catalog()
        changed = copy.deepcopy(baseline)
        changed["files"][0]["mappings"][0]["source"] = "Nipton %s"
        baseline["files"][0]["mappings"][0]["source"] = "Nipton %s"
        baseline["files"][0]["mappings"][0]["dest"] = "닙톤 %d"
        changed["files"][0]["mappings"][0]["dest"] = "닙튼 %s"
        with self.assertRaisesRegex(ValueError, "Invalid previous translation"):
            keep_identity(baseline, changed)

    def test_catalog_removal_or_provider_swap_fails(self):
        base = self.catalog()
        dropped = copy.deepcopy(base)
        dropped["files"][1]["mappings"] = []
        with self.assertRaisesRegex(ValueError, "identity removed"):
            keep_identity(base, dropped)
        switched = copy.deepcopy(base)
        switched["files"][1]["provider"] = "Unknown provider"
        with self.assertRaisesRegex(ValueError, "Missing/ambiguous"):
            keep_identity(base, switched)

    def test_zip_extraction_rejects_traversal_symlink_and_duplicates(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            archive = root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../evil.txt", "x")
            with zipfile.ZipFile(archive) as z:
                with self.assertRaises(ValueError):
                    unpack(z, root / "target")
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("TranslationData/X", "one")
                z.writestr("translationdata/x", "two")
            with zipfile.ZipFile(archive) as z:
                with self.assertRaisesRegex(ValueError, "Duplicate"):
                    checked_zip(z)
            with zipfile.ZipFile(archive, "w") as z:
                from zipfile import ZipInfo
                item = ZipInfo("TranslationData/link")
                item.create_system = 3
                item.external_attr = (0o120777 << 16)
                z.writestr(item, "target")
            with zipfile.ZipFile(archive) as z:
                with self.assertRaisesRegex(ValueError, "non-regular"):
                    checked_zip(z)

    def test_overlay_and_payload_hash_guard(self):
        import hashlib
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            package = root / "package"
            overlay = root / "overlay"
            path = overlay / "TranslationData/runtime/New NVSE/nvse/plugins/script.txt"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"new translation")
            names = overlay_tree(package, overlay)
            self.assertEqual(names, ["TranslationData/runtime/New NVSE/nvse/plugins/script.txt"])
            checksum = hashlib.sha256(b"new translation").hexdigest()
            data = self.catalog()
            data["runtime_mods"] = [{
                "mod": "New NVSE", "files": [{
                    "payload": "runtime/New NVSE/nvse/plugins/script.txt",
                    "payload_sha256": checksum}]}]
            self.assertEqual(validate_payloads(package, data), 1)
            path.write_bytes(b"changed")
            overlay_tree(package, overlay)
            with self.assertRaisesRegex(ValueError, "mismatch"):
                validate_payloads(package, data)
            (overlay / "NSKRXEditWorker.exe").write_bytes(b"overwrite")
            with self.assertRaisesRegex(ValueError, "Overlay must live"):
                overlay_tree(package, overlay)

    def test_runtime_payload_auto_sync_is_declared_and_checksum_verified(self):
        import hashlib
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            stage, package = root / "local", root / "package"
            relative = "runtime/My Runtime/NVSE/Plugins/script.txt"
            source = stage / relative
            source.parent.mkdir(parents=True)
            source.write_bytes(b"new NVSE script")
            catalog = self.catalog()
            catalog["runtime_mods"].append({"mod": "My Runtime", "files": [{
                "payload": relative,
                "payload_sha256": hashlib.sha256(b"new NVSE script").hexdigest()}]})
            copied = sync_local_payloads(package, stage, catalog)
            self.assertEqual(copied, ["TranslationData/" + relative])
            self.assertEqual((package / "TranslationData" / relative).read_bytes(),
                             b"new NVSE script")
            self.assertEqual(sync_local_payloads(package, stage, catalog), [])
            source.write_bytes(b"unexpected")
            (package / "TranslationData" / relative).unlink()
            with self.assertRaisesRegex(ValueError, "missing/incorrect"):
                sync_local_payloads(package, stage, catalog)


if __name__ == "__main__":
    unittest.main()
