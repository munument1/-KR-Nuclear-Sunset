import unittest
from nskr_skill_display import patch_config,BIG_GUNS_DESCRIPTION

class BigGunsConfigTests(unittest.TestCase):
    def test_only_two_display_values_change(self):
        original=(b'[FreeTypeFont]\r\nbEnableFreeTypeFontRendering = 1\r\n'
                  b'[Multibyte]\r\nuiEncoding = 4\r\nbChangeJIPBigGunDesc = 0\r\n'
                  b'sNewBigGunsDesc = ""\r\n[Dictionary]\r\nbUseDictionary = 1\r\n')
        result=patch_config(original)
        expected=original.replace(b'bChangeJIPBigGunDesc = 0',b'bChangeJIPBigGunDesc = 1').replace(
            b'sNewBigGunsDesc = ""',b'sNewBigGunsDesc = "'+BIG_GUNS_DESCRIPTION.encode()+b'"')
        self.assertEqual(result,expected);self.assertEqual(patch_config(result),result)
        self.assertLess(len(BIG_GUNS_DESCRIPTION.encode()),512)

    def test_missing_or_duplicate_values_fail_closed(self):
        with self.assertRaises(ValueError):patch_config(b'[Multibyte]\nbChangeJIPBigGunDesc=0\n')
        with self.assertRaises(ValueError):patch_config(
            b'[Multibyte]\nbChangeJIPBigGunDesc=0\nbChangeJIPBigGunDesc=0\nsNewBigGunsDesc=""\n')
