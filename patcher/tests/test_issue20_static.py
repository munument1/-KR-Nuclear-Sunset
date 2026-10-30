import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import audit_issue20_static as a


class Issue20StaticAuditTests(unittest.TestCase):
    def test_report_classifies_notes_without_inventing_game_pass(self):
        report = {"files": [
            {"output_path": "mods/NS/NS.esp",
             "composition_review_notes": [{"reason": "unsupported_cp949", "form": "00123456"}],
             "unmatched": 2, "unmatched_entries": [{"source": "English", "reason": "unmatched"}]},
            {"path": "another.esp", "unmatched": 1}],
            "skipped": [{"path": "old.esp", "reason": "updated_plugin_needs_record_backend"}]}
        result = a.audit(report)
        self.assertEqual(result["game_validation"], "not_run")
        self.assertEqual(result["report_review_count"], 4)
        self.assertEqual(set(row["layer"] for row in result["report_findings"]),
                         {"composition_review_notes", "unmatched_entries",
                          "unmatched_without_details", "skipped"})

    def test_contextual_catalog_variants_not_auto_rewritten(self):
        source = {"files": [
            {"path": "NS.esp", "mappings": [
                {"owner": "NS.esm", "id": "123", "source": "Casing", "dest": "탄피"},
                {"owner": "NS.esm", "id": "124", "source": "Casing.", "dest": "탄피."},
                {"owner": "NS.esm", "id": "125", "source": "Full sentence.", "dest": "탄피."},
            ]}
        ]}
        result = a.audit({"files": []}, [("catalog.json", source)])
        self.assertEqual(result["variant_candidates"]["탄피"]["forms"], ["탄피", "탄피."])
        self.assertEqual(result["variant_candidates"]["탄피"]["entries"][0]["context"]["id"], "123")
        self.assertEqual(source["files"][0]["mappings"][1]["dest"], "탄피.")

    def test_zip_and_directory_same_mappings_and_inputs_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "TranslationData"
            data.mkdir()
            content = {"files": [{"mappings": [{"source": "Casing", "dest": "탄피."}]}]}
            (data / "catalog.json").write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
            (data / "runtime_ui").mkdir()
            ui = [{"original": "Shell casing", "translation": "탄피"}]
            (data / "runtime_ui" / "NSKR_UI_Translations.json").write_text(
                json.dumps(ui, ensure_ascii=False), encoding="utf-8")
            archive = root / "release.zip"
            with zipfile.ZipFile(archive, "w") as z:
                for file in data.rglob("*.json"):
                    z.write(file, "TranslationData/" + file.relative_to(data).as_posix())
            direct = a.audit({"files": []}, a.catalog_documents(data))
            zipped = a.audit({"files": []}, a.catalog_documents(archive))
            self.assertEqual(direct["translation_hits"]["탄피"], [
                dict(entry, document=entry["document"].replace("TranslationData/", "")) for
                entry in zipped["translation_hits"]["탄피"]])
            self.assertEqual(len(direct["translation_hits"]["탄피"]), 2)
            out = root / "result.json"
            report = root / "report.json"
            report.write_text('{"files":[]}', encoding="utf-8")
            a.main(["--report", str(report), "--data", str(data), "--output", str(out)])
            with self.assertRaises(FileExistsError):
                a.main(["--report", str(report), "--data", str(data), "--output", str(out)])
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["game_validation"], "not_run")

    def test_bad_report_fails_closed(self):
        with self.assertRaises(ValueError):
            a.audit({"skipped": []})
        with self.assertRaises(ValueError):
            a.audit({"files": [{"notification_review_notes": "unexpected"}]})


if __name__ == "__main__":
    unittest.main()
