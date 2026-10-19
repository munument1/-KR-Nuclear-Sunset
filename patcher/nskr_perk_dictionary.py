"""Stage an isolated tNVSE dictionary overlay for compiled PERK descriptions.

Source SCPT/SCDA code is left untouched. The Fast Metabolism source is a
Korean/English mixed string; only its long, exact English suffix is a wildcard
anchor. Existing dictionary wildcard rules must be absent before enabling
tNVSE's mixed-source switch.
"""
from __future__ import annotations

import configparser
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import nskr
from tools.audit_issue11_compiled_scripts import CASES, inspect_record


MOD_NAME = 'Nuclear Sunset - Korean Perk Runtime'
PLUGIN_DIR = 'NVSE/plugins'
DICT_FILENAME = 'NSKR_Perk_Descriptions.json'
DICT_VIRTUAL_PATH = 'Data/nvse/plugins/' + DICT_FILENAME
RELATIVE_FILES = ('tnvse.ini', 'tnvse_dictionary.xml', DICT_FILENAME)
FAST_BASE_EN = 'With the Fast Metabolism perk, you gain a 20% Health bonus when using Stimpaks.'
FAST_BASE_KO = '재빠른 신진대사 퍽이 있으면, 스팀팩의 체력 회복량이 20% 증가합니다.'
FAST_SUFFIX_EN = ' Alcohol will also reduce your radiation twice as quickly.'
FAST_SUFFIX_KO = ' 술을 마시면 방사능 수치도 두 배 빠르게 감소합니다.'
HEADHUNTER_KO = (
    '적의 두 눈 사이에 총알을 명중시키기 위해 신중하게 조준합니다. '
    '불릿 타임에서 적의 머리를 명중시킬 확률이 25% 증가하는 대신 AP 소모량이 50% 증가합니다. '
    '2단계에서는 엎드린 자세에서 재장전 속도가 25% 증가하고, '
    '불릿 타임에서 적의 머리를 공격할 때 치명타 피해량이 15% 증가합니다.'
)


def dictionary_entries():
    """Exact displayed sentences derived from the two verified compiled scripts.

    NVSE printf ``%%`` is normally rendered as a single ``%``. Keep both
    exact alternatives until the live output has been observed; no broad match.
    """
    head_en = CASES[0]['source_en']
    if '%%' not in head_en or CASES[1]['source_en'] != '%z' + FAST_SUFFIX_EN:
        raise ValueError('Reviewed compiled script source changed')
    pairs = [
        (head_en.replace('%%', '%'), HEADHUNTER_KO),
        (head_en, HEADHUNTER_KO),
        ('[%]' + FAST_SUFFIX_EN, '[%]' + FAST_SUFFIX_KO),
        (FAST_BASE_EN + FAST_SUFFIX_EN, FAST_BASE_KO + FAST_SUFFIX_KO),
    ]
    if len(set(source for source, _ in pairs)) != len(pairs):
        raise ValueError('Dictionary sources must be unique')
    return [{'original': source, 'translation': translation} for source, translation in pairs]


def render_xml_overlay(source: bytes, *, allow_empty=False) -> bytes:
    """Preserve the existing XML byte-for-byte except one new dictionary node."""
    bom = b'\xef\xbb\xbf' if source.startswith(b'\xef\xbb\xbf') else b''
    text = source[len(bom):].decode('utf-8')
    root = ET.fromstring(text)
    if root.tag.casefold() != 'tnvse':
        raise ValueError('Unrecognized tNVSE XML root')
    dictionaries = [node for node in root if node.tag.casefold() == 'dictionary']
    if len(dictionaries) != 1:
        raise ValueError('Expected one tNVSE dictionary node')
    nodes = dictionaries[0]
    paths = [item.attrib.get('path', '').casefold() for item in nodes if item.tag.casefold() == 'json']
    if not paths and not allow_empty:
        raise ValueError('Existing dictionary JSON source missing')
    if DICT_VIRTUAL_PATH.casefold() in paths:
        matched = [item for item in nodes if item.tag.casefold() == 'json'
                   and item.attrib.get('path', '').casefold() == DICT_VIRTUAL_PATH.casefold()]
        if len(matched) != 1 or matched[0].attrib.get('priority') != '40':
            raise ValueError('Existing perk dictionary node differs')
        return source
    ending = list(re.finditer(r'</\s*dictionary\s*>', text, re.IGNORECASE))
    if len(ending) != 1:
        raise ValueError('Cannot safely append dictionary XML source')
    line = f'<json path="{DICT_VIRTUAL_PATH}" priority="40"/>'
    at = ending[0].start()
    updated = text[:at] + line + text[at:]
    ET.fromstring(updated)
    return bom + updated.encode('utf-8')


def render_ini_overlay(data: bytes) -> bytes:
    text = data.decode('utf-8-sig')
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.read_string(text)
    if not config.has_section('Multibyte') or not config.has_section('Dictionary'):
        raise ValueError('tNVSE multibyte/dictionary sections missing')
    checks = (("Multibyte", "bEnableMultibyteFontHook"),
              ("Dictionary", "bEnableDictionaryTranslation"))
    if any(config.getint(section, key, fallback=0) != 1 for section, key in checks):
        raise ValueError('Installed tNVSE dictionary/multibyte support inactive')
    if config.getint('Dictionary', 'bEnableDictionaryWildcardTranslation', fallback=0) != 1:
        raise ValueError('Installed tNVSE wildcard support inactive')
    if config.getint('Dictionary', 'bEnableDictionaryRegexTranslation', fallback=0) != 0:
        raise ValueError('Unreviewed regex translation alongside mixed-source mode')
    if config.getint('Dictionary', 'bEnableDictionaryPerkDescriptionTranslation', fallback=0) != 0:
        raise ValueError('Unreviewed structured perk translation alongside mixed-source mode')
    # Replace only the value in the correct INI section; leave every other
    # setting, encoding, CRLF and comment intact.
    lines = text.splitlines(keepends=True)
    section = None
    matches = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section = stripped.casefold()
        if section == '[dictionary]' and re.match(
                r'^\s*bEnableDictionaryMixedSourceTranslation\s*=', line, re.I):
            matches.append(i)
    if len(matches) != 1:
        raise ValueError('Expected exactly one mixed-source tNVSE setting')
    index = matches[0]
    if config.getint('Dictionary', 'bEnableDictionaryMixedSourceTranslation', fallback=-1) not in (0, 1):
        raise ValueError('Unrecognized mixed-source config setting')
    old_line = lines[index]
    lines[index] = re.sub(
        r'(?i)^(\s*bEnableDictionaryMixedSourceTranslation\s*=\s*)[01]',
        r'\g<1>1', old_line, count=1)
    return (b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'') + ''.join(lines).encode('utf-8')


def render_dictionary_overlay(ini: bytes, xml: bytes, existing_json: bytes, *, allow_empty=False):
    """Return exact overlay files; guard against global wildcard interactions."""
    existing_entries = json.loads(existing_json.decode('utf-8-sig'))
    if not isinstance(existing_entries, list) or any(
            not isinstance(e, dict) or not isinstance(e.get('original'), str)
            for e in existing_entries):
        raise ValueError('Existing dictionary has unexpected JSON schema')
    if any('[%]' in e['original'] for e in existing_entries):
        raise ValueError('Existing wildcard entries would become mixed-source eligible')
    dictionary = dictionary_entries()
    payload = json.dumps(dictionary, ensure_ascii=False, indent=2).encode('utf-8') + b'\n'
    if json.loads(payload) != dictionary:
        raise ValueError('Dictionary JSON round-trip mismatch')
    return {'tnvse.ini': render_ini_overlay(ini),
            'tnvse_dictionary.xml': render_xml_overlay(xml, allow_empty=allow_empty),
            DICT_FILENAME: payload}


def _source_matches(installation) -> tuple[bool, str]:
    """Allow this mapping only for the exact, independently audited mod builds."""
    for spec in CASES:
        provider, filename = spec['relative_plugin'].split('/', 1)
        if provider not in installation.mods_enabled:
            return False, f'mod_not_enabled:{provider}'
        source = installation.mods / provider / filename
        if not source.is_file():
            return False, f'plugin_not_found:{filename}'
        with source.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != spec['expected_sha256']:
            return False, f'plugin_version_mismatch:{filename}'
        try:
            inspect_record(source, spec)
        except (ValueError, UnicodeError, OSError) as exc:
            return False, f'compiled_literal_mismatch:{filename}:{exc}'
    return True, 'source_literals_verified'


def build_perk_dictionary(installation, stage: Path, seen: set[str]):
    """Stage three files in a new MO2 mod; return ``(file_rows, status)``.

    This is a passive translation overlay requiring manual MO2 activation above
    existing tNVSE and Korean UI providers. ``stage`` must be outside MO2.
    """
    stage = Path(stage).resolve()
    if stage.is_relative_to(installation.mods.resolve()) or stage.is_relative_to(installation.game.resolve()):
        raise ValueError('Output stage overlaps MO2 or game files')
    # GUI inventory mode deliberately scans *all* installed mods and its
    # alphabetical provider order is not the selected profile's VFS order.
    # Only this runtime overlay must resolve original files via the selected
    # MO2 profile. Keep the caller's full-install inventory untouched.
    runtime_installation = installation
    if getattr(installation, 'all_installed', False):
        try:
            runtime_installation = nskr.Installation(
                installation.root, game_dir=installation.game)
        except (OSError, ValueError, KeyError, configparser.Error) as exc:
            return [], {'status': 'skipped',
                        'reason': f'selected_profile_unavailable:{exc}',
                        'game_validation': 'not_run'}
    valid, reason = _source_matches(runtime_installation)
    if not valid:
        return [], {'status': 'skipped', 'reason': reason, 'game_validation': 'not_run'}

    sources = {}
    try:
        # The font builder may have staged a newer Korean INI in the same
        # Output before this builder runs. Retain its rendering configuration.
        staged_ini = list(stage.glob('mods/*/NVSE/plugins/tnvse.ini'))
        if len(staged_ini) > 1:
            raise ValueError('Ambiguous staged tNVSE INI provider')
        for name in ('tnvse.ini', 'tnvse_dictionary.xml'):
            source = staged_ini[0] if name == 'tnvse.ini' and staged_ini else None
            if source is None:
                try:
                    source = runtime_installation.source(f'{PLUGIN_DIR}/{name}')
                except ValueError:
                    if name != 'tnvse_dictionary.xml':
                        raise
                    source = None
            if source is None:
                sources[name] = (None, b'<tNVSE><dictionary></dictionary></tNVSE>')
                continue
            sources[name] = (source, source.read_bytes())
        source_ini = sources['tnvse.ini'][1]
        source_xml = sources['tnvse_dictionary.xml'][1]
        root = ET.fromstring(source_xml.decode('utf-8-sig'))
        dictionary_nodes = [node for node in root if node.tag.casefold() == 'dictionary']
        if len(dictionary_nodes) != 1:
            raise ValueError('Unsupported existing tNVSE dictionary layout')
        original_json_paths = [node.attrib.get('path') for node in dictionary_nodes[0]
                               if node.tag.casefold() == 'json'
                               and node.attrib.get('path', '').casefold() != DICT_VIRTUAL_PATH.casefold()]
        xml_absent = sources['tnvse_dictionary.xml'][0] is None
        if xml_absent and not original_json_paths:
            existing_json = b'[]'
        else:
            if (len(original_json_paths) != 1 or
                    not original_json_paths[0].lower().startswith('data/nvse/plugins/')):
                raise ValueError('Dictionary set must contain one reviewed JSON source')
            json_relative = original_json_paths[0][5:]
            staged_json = list(stage.glob(f'mods/*/{json_relative}'))
            if len(staged_json) > 1:
                raise ValueError('Ambiguous staged tNVSE dictionary JSON provider')
            existing_json_source = (staged_json[0] if staged_json
                                    else runtime_installation.source(json_relative))
            existing_json = existing_json_source.read_bytes()
        payloads = render_dictionary_overlay(source_ini, source_xml, existing_json,
                                             allow_empty=xml_absent)
    except (ValueError, OSError, UnicodeError, ET.ParseError, configparser.Error) as exc:
        return [], {'status': 'skipped', 'reason': f'tnvse_source_incompatible:{exc}',
                    'game_validation': 'not_run'}

    output_paths = {name: f'mods/{MOD_NAME}/{PLUGIN_DIR}/{name}' for name in RELATIVE_FILES}
    for key in output_paths.values():
        if key.casefold() in seen or (stage / key).exists():
            raise ValueError(f'Conflicting staged PERK runtime path: {key}')
    for name, (source, raw) in sources.items():
        if source is not None and source.read_bytes() != raw:
            raise ValueError(f'tNVSE source changed while staging: {source}')

    rows = []
    for name, key in output_paths.items():
        target = stage / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payloads[name])
        seen.add(key.casefold())
        rows.append({'path': f'{PLUGIN_DIR}/{name}', 'output_path': key,
                     'provider': MOD_NAME,
                     'source_sha256': (hashlib.sha256(sources[name][1]).hexdigest()
                                       if name in sources and sources[name][0] is not None else None),
                     'output_sha256': hashlib.sha256(payloads[name]).hexdigest(),
                     'status': 'perk_compiled_dictionary_exact_overlay'})
    priorities = ['tNVSE', 'tNVSE Default Config']
    for name in ('tnvse.ini', 'tnvse_dictionary.xml'):
        chain = runtime_installation.providers.get(f'{PLUGIN_DIR}/{name}'.casefold(), [])
        if chain:
            priorities.append(chain[-1]['provider'])
    for staged_ini in stage.glob('mods/*/NVSE/plugins/tnvse.ini'):
        priorities.append(staged_ini.relative_to(stage).parts[1])
    return rows, {'status': 'generated', 'mod': MOD_NAME,
                  'mods_requiring_activation': ([] if MOD_NAME in runtime_installation.mods_enabled else [MOD_NAME]),
                  'requires_priority_above': sorted(set(priorities) - {MOD_NAME}),
                  'source_profile': getattr(runtime_installation, 'profile', ''),
                  'dictionary_entries': len(dictionary_entries()),
                  'enabled_global_mixed_source_matching': True,
                  'existing_wildcard_entries': 0,
                  'source_validation': reason, 'game_validation': 'not_run'}
