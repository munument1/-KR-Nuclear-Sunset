#pragma once

#include "encoding.h"

#include <cstring>
#include <string>
#include <string_view>

namespace fonthook::save_level_tile_fix
{
	struct Probe
	{
		size_t length = 0;
		bool levelPrefix = false;
		bool hasColon = false;
		bool fullUtf8 = false;
		bool suffixUtf8 = false;
		bool suffixConverted = false;
	};

	// The SaveLoadMenu level row is assembled from CP949 UI fragments and
	// sometimes a raw UTF-8 title from the .fos header. This repairs only the
	// byte shape "레벨/Level <digits>: <UTF-8 Hangul>" in that specific row.
	inline bool TryNormalize(const char* raw, std::string& corrected, Probe& probe)
	{
		probe = {};
		if (!raw) return false;
		constexpr size_t kMaximumBytes = 512;
		probe.length = strnlen_s(raw, kMaximumBytes + 1);
		if (probe.length < 11 || probe.length > kMaximumBytes)
			return false;
		const std::string_view text(raw, probe.length);
		probe.hasColon = text.find(':') != std::string_view::npos;
		probe.fullUtf8 = IsValidUTF8With3ByteMin(raw);

		// Three real save-row encodings: a CP949 Korean prefix plus UTF-8
		// title; an ASCII "Level" prefix plus UTF-8 title; or fully UTF-8.
		// The latter two otherwise depend on per-font generic conversion.
		constexpr std::string_view kLevelCp949("\xB7\xB9\xBA\xA7 ", 5);
		constexpr std::string_view kLevelUtf8("\xEB\xA0\x88\xEB\xB2\xA8 ", 7);
		constexpr std::string_view kLevelAscii("Level ", 6);
		size_t pos = 0;
		if (!probe.fullUtf8 && text.substr(0, 5) == kLevelCp949)
			pos = kLevelCp949.size();
		else if (probe.fullUtf8 && text.substr(0, 7) == kLevelUtf8)
			pos = kLevelUtf8.size();
		else if (probe.fullUtf8 && text.substr(0, 6) == kLevelAscii)
			pos = kLevelAscii.size();
		probe.levelPrefix = pos != 0;
		if (!probe.levelPrefix) return false;
		const size_t digitStart = pos;
		while (pos < text.size() && pos - digitStart < 4
			&& text[pos] >= '0' && text[pos] <= '9')
			++pos;
		if (pos == digitStart || pos + 2 >= text.size()
			|| text[pos] != ':' || text[pos + 1] != ' ')
			return false;

		const std::string suffix(text.substr(pos + 2));
		probe.suffixUtf8 = IsValidUTF8With3ByteMin(suffix.c_str());
		if (!probe.suffixUtf8) return false;
		// Restrict the replacement to titles containing Hangul syllables. The
		// strict UTF-8 validator above rejects incomplete or overlong sequences.
		bool hasHangul = false;
		for (size_t i = 0; i + 2 < suffix.size(); ++i)
		{
			const unsigned char a = static_cast<unsigned char>(suffix[i]);
			const unsigned char b = static_cast<unsigned char>(suffix[i + 1]);
			if ((a == 0xEA && b >= 0xB0)
				|| (a >= 0xEB && a <= 0xEC)
				|| (a == 0xED && b <= 0x9E))
			{
				hasHangul = true;
				break;
			}
		}
		if (!hasHangul) return false;

		std::string cp949Converted;
		probe.suffixConverted = TryUTF8ToMultiByteStr(
			probe.fullUtf8 ? text : std::string_view(suffix),
			949, cp949Converted);
		if (!probe.suffixConverted) return false;
		if (probe.fullUtf8)
			corrected = std::move(cp949Converted);
		else
		{
			corrected.assign(text.substr(0, pos + 2));
			corrected.append(cp949Converted);
		}
		if (corrected == text) return false;
		return true;
	}
}
