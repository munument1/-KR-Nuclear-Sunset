"""Synthetic, OS-independent regressions for issue #14 read-only PERK audit."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

from tools.audit_issue14_perk_regression import compare, index_perks, main


def perk(*, id="044caf", field="DESC", source="English", dest="한국어", **kwargs):
    return dict(owner="falloutnv.esm", id=id, signature="PERK", field=field,
                path=field, field_occurrence=0, source=source, dest=dest, **kwargs)


def catalog(*entries):
    return dict(schema_version=1, target_modlist="nuclear-sunset-ttw",
                files=[dict(kind="plugin-records", path=plugin, provider=provider,
                            mappings=list(rows)) for plugin, provider, rows in entries])


class PerkAuditTests(unittest.TestCase):
    def test_detects_translation_source_history_addition_and_removal(self):
        prior = catalog(("A.esp", "A", [perk(id="000001", dest="구번역"),
                                       perk(id="000002", source="Old English"),
                                       perk(id="000003", dest="removed"),
                                       perk(id="000004", dest="same")]))
        current = catalog(("A.esp", "A", [perk(id="000001", dest="새번역"),
                                         perk(id="000002", source="New English"),
                                         perk(id="000004", dest="same",
                                              previous_dests=["더 오래된 번역"]),
                                         perk(id="000005", dest="added")]))
        found = {r["formid"]: r for r in compare(prior, current)}
        self.assertEqual(found["000001"]["change"], "translation_changed")
        self.assertEqual(found["000002"]["change"], "source_changed")
        self.assertEqual(found["000003"]["change"], "removed_mapping")
        self.assertEqual(found["000004"]["change"], "history_changed")
        self.assertEqual(found["000005"]["change"], "new_mapping")
        self.assertTrue(all(r["report_status"] == "report_not_provided" for r in found.values()))

    def test_provider_and_occurrence_are_separate(self):
        base = perk(id="000001")
        again = {**base, "field_occurrence": 1, "dest": "다른 한국어"}
        data = catalog(("A.esp", "One", [base, again]),
                       ("A.esp", "Two", [base]))
        self.assertEqual(len(index_perks(data)), 3)
        new = catalog(("A.esp", "One", [{**base, "dest": "개정"}, again]),
                      ("A.esp", "Two", [base]))
        rows = compare(data, new)
        affected = [r for r in rows if r["change"] == "translation_changed"]
        self.assertEqual(len(affected), 1)
        self.assertEqual((affected[0]["provider"], affected[0]["occurrence"]), ("one", 0))

    def test_ambiguous_same_identity_never_silently_merged(self):
        older = catalog(("A.esp", "One", [perk(), perk(dest="중복")]))
        newer = catalog(("A.esp", "One", [perk()]))
        rows = compare(older, newer)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["change"], "ambiguous_duplicate_mapping")

    def test_report_mismatch_is_record_specific(self):
        base = catalog(("FalloutNV.esm", "Fixed ESMs", [perk(),
                                                        perk(id="123456", field="FULL")]))
        unmatched = dict(owner="falloutnv.esm", id="044caf", signature="PERK",
                         field="DESC", path="DESC", field_occurrence=0,
                         reason="source_or_path_mismatch")
        report = dict(files=[dict(path="FalloutNV.esm", provider="Fixed ESMs",
                                  unmatched_entries=[unmatched])], skipped=[])
        found = {r["formid"]: r for r in compare(base, base, report)}
        self.assertEqual(found["044caf"]["report_status"], "mapping_unmatched")
        self.assertEqual(found["044caf"]["notes"], "source_or_path_mismatch")
        self.assertEqual(found["123456"]["report_status"], "plugin_processed_field_unverified")

    def test_english_exception_and_skipped_are_distinct(self):
        base = catalog(("FalloutNV.esm", "Fixed ESMs", [perk()]),
                       ("Other.esp", "Other", [perk(id="004321")]))
        report = dict(
            files=[dict(path="FalloutNV.esm", provider="Fixed ESMs")],
            skipped=[dict(path="Other.esp", provider="Other", reason="not_enabled")],
            english_only_exceptions=[dict(plugin="FalloutNV.esm",
                                          formid="044CAF", field="PERK/DESC")])
        found = {r["plugin"]: r for r in compare(base, base, report)}
        self.assertEqual(found["falloutnv.esm"]["report_status"], "explicit_english_exception")
        self.assertEqual(found["other.esp"]["report_status"], "skipped")

    def test_invalid_catalog_refused(self):
        with self.assertRaisesRegex(ValueError, "Not a Nuclear Sunset"):
            index_perks({"files": []})

    def test_csv_cli_utf8_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            old, new, output = root / "old.json", root / "new.json", root / "audit.csv"
            obj = catalog(("A.esp", "A", [perk()]))
            for path in (old, new):
                path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
            args = ["--previous", str(old), "--current", str(new), "--output", str(output)]
            self.assertEqual(main(args), 0)
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["current_dest"], "한국어")
            self.assertEqual(rows[0]["change"], "unchanged")
            with self.assertRaises(FileExistsError):
                main(args)


if __name__ == "__main__":
    unittest.main()
