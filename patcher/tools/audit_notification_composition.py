"""Read-only audit of active-profile notification composition inputs.

Reports offline plugin winners. Runtime scripts/native hooks may still replace
their values; this inventory alone does not establish in-game resolution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from nskr_compiled_scpt import _walk, _slots, _decode_record
from nskr_composed_display import CP949_GMSTS

TARGETS = CP949_GMSTS | {'sskillincreased', 'sskillincreasednum', 'sskilldecreased'}


def describe(value):
    raw = value.rstrip(b'\0')
    for encoding in ('utf-8', 'cp949'):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        if any('\uac00' <= char <= '\ud7a3' for char in text):
            return dict(encoding=encoding, text=text,
                        payload_sha256=hashlib.sha256(value).hexdigest())
    return dict(encoding='ascii_or_unknown',
                payload_sha256=hashlib.sha256(value).hexdigest())


def audit(installation):
    winners = {}
    for plugin in installation.active:
        chain = installation.providers.get(plugin.casefold(), [])
        if not chain:
            continue
        source = Path(chain[-1]['physical'])

        def visit(header, payload):
            if header[:4] not in (b'GMST', b'AVIF'):
                return payload
            slots = list(_slots(_decode_record(header, payload)))
            edid = next((v.rstrip(b'\0').decode('ascii', 'replace')
                         for key, _, v in slots if key == b'EDID'), '')
            if header[:4] == b'GMST' and edid.casefold() not in TARGETS:
                return payload
            field = b'DATA' if header[:4] == b'GMST' else b'FULL'
            value = next((v for key, _, v in slots if key == field), None)
            if value is not None:
                winners[(header[:4].decode(), edid.casefold())] = dict(
                    plugin=plugin, provider=chain[-1]['provider'],
                    signature=header[:4].decode(), edid=edid, field=field.decode(),
                    form=f'{struct.unpack_from("<I", header, 12)[0]:08X}',
                    **describe(value))
            return payload

        _walk(source.read_bytes(), visit)
    return dict(profile=installation.profile, offline_inventory_only=True,
                in_game_verified=False, inputs=list(winners.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mo2', type=Path, required=True)
    parser.add_argument('--profile')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(nskr.Installation(args.mo2, args.profile))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Reported {len(result["inputs"])} active-profile composition inputs')
