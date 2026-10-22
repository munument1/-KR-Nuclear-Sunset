"""Read-only MO2 provider probe tests for issue #14."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import nskr
from tools.audit_issue14_mo2_winners import WATCHED, main, summarize


class ProviderSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "MO2"
        profile = self.root / "profiles/Test"
        profile.mkdir(parents=True)
        data = self.root / "Game/Data"
        data.mkdir(parents=True)
        (data / "FalloutNV.esm").write_bytes(b"stock")
        (profile / "modlist.txt").write_text(
            "+Preferred Korean\n+Original Config\n-Korean Perk Runtime Old\n",
            encoding="utf-8")
        (profile / "plugins.txt").write_text("FalloutNV.esm\n", encoding="cp1252")
        (profile / "loadorder.txt").write_text("FalloutNV.esm\n", encoding="utf-8")
        (self.root / "ModOrganizer.ini").write_text(
            "[General]\ngameName=TTW\nselected_profile=Test\ngamePath="
            + str(self.root / "Game") + "\n", encoding="utf-8")
        for mod, data in (("Preferred Korean", b"korean"), ("Original Config", b"original"),
                          ("Korean Perk Runtime Old", b"disabled")):
            target = self.root / "mods" / mod / "NVSE/plugins/tnvse.ini"
            target.parent.mkdir(parents=True)
            target.write_bytes(data)
        levelup = self.root / "mods/Preferred Korean/Menus/levelup_menu.xml"
        levelup.parent.mkdir(parents=True)
        levelup.write_text('<text name="LUM_SelectionText" />', encoding="utf-8")
        src = self.root / "mods/Preferred Korean/NVSE/plugins/scripts/gr_BulletTimePerkDesc.txt"
        src.parent.mkdir(parents=True)
        src.write_bytes(b"guarded source")
        self.inst = nskr.Installation(self.root)

    def test_winner_and_disabled_provider(self):
        result = summarize(self.inst)
        ini = next(e for e in result["watched_paths"]
                   if e["virtual_path"] == "NVSE/plugins/tnvse.ini")
        self.assertEqual(ini["winning_provider_by_offline_priority"], "Preferred Korean")
        self.assertEqual([r["provider"] for r in ini["providers_low_to_high"]],
                         ["Original Config", "Preferred Korean"])
        self.assertEqual(ini["winning_sha256"], hashlib.sha256(b"korean").hexdigest())
        ui = next(e for e in result["watched_paths"]
                  if e["virtual_path"] == "Menus/levelup_menu.xml")
        self.assertEqual(ui["winning_provider_by_offline_priority"], "Preferred Korean")
        self.assertEqual(len(result["watched_paths"]), len(WATCHED))
        self.assertIn("offline_loose_file_provider_precedence_only", result["evidence_scope"])
        self.assertEqual(result["possible_previous_test_mods"], [])

    def test_rejects_aggregate_all_installed_without_selected_profile(self):
        with self.assertRaisesRegex(ValueError, "selected profile"):
            summarize(nskr.Installation(self.root, all_installed=True))

    def test_cli_only_writes_outside_installation_and_never_overwrites(self):
        target = self.base / "snapshot.json"
        args = ["--mo2-root", str(self.root), "--output", str(target)]
        self.assertEqual(main(args), 0)
        result = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(result["profile"], "Test")
        with self.assertRaises(FileExistsError):
            main(args)
        inside = self.root / "unwanted.json"
        with self.assertRaises(SystemExit):
            main(["--mo2-root", str(self.root), "--output", str(inside)])
        self.assertFalse(inside.exists())


if __name__ == "__main__":
    unittest.main()
