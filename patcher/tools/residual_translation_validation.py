"""Source-format checks for plugin and runtime UI translation candidates."""
from collections import Counter
import re

from nskr_xedit import FORMAT

EXTRA = re.compile(r'\$[A-Za-z_]\w*|\{[^{}\r\n]+\}|\\[nrt]|\\x[0-9a-fA-F]{2}|#\d+\|')


def protected(text):
    return Counter(FORMAT.findall(text)) + Counter(EXTRA.findall(text))


def normalize_boundary_whitespace(source, destination):
    """Preserve source layout outside the translated prose."""
    prefix = re.match(r'^\s*', source)[0]
    suffix = re.search(r'\s*$', source)[0]
    return prefix + destination.strip() + suffix


def validate(source, destination, signature='', field=''):
    reasons = []
    if not isinstance(destination, str) or not destination.strip():
        return ['empty_or_non_string_translation']
    if protected(source) != protected(destination):
        reasons.append('protected_token_mismatch')
    if source.replace('\r\n', '\n').count('\n') != destination.replace('\r\n', '\n').count('\n'):
        reasons.append('newline_count_mismatch')
    if '\ufffd' in destination or '\0' in destination:
        reasons.append('invalid_output_character')
    if (signature == 'MESG' and field == 'DESC'
            and len(source.encode('utf-8')) <= 1023
            and len(destination.encode('utf-8')) > 1023):
        reasons.append('message_byte_budget_exceeded')
    return reasons
