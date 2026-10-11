from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import nskr_gui


class SelfTestFailureTests(unittest.TestCase):
    def test_cli_failure_records_traceback_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with patch.object(nskr_gui.sys, 'argv', ['patcher', '--self-test', 'MO2']), \
                    patch.object(nskr_gui, 'program_folder', return_value=folder), \
                    patch.object(nskr_gui, 'main', side_effect=ValueError('known UI failure')), \
                    patch.object(nskr_gui.sys, 'stderr', None):
                self.assertEqual(nskr_gui.entrypoint(), 1)
            text = (folder / 'NuclearSunset-self-test.error.log').read_text(encoding='utf-8')
            self.assertIn('ValueError: known UI failure', text)

    def test_cli_success_does_not_create_failure_log(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with patch.object(nskr_gui.sys, 'argv', ['patcher', '--package-check']), \
                    patch.object(nskr_gui, 'program_folder', return_value=folder), \
                    patch.object(nskr_gui, 'main', return_value=0):
                self.assertEqual(nskr_gui.entrypoint(), 0)
            self.assertFalse((folder / 'NuclearSunset-self-test.error.log').exists())


if __name__ == '__main__':
    unittest.main()
