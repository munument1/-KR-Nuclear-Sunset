"""Apply a *fail-closed*, source-pinned candidate for FNV save-menu mixed-encoding titles.

Input is the exactly shipped v1.0.9 tNVSE 71 source:
  Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE/tnvse/Src/font/font_text_geometry.cpp

Do not ship a DLL without compiling, reviewing and validating the output.
This script writes to a NEW path, not to the baseline source.
"""
import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = "214575469b5b6a5bd5a3f8b2de18ab4769e105be3368feb7085254320dcfd824"

INCLUDES = '#include "hook_identity.h"\n#include <algorithm>\n#include <string>\n'
ENTRY = "namespace fonthook\n{\n"
HELPER = r"""
	// FNV 1.4.0.525: read-only ABI prefix of BGSSaveLoadManager and
	// SaveGameData, independently recorded in commonlib_nv.  The tNVSE 71
	// bundled source lacks BGSSaveLoadFile.hpp, so do not include a newer
	// BGSSaveLoadManager.hpp that changes the shipped native build.
	struct SaveTitleDataView
	{
		const char* filename;
		UInt32 unused;
		UInt32 saveNumber;
		const char* playerName;
		const char* playerTitle;
		const char* location;
		const char* playTime;
	};
	struct SaveTitleListNodeView
	{
		SaveTitleDataView item;
		SaveTitleListNodeView* next;
	};
	struct SaveTitleManagerView
	{
		SaveTitleListNodeView* saveList;
		UInt32 saveCount;
	};
	static_assert(sizeof(SaveTitleDataView) == 0x1C);
	static_assert(offsetof(SaveTitleDataView, playerTitle) == 0x10);
	static_assert(sizeof(SaveTitleListNodeView) == 0x20);
	static_assert(sizeof(SaveTitleManagerView) == 0x8);

	// Issue #27: save headers can contain UTF-8 player titles while nearby UI
	// fragments are CP949. Strictly converting the WHOLE mixed string fails.
	// Only convert an exact UTF-8 title present in the current save-list
	// metadata. Never edit the .fos header or the game-managed title pointer.
	static bool ReadBoundedSaveTitle(const char* title, std::string& out)
	{
		out.clear();
		if (!title) return false;
		for (size_t i = 0; i < 160; ++i)
		{
			if (!hook_identity::IsAccessibleRegion(
					reinterpret_cast<SIZE_T>(title + i), 1, false))
				return false;
			if (!title[i]) return !out.empty();
			out.push_back(title[i]);
		}
		out.clear();
		return false;
	}

	static void NormalizeMixedSaveTitleForUi(BSStringT<char>* text)
	{
		if (!text || !text->pString || !g_bEnableUTF8
			|| !g_bEnableMultibyteFontHook || !IsEastAsianUiMode()
			|| g_usingWinEncoding != 949)
			return;
		const size_t length = std::strlen(text->pString);
		if (length < 6 || length > 1024
			|| IsValidUTF8With3ByteMin(text->pString))
			return; // Existing full-UTF-8 renderer handles this.

		// Most UI strings are CP949. Skip costly save-list scans unless
		// the mixed string contains the 3-byte UTF-8 form of a Hangul
		// syllable (U+AC00..D7A3). This check never mutates text.
		bool hasUtf8HangulCandidate = false;
		for (size_t i = 0; i + 2 < length; ++i)
		{
			const UInt8 a = static_cast<UInt8>(text->pString[i]);
			const UInt8 b = static_cast<UInt8>(text->pString[i + 1]);
			const UInt8 c = static_cast<UInt8>(text->pString[i + 2]);
			if (a >= 0xEA && a <= 0xED
				&& (b & 0xC0) == 0x80 && (c & 0xC0) == 0x80)
			{
				hasUtf8HangulCandidate = true;
				break;
			}
		}
		if (!hasUtf8HangulCandidate)
			return;

		constexpr SIZE_T kSaveManagerSingleton = 0x11DE134;
		if (!hook_identity::IsAccessibleRegion(kSaveManagerSingleton,
				sizeof(void*), false))
			return;
		SaveTitleManagerView* manager =
			*reinterpret_cast<SaveTitleManagerView**>(kSaveManagerSingleton);
		if (!manager || !hook_identity::IsAccessibleRegion(
				reinterpret_cast<SIZE_T>(manager), sizeof(*manager), false))
			return;
		auto* node = manager->saveList;
		const UInt32 cap = std::min<UInt32>(manager->saveCount, 256);
		if (!node || !cap) return;

		std::string convertedText(text->pString, length);
		for (UInt32 i = 0; i < cap && node; ++i)
		{
			if (!hook_identity::IsAccessibleRegion(
					reinterpret_cast<SIZE_T>(node), sizeof(*node), false))
				return;
			std::string utf8Title;
			if (ReadBoundedSaveTitle(node->item.playerTitle, utf8Title)
				&& IsValidUTF8With3ByteMin(utf8Title.c_str()))
			{
				const size_t match = convertedText.find(utf8Title);
				if (match != std::string::npos)
				{
					std::string cp949Title;
					if (!TryUTF8ToMultiByteStr(
							utf8Title, g_usingWinEncoding, cp949Title))
						return; // Fail closed: never substitute '?' or best fit.
					convertedText.replace(
						match, utf8Title.size(), cp949Title);
					if (text->Set(convertedText.c_str()))
					{
						static bool logged = false;
						if (!logged)
						{
							gLog.FormattedMessage(
								"tnvse_issue27: save list UTF-8 title fragment normalized to CP949 in UI only");
							logged = true;
						}
					}
					return;
				}
			}
			node = node->next;
		}
	}

"""
CREATE = "\t\t\tconst char* pStr = axTextString->pString;\n\t\t\tstd::string sConvertedStr;"
MAKE = "\t\t\tconst char* pStr = apTextString->pString;\n\t\t\tstd::string sConvertedStr;"


def apply(raw: bytes) -> bytes:
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source SHA mismatch: do not apply to another tNVSE revision")
    decoded = raw.decode("utf-8")
    original_crlf = "\r\n" in decoded
    src = decoded.replace("\r\n", "\n")
    for original in ('#include "native_calls.h"\n', ENTRY, CREATE, MAKE):
        if src.count(original) != 1:
            raise ValueError("Native source structural anchor missing/ambiguous")
    src = src.replace(
        '#include "native_calls.h"\n',
        '#include "native_calls.h"\n' + INCLUDES)
    src = src.replace(ENTRY, ENTRY + HELPER, 1)
    src = src.replace(CREATE,
        "\t\t\tNormalizeMixedSaveTitleForUi(axTextString);\n" + CREATE)
    src = src.replace(MAKE,
        "\t\t\tNormalizeMixedSaveTitleForUi(apTextString);\n" + MAKE)
    assert src.count("NormalizeMixedSaveTitleForUi(") == 3
    return (src.replace("\n", "\r\n") if original_crlf else src).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        raise FileExistsError("Output must be a new path; source is immutable")
    data = apply(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print("source-pinned candidate SHA256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
