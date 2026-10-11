from pathlib import Path
import struct
import tempfile
import unittest

from tools.prepare_nuclear_runtime import write_ui_gmst_plugin
from tools.tes4_text_scan import masters, plugin_records, subrecords


def field(sig, data):
    return sig + struct.pack("<H", len(data)) + data


def record(sig, fid, data):
    return struct.pack("<4sIIIIHH", sig, len(data), 0, fid, 0, 15, 0) + data


def group(sig, data):
    return b"GRUP" + struct.pack("<I", 24 + len(data)) + sig + bytes(12) + data


class RuntimeUiTests(unittest.TestCase):
    def test_gmst_only_preserves_text_and_drops_invalid_radio_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / "Radio UI.esp", root / "NSKR UI Strings.esp"
            head = field(b"HEDR", struct.pack("<fII", 1.34, 4, 0x800))
            head += field(b"MAST", b"FalloutNV.esm\0") + field(b"DATA", bytes(8))
            gmst = record(b"GMST", 0x01000810,
                          field(b"EDID", b"sNewGame\0") + field(b"DATA", "새 게임\0".encode()))
            radio = record(b"INFO", 0x1234, field(b"SCRO", struct.pack("<I", 0x0e001151))
                           + field(b"SCTX", b"unsafe radio script\0"))
            original = record(b"TES4", 0, head) + group(b"GMST", gmst) + group(b"INFO", radio)
            source.write_bytes(original)
            self.assertEqual(write_ui_gmst_plugin(source, target), 1)
            rows = list(plugin_records(target))
            self.assertEqual(rows, [(0x01000810, "GMST",
                                    [("EDID", b"sNewGame\0"), ("DATA", "새 게임\0".encode())])])
            self.assertEqual(masters(target), ["FalloutNV.esm"])
            data = target.read_bytes()
            header_end = 24 + struct.unpack_from("<I", data, 4)[0]
            hedr = next(value for sig, value in subrecords(data[24:header_end]) if sig == "HEDR")
            self.assertEqual(struct.unpack_from("<II", hedr, 4), (2, 0x811))
            self.assertNotIn(b"SCRO", data)
            self.assertNotIn(b"unsafe radio script", data)
            self.assertEqual(source.read_bytes(), original)
            with self.assertRaises(FileExistsError):
                write_ui_gmst_plugin(source, target)
