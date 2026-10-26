#include "encoding.h"
#include "font_multibyte_prewarm_policy.h"
#include "load_config.h"
#include "IDebugLog.h"
#include <atomic>
#include <limits>

namespace fonthook
{
	bool IsDbcsCodePage(UInt32 codePage)
	{
		return multibyte_prewarm::IsDbcsCodePage(codePage);
	}

	bool IsEastAsianUiMode()
	{
		return g_uiEncoding >= 1 && g_uiEncoding <= 4;
	}

	bool UsesDbcsTextLayout()
	{
		return g_bEnableMultibyteFontHook && IsDbcsCodePage(g_usingWinEncoding);
	}

	UInt32 GetFreeTypeTextCodePage()
	{
		if (UsesDbcsTextLayout())
			return g_usingWinEncoding;

		if (g_usingWinEncoding == kWindows1251CodePage)
			return kWindows1251CodePage;

		return kWindows1252CodePage;
	}

	// ===================== GBK (Code Page 936) =====================
	bool IsGBKLeadByte(UInt8 c)
	{
		return multibyte_prewarm::IsLeadByte(
			multibyte_prewarm::kCodePageGbk, c);
	}

	bool IsGBKTrailByte(UInt8 c)
	{
		return multibyte_prewarm::IsTrailByte(
			multibyte_prewarm::kCodePageGbk, c);
	}

	bool TryDecodeGBK(const char* p, UInt32& outCode)
	{
		UInt8 lead = (UInt8)p[0];
		UInt8 trail = (UInt8)p[1];
		if (!IsGBKLeadByte(lead) || !IsGBKTrailByte(trail))
			return false;
		outCode = (UInt32(lead) << 8) | UInt32(trail);
		return true;
	}

	// ===================== Big5 (Code Page 950) =====================
	bool IsBig5LeadByte(UInt8 c)
	{
		return multibyte_prewarm::IsLeadByte(
			multibyte_prewarm::kCodePageBig5, c);
	}

	bool IsBig5TrailByte(UInt8 c)
	{
		return multibyte_prewarm::IsTrailByte(
			multibyte_prewarm::kCodePageBig5, c);
	}

	bool TryDecodeBig5(const char* p, UInt32& outCode)
	{
		UInt8 lead = (UInt8)p[0];
		UInt8 trail = (UInt8)p[1];
		if (!IsBig5LeadByte(lead) || !IsBig5TrailByte(trail))
			return false;
		outCode = (UInt32(lead) << 8) | UInt32(trail);
		return true;
	}

	// ===================== Shift-JIS (Code Page 932) =====================
	bool IsSJISLeadByte(UInt8 c)
	{
		return multibyte_prewarm::IsLeadByte(
			multibyte_prewarm::kCodePageShiftJis, c);
	}

	bool IsSJISTrailByte(UInt8 c)
	{
		return multibyte_prewarm::IsTrailByte(
			multibyte_prewarm::kCodePageShiftJis, c);
	}

	bool TryDecodeSJIS(const char* p, UInt32& outCode)
	{
		UInt8 lead = (UInt8)p[0];
		UInt8 trail = (UInt8)p[1];
		if (!IsSJISLeadByte(lead) || !IsSJISTrailByte(trail))
			return false;
		outCode = (UInt32(lead) << 8) | UInt32(trail);
		return true;
	}

	// ===================== Korean/UHC (Code Page 949) =====================
	bool IsKoreanLeadByte(UInt8 c)
	{
		return multibyte_prewarm::IsLeadByte(
			multibyte_prewarm::kCodePageUhc, c);
	}

	bool IsKoreanTrailByte(UInt8 c)
	{
		return multibyte_prewarm::IsTrailByte(
			multibyte_prewarm::kCodePageUhc, c);
	}

	bool TryDecodeKorean(const char* p, UInt32& outCode)
	{
		UInt8 lead = (UInt8)p[0];
		UInt8 trail = (UInt8)p[1];
		if (!IsKoreanLeadByte(lead) || !IsKoreanTrailByte(trail))
			return false;
		outCode = (UInt32(lead) << 8) | UInt32(trail);
		return true;
	}

	bool TryDecodeDoubleByteForCodePage(
		const char* p, UInt32 codePage, UInt32& outCode)
	{
		if (!p || static_cast<UInt8>(p[0]) < 0x80 || !p[1])
			return false;
		switch (codePage)
		{
		case 936: return TryDecodeGBK(p, outCode);
		case 950: return TryDecodeBig5(p, outCode);
		case 932: return TryDecodeSJIS(p, outCode);
		case 949: return TryDecodeKorean(p, outCode);
		default: return false;
		}
	}

	bool TryDecodeFreeTypeDoubleByte(const char* p, UInt32& outCode)
	{
		return TryDecodeDoubleByteForCodePage(
			p, GetFreeTypeTextCodePage(), outCode);
	}

	// ===================== UTF-8 =====================
	bool IsValidUTF8With3ByteMin(const char* s)
    {
        if (!s) return false;
        const UInt8* p = reinterpret_cast<const UInt8*>(s);
        bool has3ByteOrMore = false;
        while (*p)
        {
            const UInt8 first = *p++;
            if (first < 0x80) continue;
            if (first >= 0xC2 && first <= 0xDF)
            {
                if (!p[0] || (p[0] & 0xC0) != 0x80) return false;
                ++p;
            }
            else if (first >= 0xE0 && first <= 0xEF)
            {
                if (!p[0] || !p[1]) return false;
                const UInt8 second = p[0], third = p[1];
                if ((second & 0xC0) != 0x80 || (third & 0xC0) != 0x80
                    || (first == 0xE0 && second < 0xA0)
                    || (first == 0xED && second >= 0xA0)) return false;
                p += 2;
                has3ByteOrMore = true;
            }
            else if (first >= 0xF0 && first <= 0xF4)
            {
                if (!p[0] || !p[1] || !p[2]) return false;
                const UInt8 second = p[0];
                if ((second & 0xC0) != 0x80 || (p[1] & 0xC0) != 0x80
                    || (p[2] & 0xC0) != 0x80
                    || (first == 0xF0 && second < 0x90)
                    || (first == 0xF4 && second > 0x8F)) return false;
                p += 3;
                has3ByteOrMore = true;
            }
            else return false;
        }
        // Retain the legacy two-byte-only heuristic: byte provenance is
        // ambiguous for existing DBCS strings. Do not guess new encodings.
        return has3ByteOrMore;
    }

	// ===================== Encoding Conversion =====================
	namespace
    {
        void TraceEncodingConversionFailure(const char* reason, UInt32 codePage, size_t bytes)
        {
            static std::atomic<unsigned> remaining{8};
            unsigned count = remaining.load(std::memory_order_relaxed);
            while (count && !remaining.compare_exchange_weak(
                count, count - 1, std::memory_order_relaxed)) {}
            if (count)
                gLog.FormattedMessage(
                    "tnvse_encoding_boundary: conversion_skipped reason=%s codePage=%u bytes=%u",
                    reason, codePage, static_cast<unsigned>(bytes));
        }
    }

    bool TryUTF8ToMultiByteStr(std::string_view utf8, UInt32 codePage, std::string& converted)
    {
        if (utf8.empty()) { converted.clear(); return true; }
        if (utf8.size() > static_cast<size_t>(std::numeric_limits<int>::max())) return false;
        const int inputBytes = static_cast<int>(utf8.size());
        const int wideCount = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
            utf8.data(), inputBytes, nullptr, 0);
        if (!wideCount)
        {
            TraceEncodingConversionFailure("invalid_utf8", codePage, utf8.size());
            return false;
        }
        std::wstring wide(static_cast<size_t>(wideCount), L'\0');
        if (MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
            utf8.data(), inputBytes, wide.data(), wideCount) != wideCount) return false;
        // Reviewed display-equivalent mapping already used by the Korean
        // patcher. Avoid Windows best-fit while retaining these two targets.
        if (codePage == 949)
            for (wchar_t& unit : wide)
                if (unit == 0x2014) unit = 0x2015;
        const bool outputUtf8 = codePage == CP_UTF8;
        const DWORD flags = outputUtf8 ? WC_ERR_INVALID_CHARS : WC_NO_BEST_FIT_CHARS;
        BOOL usedDefault = FALSE;
        BOOL* defaultFlag = outputUtf8 ? nullptr : &usedDefault;
        const int count = WideCharToMultiByte(codePage, flags,
            wide.data(), wideCount, nullptr, 0, nullptr, defaultFlag);
        if (!count || usedDefault)
        {
            TraceEncodingConversionFailure("unrepresentable", codePage, utf8.size());
            return false;
        }
        std::string result(static_cast<size_t>(count), '\0');
        usedDefault = FALSE;
        if (WideCharToMultiByte(codePage, flags, wide.data(), wideCount,
            result.data(), count, nullptr, defaultFlag) != count || usedDefault)
        {
            TraceEncodingConversionFailure("unrepresentable", codePage, utf8.size());
            return false;
        }
        // Check Unicode roundtrip as well as Windows' default-character flag.
        const int checkCount = MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS,
            result.data(), count, nullptr, 0);
        if (checkCount != wideCount)
        {
            TraceEncodingConversionFailure("roundtrip", codePage, utf8.size());
            return false;
        }
        std::wstring check(static_cast<size_t>(checkCount), L'\0');
        if (MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS,
            result.data(), count, check.data(), checkCount) != checkCount || check != wide)
        {
            TraceEncodingConversionFailure("roundtrip", codePage, utf8.size());
            return false;
        }
        converted.swap(result);
        return true;
    }

    std::string UTF8ToMultiByteStr(const std::string& utf8, UInt32 codePage)
    {
        std::string converted;
        return TryUTF8ToMultiByteStr(utf8, codePage, converted) ? converted : utf8;
    }

	std::string WideToUTF8(std::wstring_view value)
	{
		if (value.empty())
			return {};

		const int encodedByteCount = WideCharToMultiByte(
			CP_UTF8,
			0,
			value.data(),
			static_cast<int>(value.size()),
			nullptr,
			0,
			nullptr,
			nullptr);

		if (encodedByteCount <= 0)
			return {};

		std::string utf8(static_cast<size_t>(encodedByteCount), '\0');

		const int written = WideCharToMultiByte(
			CP_UTF8,
			0,
			value.data(),
			static_cast<int>(value.size()),
			utf8.data(),
			encodedByteCount,
			nullptr,
			nullptr);

		if (written <= 0)
			return {};

		return utf8;
	}

} // namespace fonthook

// ---- Unified encoding dispatch ----
// These functions use the configured UI code page. FreeType-only code uses
// TryDecodeFreeTypeDoubleByte so its resource identity remains Windows-1252.
// They replace the repeated if/else-if chains scattered across the codebase.

namespace fonthook
{

	bool IsLeadByte(UInt8 c)
	{
		if (c < 0x80) return false;  // ASCII fast-path
		switch (g_usingWinEncoding)
		{
		case 936:  return IsGBKLeadByte(c);
		case 950:  return IsBig5LeadByte(c);
		case 932:  return IsSJISLeadByte(c);
		case 949:  return IsKoreanLeadByte(c);
		default:   return false;
		}
	}

	bool IsTrailByte(UInt8 c)
	{
		// DBCS trail bytes may be in the ASCII range, e.g. GBK/Big5/SJIS 0x40-0x7E.
		switch (g_usingWinEncoding)
		{
		case 936:  return IsGBKTrailByte(c);
		case 950:  return IsBig5TrailByte(c);
		case 932:  return IsSJISTrailByte(c);
		case 949:  return IsKoreanTrailByte(c);
		default:   return false;
		}
	}

	bool TryDecodeDoubleByte(const char* p, UInt32& outCode)
	{
		return TryDecodeDoubleByteForCodePage(p, g_usingWinEncoding, outCode);
	}

} // namespace fonthook
