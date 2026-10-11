"""Extend the existing VNV source-function regression with quote-byte coverage."""
import argparse
from pathlib import Path
import runpy


def generate(source, vnv_regression, output):
    existing = runpy.run_path(str(vnv_regression))
    existing["generate"](source, output)
    hooks = (source / "tnvse/Src/font/text_hooks.cpp").read_text(encoding="utf-8-sig")
    function = existing["between"](
        hooks, "\tvoid __cdecl NormalizeSingleByteQuotes", "\tchar* __fastcall BSString_c_strHook")
    code = output.read_text(encoding="utf-8")
    checks = r'''
bool g_bEnableMultibyteFontHook = true;
''' + function + r'''
void CheckNoteQuoteBytes() {
    // This exhaustively verifies the observed retail Windows-1252 mapping.
    g_bEnableMultibyteFontHook = false;
    for (unsigned int i = 0; i < 256; ++i) {
        char value = static_cast<char>(i);
        NormalizeSingleByteQuotes(&value);
        unsigned int expected = (i == 0x91 || i == 0x92) ? 0x27 :
            (i == 0x93 || i == 0x94) ? 0x22 : i;
        assert(static_cast<unsigned char>(value) == expected);
    }
    // Korean mode must preserve every encoded byte, including 91-94.
    g_bEnableMultibyteFontHook = true;
    for (unsigned int i = 0; i < 256; ++i) {
        char value = static_cast<char>(i);
        NormalizeSingleByteQuotes(&value);
        assert(static_cast<unsigned char>(value) == i);
    }
    const std::string note = "작업대에서 다음을 조합하세요:";
    std::string preserved = note;
    for (char& value : preserved) NormalizeSingleByteQuotes(&value);
    assert(preserved == note && IsValidUTF8With3ByteMin(preserved.c_str()));
    // Independent CP949 bytes for '요' from the Windows-949 encoding table.
    assert(UTF8ToMultiByteStr("요", 949) == std::string("\xBF\xE4", 2));
    const std::string korean = UTF8ToMultiByteStr(note, 949);
    preserved = korean;
    for (char& value : preserved) NormalizeSingleByteQuotes(&value);
    assert(preserved == korean);
    std::cout << "note quote regression: 256 retail bytes, 256 DBCS bytes, UTF8 and CP949 passed\n";
}
'''
    code = code.replace("int main() {", checks + "\nint main() {\nCheckNoteQuoteBytes();", 1)
    output.write_text(code, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("vnv_regression", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    generate(args.source, args.vnv_regression, args.output)
