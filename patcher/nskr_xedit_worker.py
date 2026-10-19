"""Headless UTF-8 XEditLib worker for VNV Korean Patcher.

The parent process prepares an isolated copy of the current MO2 load-order prefix.
This worker applies direct SST mappings first, then base/DLC SST fallback mappings
for exact owner/FormID/signature/field/path/source matches. It performs no network I/O.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from nskr_xelib import XEditLib
from nskr_plugin_text import write_plugin, verify_plugin

FLAT_SIGNATURES = {
    'CELL','WRLD','REFR','ACRE','ACTI','ARMO','ARMA','WEAP','MISC','KEYM',
    'ALCH','CLAS','RACE','HDPT','HAIR','EYES','CSNO','AMEF','REPU','RCCT','FURN','MSET','COBJ','IMOD',
    'CMNY','LIGH','GMST','PROJ','CCRD','DOOR','NPC_','CREA','CONT','ENCH','TACT','MGEF','AMMO','CDCK',
    'BOOK','RCPE','MSTT','CHAL','INGR','CHIP','SPEL','NOTE','EXPL','DIAL','LSCR','WATR','ALOC',
}
DISPLAY_CONTAINERS = {'XMRK','EPFT','RDAT'}
FIELD_RE = re.compile(r'^([A-Z0-9_]{4})(?: -|$)')


def normalize_cp1252_sources(items, candidates):
    """Restore only explicitly typed, exact CP1252 source-byte views."""
    for item in items:
        sources = set()
        for candidate in candidates:
            if (candidate.get('source_encoding') != 'cp1252'
                    or candidate['field'] != item['field']
                    or candidate['path'] != item['path']
                    or candidate.get('field_occurrence') != item['field_occurrence']):
                continue
            expected = candidate['source'].encode('cp1252').decode('utf-8', errors='replace')
            if expected == item['source']:
                sources.add(candidate['source'])
        if len(sources) > 1:
            raise ValueError('Ambiguous explicit CP1252 source-byte view')
        if sources:
            item['source'] = next(iter(sources))


def canonical_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def sha_obj(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()


def runtime_dir() -> Path:
    explicit = os.environ.get('NSKR_XEDIT_RUNTIME')
    if explicit:
        return Path(explicit).resolve()
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent / 'Backend'
    fallback = Path(__file__).resolve().parent / '.tools' / 'xeditlib-native'
    if fallback.is_dir():
        return fallback
    raise FileNotFoundError('XEditLib runtime directory is not configured')


def field_name(x: XEditLib, handle: int):
    match = FIELD_RE.match(x.name(handle))
    return match.group(1) if match else None


def text_fields(x: XEditLib, record: int, wanted: set[str]):
    found = []
    signature = x.signature(record)
    if signature in FLAT_SIGNATURES:
        for field in wanted:
            paths = (['FULL', r'XMRK\FULL'] if signature == 'REFR' and field == 'FULL'
                     else [r'TNAM\Text'] if signature == 'NOTE' and field == 'TNAM'
                     else [field])
            for relative in paths:
                if not x.has_element(record, relative):
                    continue
                child = x.get_element(record, relative)
                try:
                    if x.value_type(child) in (3, 4):
                        found.append({'field': field, 'path': relative, 'source': x.get_value(child)})
                finally:
                    x.release(child)
        return found

    def walk(handle: int, inherited=None, prefix=''):
        try:
            children = x.get_elements(handle)
        except Exception:
            return
        for child in children:
            try:
                if x.element_type(child) in (0, 1, 2, 10, 11, 13):
                    continue
                named = field_name(x, child)
                field = named or inherited
                part = x.path_name(child, True) or x.path_name(child, False) or x.name(child)
                relative = prefix + '\\' + part if prefix else part
                value_type = x.value_type(child)
                if field and field in wanted and value_type in (3, 4):
                    found.append({'field': field, 'path': relative, 'source': x.get_value(child)})
                elif value_type in (9, 10, 11) and (
                        not named or named in wanted or named in DISPLAY_CONTAINERS):
                    walk(child, field, relative)
            finally:
                x.release(child)
    walk(record)
    return found


class IdentityCache:
    def __init__(self, x: XEditLib):
        self.x = x
        self.files = {}

    def identity(self, file_handle: int, record: int):
        if file_handle not in self.files:
            self.files[file_handle] = {
                'masters': self.x.get_master_names(file_handle),
                'name': self.x.name(file_handle),
            }
        local = self.x.get_form_id(record, True)
        meta = self.files[file_handle]
        index = local >> 24
        owner = meta['masters'][index] if index < len(meta['masters']) else meta['name']
        return {
            'owner': owner.lower(),
            'id': format(local & 0xFFFFFF, '06x'),
            'signature': self.x.signature(record),
        }


def row_key(row) -> str:
    return '|'.join((row['owner'].lower(), row['id'].lower(), row['signature']))


def record_json(x: XEditLib, record: int):
    signature = x.signature(record)
    if signature in {'CELL', 'DIAL', 'WRLD'}:
        obj = {}
        for child in x.get_elements(record):
            try:
                if x.element_type(child) not in (0, 1, 2) and not x.name(child).startswith('Child Group'):
                    obj.update(json.loads(x.element_to_json(child)))
            finally:
                x.release(child)
    else:
        obj = json.loads(x.element_to_json(record))
    if isinstance(obj.get('Record Header'), dict):
        obj['Record Header'].pop('Data Size', None)
    group = x.get_element_group(record)
    try:
        obj['$parent'] = x.path(group, True, True)
    finally:
        x.release(group)
    return obj


def digest(x: XEditLib, record: int) -> str:
    return sha_obj(record_json(x, record))


def header_digest(x: XEditLib, file_handle: int) -> str:
    header = x.get_element(file_handle, 'File Header')
    try:
        obj = json.loads(x.element_to_json(header))
    finally:
        x.release(header)
    if isinstance(obj.get('Record Header'), dict):
        obj['Record Header'].pop('Data Size', None)
    if isinstance(obj.get('HEDR - Header'), dict):
        obj['HEDR - Header'].pop('Number of Records', None)
    onam = obj.get('ONAM - Overriden Forms')
    if isinstance(onam, list):
        onam.sort()
    return sha_obj(obj)


def matching_rows(item, candidates, exact_path, *, accept_translated=False):
    return [c for c in candidates
            if c['field'] == item['field']
            and (not exact_path or c['path'] == item['path'])
            and (c['source'] == item['source'] or (
                accept_translated and c['path'] == item['path']
                and item['source'] in (c['dest'], *(c.get('previous_dests') or ()))))]


def select_destination(item, direct_candidates, fallback_candidates, strict_path=False):
    # Direct SST always wins. Prefer exact xEdit path; source+field is only a
    # fallback for stable flat records where the SST has no path information.
    direct = matching_rows(item, direct_candidates, True)
    if not direct and not strict_path:
        direct = matching_rows(item, direct_candidates, False)
    if not direct:
        # Previously generated Korean plugins can be a source provider after a
        # manual MO2 copy. A known previous translation is an exact source too,
        # but it must match the same record, field and xEdit path. This lets a
        # later release replace old Korean text with its revised translation.
        direct = matching_rows(item, direct_candidates, True, accept_translated=True)
    if direct:
        origins = {c.get('origin', 'sst_direct') for c in direct}
        return {c['dest'] for c in direct}, next(iter(origins)) if len(origins) == 1 else 'mixed_direct'

    # Base/DLC inheritance is deliberately stricter: an override must retain the
    # exact field path as well as owner/FormID/signature/source.
    inherited = matching_rows(item, fallback_candidates, True)
    if not inherited:
        inherited = matching_rows(item, fallback_candidates, True, accept_translated=True)
    if inherited:
        return {c['dest'] for c in inherited}, 'base_dlc_sst_fallback'
    return set(), None


def unmatched_candidates(items, candidates, strict_path):
    return [c for c in candidates
            if not any(matching_rows(item, [c], strict_path)
                       or matching_rows(item, [c], True, accept_translated=True)
                       for item in items)]


def run(request: dict):
    root = runtime_dir()
    dll = root / 'XEditLib.dll'
    if not dll.is_file():
        raise FileNotFoundError(dll)
    if ctypes.windll.kernel32.GetACP() != 65001:
        raise RuntimeError('NSKR XEdit worker must run with UTF-8 active code page')

    x = XEditLib(dll)
    game = Path(request['game']).resolve()
    fallback_targets = {x.lower() for x in request.get('fallbackTargets', [])}
    fallback_by_record = {}
    for mapping in request.get('fallbackMappings') or []:
        fallback_by_record.setdefault(row_key(mapping), []).append(mapping)

    result = {'engine': 'Python/ctypes/XEditLib', 'acp': 65001, 'files': []}
    fields_by_sig = {sig: set(fields) for sig, fields in (request.get('fields') or {}).items()}
    inspect_keys = set(request.get('inspectRecordKeys', []))

    x.init()
    try:
        x.set_language('English')
        x.set_game_path(str(game) + os.sep)
        x.set_game_mode(x.GM_FNV)
        x.load_plugins('\n'.join(request['plugins']), True, False)
        x.wait_for_loader()

        targets = request.get('targets') or request['plugins']
        for plugin in targets:
            # XEditLib may recycle numeric handles after Release(). Never keep
            # file metadata cached across target files under the old handle.
            identities = IdentityCache(x)
            file_handle = x.file_by_name(plugin)
            rows, changed, missing, before_hashes = [], [], [], []
            already_translated_count = 0
            try:
                head_hash = header_digest(x, file_handle)
                expected_header = request.get('expectedHeaders', {}).get(plugin)
                if expected_header and expected_header != head_hash:
                    raise RuntimeError('Plugin header readback mismatch ' + plugin)

                expected = {row_key(r): r for r in request.get('expected', {}).get(plugin, [])}
                expected_changes = {}
                for update in request.get('changes', {}).get(plugin, []):
                    expected_changes.setdefault(row_key(update), []).append(update)

                mappings = (request.get('mappings') or {}).get(plugin, [])
                direct_by_record = {}
                for mapping in mappings:
                    direct_by_record.setdefault(row_key(mapping), []).append(mapping)
                allow_fallback = plugin.lower() in fallback_targets

                all_records = x.get_records(file_handle, '', True)
                record_index_keys = []
                verified = set()
                for record in sorted(all_records, reverse=True):
                    try:
                        signature = x.signature(record)
                        if signature == 'TES4':
                            continue
                        ident = identities.identity(file_handle, record)
                        record_key = row_key(ident)
                        record_index_keys.append(record_key)

                        mode = request.get('mode')
                        direct_candidates = direct_by_record.get(record_key, [])
                        inherited_candidates = fallback_by_record.get(record_key, []) if allow_fallback else []
                        prior = expected.get(record_key)

                        needs_items = (
                            mode == 'apply' and (direct_candidates or inherited_candidates)
                        ) or (
                            mode == 'inspect' and (not inspect_keys or record_key in inspect_keys)
                        ) or (
                            mode == 'verify' and prior is not None
                        )
                        if not needs_items:
                            continue

                        edid = ''
                        if x.has_element(record, 'EDID'):
                            edid = x.get_value(record, 'EDID')
                        wanted = fields_by_sig.get(signature)
                        items = (text_fields(x, record, wanted)
                                 if wanted and (signature != 'GMST' or edid.startswith('s'))
                                 else [])
                        occurrences = {}
                        for item in items:
                            occurrence = occurrences.get(item['field'], 0)
                            occurrences[item['field']] = occurrence + 1
                            item['field_occurrence'] = occurrence
                        if mode == 'inspect':
                            rows.extend({**ident, 'edid': edid, **item} for item in items)
                            continue

                        if mode == 'verify':
                            verified.add(record_key)
                            actual = {(item['field'], item['path']): item['source'] for item in items}
                            for update in expected_changes.get(record_key, []):
                                value = actual.get((update['field'], update['path']))
                                if value != update['dest']:
                                    raise RuntimeError(
                                        f"Translation readback mismatch {record_key} {update['path']}: "
                                        f"expected {update['dest']!r}, actual {value!r}")
                            continue

                        normalize_cp1252_sources(items, direct_candidates)
                        updates = []
                        already_translated = 0
                        for candidate in unmatched_candidates(
                                items, direct_candidates, request.get('strictPaths', False)):
                            possible_legacy = any(
                                item['field'] == candidate['field']
                                and item['path'] == candidate['path']
                                and any('\uac00' <= ch <= '\ud7a3' for ch in item['source'])
                                for item in items)
                            missing.append({**ident, **candidate,
                                            'reason': ('unknown_previous_korean_or_changed_source'
                                                       if possible_legacy else 'source_or_path_mismatch'),
                                            'mappingOrigin': candidate.get('origin', 'sst_direct')})
                        for item in items:
                            row = {**ident, 'edid': edid, **item}
                            values, origin = select_destination(
                                row, direct_candidates, inherited_candidates,
                                strict_path=request.get('strictPaths', False))
                            if not values:
                                continue
                            if len(values) != 1:
                                missing.append({**row, 'reason': 'ambiguous_translation',
                                                'mappingOrigin': origin})
                                continue
                            dest = next(iter(values))
                            if dest == row['source']:
                                if any(c['field'] == row['field'] and c['path'] == row['path']
                                       and c['dest'] == row['source']
                                       for c in direct_candidates + inherited_candidates):
                                    already_translated += 1
                                continue
                            if '\ufffd' in row['source']:
                                missing.append({**row, 'reason': 'source_encoding_unreadable',
                                                'mappingOrigin': origin})
                                continue
                            updates.append({**row, 'dest': dest, 'mappingOrigin': origin})

                        already_translated_count += already_translated
                        if updates:
                            changed.extend(updates)
                        if request.get('includeRows'):
                            rows.extend({**ident, 'edid': edid, **item} for item in items)
                    finally:
                        x.release(record)

                record_index_keys.sort()
                record_index_hash = hashlib.sha256(
                    '\n'.join(record_index_keys).encode('utf-8')).hexdigest()
                expected_index = (request.get('expectedRecordIndexes') or {}).get(plugin)
                if expected_index and expected_index != record_index_hash:
                    raise RuntimeError('Record index readback mismatch ' + plugin)
                if request.get('mode') == 'verify' and len(verified) != len(expected):
                    raise RuntimeError('Records missing from readback ' + plugin)

                if request.get('mode') == 'apply':
                    out_dir = Path(request['outDir']).resolve()
                    out_dir.mkdir(parents=True, exist_ok=True)
                    target = out_dir / plugin
                    if target.exists():
                        raise FileExistsError(target)
                    write_plugin(game / 'Data' / plugin, target, changed,
                                 x.get_master_names(file_handle))
                    before_hashes = verify_plugin(
                        game / 'Data' / plugin, target, changed, x.get_master_names(file_handle))

                result['files'].append({
                    'plugin': plugin,
                    'masters': x.get_master_names(file_handle),
                    'headerHash': head_hash,
                    'recordIndexHash': record_index_hash,
                    'recordCount': len(record_index_keys),
                    'rows': rows,
                    'changed': changed,
                    'alreadyTranslated': already_translated_count,
                    'missing': missing,
                    'beforeHashes': before_hashes,
                })
            finally:
                x.release(file_handle)
    finally:
        x.close()
    return result


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--print-acp':
        print(ctypes.windll.kernel32.GetACP())
        return 0
    if len(sys.argv) < 2:
        raise SystemExit('usage: NSKRXEditWorker <request.json> [xEdit isolation switches]')
    request_path = Path(sys.argv[1]).resolve()
    request = json.loads(request_path.read_text(encoding='utf-8-sig'))
    result = run(request)
    output = Path(request['output']).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
