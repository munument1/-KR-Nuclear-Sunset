from pathlib import Path
import tempfile
import unittest

from nskr import Installation


class LooseScriptInventoryTests(unittest.TestCase):
    def test_geck_sources_and_root_scripts_are_inventory_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('NVSE/user_defined_functions/messages.gek',
                             'scripts/custom.txt', 'meshes/model.gek'):
                file = root / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('MessageEx "A test message"', encoding='utf-8')
            installation = object.__new__(Installation)
            installation.providers = {}
            installation.archives = []
            installation.warnings = []
            installation.add_tree(root, 'Test mod')
            self.assertIn('nvse/user_defined_functions/messages.gek', installation.providers)
            self.assertIn('scripts/custom.txt', installation.providers)
            self.assertNotIn('meshes/model.gek', installation.providers)


if __name__ == '__main__':
    unittest.main()
