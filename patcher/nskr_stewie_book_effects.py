"""Exact Stewie Tweaks skill-book prefix encoding correction (#20).

Stewie's [Book Effects] sPrefix is concatenated with a game skill name.
The v1.0.8 release catalog translates Permanent -> 영구 효과: as UTF-8
while the displayed AVIF/FULL labels are CP949. Fix only this reviewed value.
"""

import re
from pathlib import Path

RELATIVE = 'nvse/plugins/nvse_stewie_tweaks.ini'
SECTION = b'book effects'
KEY = re.compile(rb'^([ \t]*sPrefix[ \t]*=[ \t]*)([^\r\n]*)(\r\n|\n|\r|)$', re.I)
SECTION_LINE = re.compile(rb'^[ \t]*\[([^\]\r\n]+)\][ \t]*(?:[;#][^\r\n]*)?$')
KOREAN = '영구 효과:'
UTF8 = KOREAN.encode('utf-8')
CP949 = KOREAN.encode('cp949')


def edit(raw, *, to_display):
    """Return bytes, changes, review notes; preserve all bytes outside one value."""
    lines = []
    section = None
    matched = 0
    changes = []
    issues = []
    for line in raw.splitlines(keepends=True):
        core = line.rstrip(b'\r\n')
        sec = SECTION_LINE.fullmatch(core)
        if sec:
            section = sec[1].strip().lower()
        if section != SECTION:
            lines.append(line)
            continue
        m = KEY.fullmatch(line)
        if not m:
            lines.append(line)
            continue
        matched += 1
        start, raw_value, ending = m.groups()
        leading = raw_value[:len(raw_value) - len(raw_value.lstrip(b' \t'))]
        trailing = raw_value[len(raw_value.rstrip(b' \t')):]
        token = raw_value.strip(b' \t')
        quote = b'"' if token.startswith(b'"') and token.endswith(b'"') and len(token) >= 2 else b''
        value = token[1:-1] if quote else token
        expected, replacement = (UTF8, CP949) if to_display else (CP949, UTF8)
        if value == expected:
            new_line = start + leading + quote + replacement + quote + trailing + ending
            lines.append(new_line)
            changes.append({'section': 'Book Effects', 'key': 'sPrefix',
                            'from_encoding': 'utf-8' if to_display else 'cp949',
                            'to_encoding': 'cp949' if to_display else 'utf-8'})
        else:
            lines.append(line)
            if value != replacement:
                issues.append({'section': 'Book Effects', 'key': 'sPrefix',
                               'reason': 'unreviewed_prefix_value'})
    if matched > 1:
        raise ValueError('Multiple [Book Effects] sPrefix keys')
    result = b''.join(lines)
    if len(changes) > 1:
        raise ValueError('Ambiguous book prefix edit')
    if changes:
        # Every original non-matching line was copied verbatim above. The only
        # edited bytes are the one reviewed setting's encoded value.
        expected, replacement = (UTF8, CP949) if to_display else (CP949, UTF8)
        if len(result) - len(raw) != len(replacement) - len(expected):
            raise ValueError('Book prefix encoding length invariant failed')
    return result, changes, issues


def normalize_reused_input(raw):
    """Permit a previously patched CP949 sPrefix in otherwise UTF-8 input."""
    try:
        raw.decode('utf-8-sig')
        return raw
    except UnicodeDecodeError:
        result, changes, issues = edit(raw, to_display=False)
        if not changes or issues:
            raise ValueError('Unreviewed Stewie Tweaks INI encoding')
        result.decode('utf-8-sig')  # reject any other mixed/unknown bytes
        return result


def finalize(stage, files):
    import nskr
    for row in files:
        if (row.get('path', '').replace('\\', '/').casefold() != RELATIVE
                or Path(row.get('output_path', '')).suffix.casefold() != '.ini'):
            continue
        target = nskr.contained(stage, row['output_path'])
        before = target.read_bytes()
        output, changes, issues = edit(before, to_display=True)
        if issues:
            row['book_effect_review_notes'] = issues
        if changes:
            if target.read_bytes() != before:
                raise ValueError('Stewie Tweaks output changed during finalization')
            target.write_bytes(output)
            if target.read_bytes() != output:
                raise ValueError('Stewie Tweaks output readback failed')
            row['stewie_book_effects'] = changes
            row['output_sha256'] = nskr.sha256(target)
            row['status'] = row.get('status', '') + '; stewie_book_effect_CP949_verified'
