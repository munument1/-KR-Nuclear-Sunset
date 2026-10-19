"""Conservative literal translations of loose NVSE script descriptions.

No script is executed or recompiled. Only the quoted argument of an exact
``SetFormDescription <form> "text"`` statement can change, with the original
command, comments and line endings retained byte-for-byte.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from tools.loose_translation import TOKEN


STATEMENT = re.compile(
    r'^(?P<prefix>[ \t]*SetFormDescription[ \t]+(?P<form>[^\s";]+)[ \t]+")'
    r'(?P<value>(?:\\.|[^"\\\r\n])*)'
    r'(?P<suffix>"[ \t]*(?:(?:;|//).*|)(?:\r\n|\n|\r|))$', re.IGNORECASE)
SCRIPT_PREFIX = 'nvse/plugins/scripts/'
REGEX_REWRITE = re.compile(
    r'^(?P<indent>[ \t]*)svDescription\s*=\s*Sv_RegexReplace\s*'
    r'\(GetFormDescription\s+(?P<form>rRef|rR|AVPerception)\)\s*'
    r'"Bullet Time\|VATS(?P<pattern>(?:\|[^"\r\n]*)?)"[ \t]*(?:\r\n|\n|\r|)$', re.IGNORECASE)
ASCII_GUARD = 'if eval Sv_RegexMatch (GetFormDescription {form}) "^[\\x00-\\x7F]*$"'
# Older v1.0.5 candidates excluded FormID 044CAF with this condition.
# Keep it for safe detection/removal when upgrading to the English-only
# Concentrated Fire description; ASCII input can use the upstream rewrite.
CONCENTRATED_FIRE_GUARD = 'if eval {form} != "44CAF"'
EXPECTED_BULLET_REWRITES = (
    ('rref', r'|V\.A\.T\.S\.(?!\s[A-Z])|V\.A\.T\.S'),
    ('rr', r'|V\.A\.T\.S\.(?!\s[A-Z])|V\.A\.T\.S'),
    ('avperception', ''),
)


def validate_entry(entry):
    if entry.get('kind') != 'nvse-script':
        raise ValueError('Expected a loose NVSE script entry')
    provider = entry.get('provider')
    path = entry.get('path')
    if (not isinstance(provider, str) or not provider or '/' in provider
            or '\\' in provider or provider in {'.', '..'}):
        raise ValueError('Script provider must be one MO2 mod directory')
    if (not isinstance(path, str) or not path.casefold().startswith(SCRIPT_PREFIX)
            or not path.casefold().endswith('.txt') or '\\' in path
            or '..' in path.split('/')):
        raise ValueError('Script path must be under NVSE/plugins/scripts')
    if entry.get('script_transform') == 'bullet_time_ascii_guard':
        if (entry.get('mappings') or entry.get('provider') != 'Bullet Time - Perk Consistency Patch'
                or Path(path).name.casefold() != 'gr_bullettimeperkdesc.txt'):
            raise ValueError('Bullet Time guard restricted to its known source and provider')
        return
    if not entry.get('mappings') or not isinstance(entry['mappings'], list):
        raise ValueError('NVSE script needs explicit reviewed mappings')
    for row in entry['mappings']:
        if (row.get('command') != 'SetFormDescription'
                or not isinstance(row.get('form'), str)
                or not re.fullmatch(r'[^\s";\\]+', row['form'])):
            raise ValueError('Only SetFormDescription and its exact target form are supported')
        source, dest = row.get('source'), row.get('dest')
        if (not isinstance(source, str) or not isinstance(dest, str)
                or not source or not dest
                or any(character in dest for character in ('"', '\\', '\n', '\r', '\x00'))
                or any(character in source for character in ('\n', '\r', '\x00'))
                or Counter(TOKEN.findall(source)) != Counter(TOKEN.findall(dest))):
            raise ValueError('Unsafe quoted NVSE script translation')
        previous = row.get('previous_dests', [])
        if (not isinstance(previous, list) or any(
                not isinstance(value, str) or not value
                or any(ch in value for ch in ('"', '\\', '\n', '\r', '\x00'))
                for value in previous)):
            raise ValueError('Unsafe previous quoted NVSE script translation')


def _decode(raw, entry):
    expected = entry.get('encoding', 'utf-8')
    if expected not in {'utf-8', 'utf-8-sig', 'utf-16-le', 'utf-16-be'}:
        raise ValueError('Unrecognized NVSE script encoding policy')
    if raw.startswith(b'\xff\xfe'):
        actual, text = 'utf-16-le', raw[2:].decode('utf-16-le')
        bom = b'\xff\xfe'
    elif raw.startswith(b'\xfe\xff'):
        actual, text = 'utf-16-be', raw[2:].decode('utf-16-be')
        bom = b'\xfe\xff'
    elif raw.startswith(b'\xef\xbb\xbf'):
        actual, text = 'utf-8-sig', raw[3:].decode('utf-8')
        bom = b'\xef\xbb\xbf'
    else:
        actual, text = 'utf-8', raw.decode('utf-8')
        bom = b''
    if expected != actual:
        raise ValueError(f'NVSE script encoding changed: expected {expected}, got {actual}')
    return text, actual, bom


def merge_script(source: Path, entry):
    """Return byte-identical script except exact, reviewed literal spans."""
    validate_entry(entry)
    raw = source.read_bytes()
    text, encoding, bom = _decode(raw, entry)
    if entry.get('script_transform') == 'bullet_time_ascii_guard':
        return _guard_bullet_time(text, raw, encoding, bom)
    lookup = {}
    for row in entry['mappings']:
        for candidate in (row['source'], *(row.get('previous_dests') or ()), row['dest']):
            key = row['form'].casefold(), candidate
            if key in lookup and lookup[key] != row['dest']:
                raise ValueError('Conflicting NVSE script translations')
            lookup[key] = row['dest']
    lines = text.splitlines(keepends=True)
    seen = set()
    translated = already = 0
    for index, line in enumerate(lines):
        match = STATEMENT.fullmatch(line)
        if not match:
            continue
        identity = match['form'].casefold(), match['value']
        dest = lookup.get(identity)
        if dest is None:
            continue
        seen.add(identity)
        if dest == match['value']:
            already += 1
        else:
            lines[index] = match['prefix'] + dest + match['suffix']
            translated += 1
    missing = [
        {'form': row['form'], 'source': row['source'], 'reason': 'source_or_command_mismatch'}
        for row in entry['mappings']
        if not any((row['form'].casefold(), candidate) in seen
                   for candidate in (row['source'], *(row.get('previous_dests') or ()), row['dest']))]
    result = bom + ''.join(lines).encode('utf-8' if encoding == 'utf-8-sig' else encoding)
    # Independently prove exact recovery by swapping only the replaced literal
    # lines back; all other bytes, delimiters and scripts must be unchanged.
    restored = lines[:]
    for index, (before, after) in enumerate(zip(text.splitlines(keepends=True), lines)):
        if before != after:
            prior = STATEMENT.fullmatch(before)
            updated = STATEMENT.fullmatch(after)
            if (not prior or not updated or prior['prefix'] != updated['prefix']
                    or prior['suffix'] != updated['suffix']):
                raise ValueError('NVSE script changed outside an approved literal')
            restored[index] = before
    if bom + ''.join(restored).encode('utf-8' if encoding == 'utf-8-sig' else encoding) != raw:
        raise ValueError('NVSE script byte restoration mismatch')
    return result, {'translated': translated, 'already_translated': already,
                    'unmatched': len(missing), 'unmatched_entries': missing,
                    'encoding': encoding}


def _guard_bullet_time(text, original, encoding, bom):
    """Prevent a third-party VATS regex rewrite from re-encoding Korean PERKs.

    All non-ASCII descriptions are protected by an ASCII condition. Since
    Concentrated Fire's DESC deliberately remains English, do not exclude
    FormID 044CAF: it needs the original V.A.T.S. -> Bullet Time replacement.
    Safely remove that extra outer guard from previous v1.0.5 candidates.
    """
    lines = text.splitlines(keepends=True)
    pairs = []
    for index, line in enumerate(lines[:-1]):
        match = REGEX_REWRITE.fullmatch(line)
        if match is None:
            continue
        form = match['form']
        setter = re.fullmatch(
            r'[ \t]*SetFormDescription[ \t]+' + re.escape(form)
            + r'[ \t]+"%z"[ \t]+svDescription[ \t]*(?:\r\n|\n|\r|)',
            lines[index + 1], re.IGNORECASE)
        if setter is None:
            raise ValueError('Unexpected Bullet Time description setter')
        pairs.append((index, form, match['indent'], match['pattern']))
    # The upstream commands have a specific replacement|pattern, ordering,
    # and target. Do not rewrite an unfamiliar revision merely because it
    # contains three visually similar GetFormDescription calls.
    if ([(form.casefold(), pattern) for _, form, _, pattern in pairs]
            != list(EXPECTED_BULLET_REWRITES)
            or text.count('aForms = GLTA 86') != 1
            or text.count('aForms = GLTA 98') != 1):
        return original, {'translated': 0, 'already_translated': 0, 'unmatched': 1,
                          'unmatched_entries': [{'reason': 'unexpected_bullet_time_script_structure'}],
                          'encoding': encoding}
    newline = '\r\n' if '\r\n' in text else '\n'
    states = []
    # Identify precisely three permitted revisions: original, previous
    # ASCII-only output, and current full output. Reject partial edits.
    for index, form, indent, _ in pairs:
        ascii_guard = indent + ASCII_GUARD.format(form=form) + newline
        tail = indent + 'endif' + newline
        has_ascii_start = index > 0 and lines[index - 1] == ascii_guard
        has_ascii_end = index + 2 < len(lines) and lines[index + 2] == tail
        if has_ascii_start != has_ascii_end:
            raise ValueError('Partially guarded Bullet Time script requires manual inspection')
        if form.casefold() == 'avperception':
            states.append('ascii' if has_ascii_start else 'original')
            continue
        known_guard = indent + CONCENTRATED_FIRE_GUARD.format(form=form) + newline
        has_known_start = index > 1 and lines[index - 2] == known_guard
        has_known_end = index + 3 < len(lines) and lines[index + 3] == tail
        if has_known_start != has_known_end or (has_known_start and not has_ascii_start):
            raise ValueError('Partially guarded Bullet Time script requires manual inspection')
        states.append('full' if has_known_start else
                      'ascii' if has_ascii_start else 'original')
    if tuple(states) not in (('original',) * 3,
                             ('ascii',) * 3,
                             ('full', 'full', 'ascii')):
        raise ValueError('Partially guarded Bullet Time script requires manual inspection')
    for (index, form, indent, _), state in reversed(list(zip(pairs, states))):
        ascii_guard = indent + ASCII_GUARD.format(form=form) + newline
        tail = indent + 'endif' + newline
        if state == 'full':
            # Migrate the earlier known-form exclusion back to the guarded
            # English text path, keeping the original replacement command.
            del lines[index + 3]
            del lines[index - 2]
            continue
        if state == 'ascii':
            continue
        lines[index:index + 2] = [ascii_guard, lines[index], lines[index + 1], tail]
    if states[0] != 'full':
        # xNVSE's inline Script Runner lambda has a strict 512 character
        # limit. The upstream CallAfter lambda is already 511 characters.
        # The Unicode guard must fit without changing its commands,
        # token order, strings, comments or block delimiters. Indentation and
        # empty lines are cosmetic in this language.
        start = next((i for i, line in enumerate(lines)
                      if line.startswith('CallAfter 0 (begin function')), None)
        end = next((i for i, line in enumerate(lines)
                    if line.startswith('end) 1 aForms iCount')), None)
        if start is None or end is None or end <= start:
            raise ValueError('Cannot verify Bullet Time CallAfter lambda')
        if len(''.join(lines[start:end + 1])) > 512:
            compact = [line.lstrip(' \t') for line in lines[start + 1:end]
                       if line.strip()]
            lines[start + 1:end] = compact
            end = start + len(compact) + 1
        if len(''.join(lines[start:end + 1])) > 512:
            # The original tutorial-skip condition remains intact, but moving
            # its explanatory comment outside the UDF may be necessary to fit
            # the guard inside JIP's documented 512-character lambda cap.
            comment = ';; Skip the tutorial messages'
            indices = [i for i in range(start + 1, end)
                       if lines[i].strip() == comment]
            if len(indices) != 1:
                raise ValueError('Bullet Time lambda would exceed the NVSE 512-character limit')
            moved = lines.pop(indices[0]).lstrip(' \t')
            lines.insert(start, moved)
    # Validate also on a second pass: an already patched but invalid lambda
    # must not silently pass the idempotence check.
    start = next((i for i, line in enumerate(lines)
                  if line.startswith('CallAfter 0 (begin function')), None)
    end = next((i for i, line in enumerate(lines)
                if line.startswith('end) 1 aForms iCount')), None)
    if start is None or end is None or end <= start:
        raise ValueError('Cannot verify Bullet Time CallAfter lambda')
    if len(''.join(lines[start:end + 1])) > 512:
        raise ValueError('Bullet Time lambda would exceed the NVSE 512-character limit')
    result = bom + ''.join(lines).encode('utf-8' if encoding == 'utf-8-sig' else encoding)
    already = sum(state == 'ascii' for state in states)
    return result, {'translated': 3 - already,
                    'already_translated': already, 'unmatched': 0,
                    'unmatched_entries': [], 'encoding': encoding,
                    'status_note': ('Concentrated Fire preserved in English with the '
                                    'original Bullet Time rewrite; non-ASCII descriptions '
                                    'are never rewritten; game validation required')}


def builtin_perk_scripts():
    """Source-grounded overrides for the runtime Tag! script from issue #11."""
    entry = {
        'kind': 'nvse-script', 'path': 'nvse/plugins/scripts/gr_TagPerkDescriptionSetter.txt',
        'encoding': 'utf-8',
        'review_status': 'runtime_script_reviewed',
        'mappings': [{
            'command': 'SetFormDescription', 'form': 'Tag',
            'source': ('The Tag! perk allows you to select a fourth skill to be a tag skill, '
                       'which will double the rate at which that skill advances.'),
            'dest': ('태그! 퍽을 선택하면 네 번째 주력 기술을 지정할 수 있으며, '
                     '해당 기술의 숙련도 상승 속도가 두 배가 됩니다.'),
            'previous_dests': [
                ('태그! 특전을 선택하면 네 번째 태그 기술을 지정할 수 있으며, '
                 '지정한 기술의 성장 속도가 두 배로 증가합니다.'),
            ],
        }],
    }
    return [
        *({**entry, 'provider': provider} for provider in (
            'SSS - Sweets Simple Settings', 'Tag Perk Description Adjustment')),
        {'kind': 'nvse-script', 'provider': 'Bullet Time - Perk Consistency Patch',
         'path': 'nvse/plugins/Scripts/gr_BulletTimePerkDesc.txt',
         'encoding': 'utf-8', 'script_transform': 'bullet_time_ascii_guard',
         'review_status': 'runtime_script_reviewed'},
    ]
