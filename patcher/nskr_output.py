"""Build a manual-copy MO2 Output tree without changing the installation.

Loose translations and native record mappings merge into today's source.
Legacy plugin payloads remain supported as version-pinned copies.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile

import nskr
import nskr_xedit
import nskr_fonts
from tools.loose_translation import TOKEN, decode, json_values, render_json

SCHEMA = 1

FIXED_ESM_MASTERS = {
    'falloutnv.esm', 'deadmoney.esm', 'honesthearts.esm', 'oldworldblues.esm',
    'lonesomeroad.esm', 'gunrunnersarsenal.esm',
}
STARTER_PACK_MASTERS = {
    'classicpack.esm', 'mercenarypack.esm', 'tribalpack.esm', 'caravanpack.esm',
}
FO3_TTW_MASTERS = {
    'fallout3.esm', 'anchorage.esm', 'thepitt.esm', 'brokensteel.esm',
    'pointlookout.esm', 'zeta.esm', 'taleoftwowastelands.esm', 'yupttw.esm',
}
BASE_TRANSLATION_MASTERS = FIXED_ESM_MASTERS | STARTER_PACK_MASTERS | FO3_TTW_MASTERS
PLUGIN_SUFFIXES = {'.esm', '.esp'}


def base_translation_memory(catalog):
    """Return conflict-free translations taken only from the official master entries.

    These rows are safe candidates for newly discovered plugins because xEditLib
    still requires the original owner/FormID/signature/field/path/source to match.
    """
    destinations = defaultdict(set)
    templates = {}
    for entry in catalog.get('files', []):
        if entry.get('kind') != 'plugin-records' or entry.get('path', '').casefold() not in BASE_TRANSLATION_MASTERS:
            continue
        for row in entry.get('mappings', []):
            if row.get('owner', '').casefold() not in BASE_TRANSLATION_MASTERS:
                continue
            if row.get('source') == row.get('dest'):
                continue
            identity = (row['owner'].casefold(), row['id'], row['signature'],
                        row['field'], row['path'], row['source'])
            destinations[identity].add(row['dest'])
            templates.setdefault(identity, row)
    memory = []
    for identity, values in destinations.items():
        if len(values) != 1:
            continue
        row = templates[identity]
        memory.append({key: row[key] for key in ('owner', 'id', 'signature', 'field', 'path', 'source')} |
                      {'dest': next(iter(values))})
    return memory


def runtime_plugin_keys(catalog):
    return {nskr.virtual_path(plugin).casefold()
            for spec in catalog.get('runtime_mods', [])
            for plugin in spec.get('plugins', [])}


def discover_new_plugin_entries(installation, catalog):
    """Find active plugins unknown to this release, without touching runtime KR plugins."""
    known = {entry['path'].casefold() for entry in catalog.get('files', [])
             if entry.get('kind') in {'plugin-copy', 'plugin-records'}}
    ignored = runtime_plugin_keys(catalog)
    entries, skipped = [], []
    for plugin in installation.active:
        key = plugin.casefold()
        if key in known or key in ignored or key in BASE_TRANSLATION_MASTERS:
            continue
        chain = installation.providers.get(key)
        if not chain:
            skipped.append({'path': plugin, 'reason': 'new_plugin_provider_missing',
                            'discovered_plugin': True, 'translation_applied': False})
            continue
        source = Path(chain[-1]['physical']).resolve()
        # MO2 may keep its configured mods/overwrite directories outside the
        # directory that contains ModOrganizer.ini. Treat those configured
        # storage roots as part of the instance instead of comparing only
        # against installation.root.
        managed = source.is_relative_to(installation.mods) or source.is_relative_to(installation.overwrite)
        if not managed:
            skipped.append({'path': plugin, 'provider': chain[-1]['provider'],
                            'reason': 'new_plugin_outside_mo2',
                            'discovered_plugin': True, 'translation_applied': False})
            continue
        entries.append({'path': plugin, 'kind': 'plugin-records',
                        'baseline_sha256': nskr.sha256(source), 'mappings': [],
                        'auto_inherited': True})
    return entries, skipped


def plugin_outcomes(report):
    """Normalize plugin results into categories used by JSON, text report and GUI."""
    outcomes = []
    for row in report.get('files', []):
        if Path(row.get('path', '')).suffix.casefold() not in PLUGIN_SUFFIXES:
            continue
        if row.get('status') == 'runtime_mod_copy':
            category = 'runtime_manual_activation'
        elif row.get('status') == 'already_patched_verified':
            category = 'already_patched'
        elif row.get('discovered_plugin'):
            category = 'new_inherited'
        elif row.get('source_updated'):
            if row.get('translated', 0) == 0:
                category = 'updated_untranslated'
            elif row.get('unmatched', 0):
                category = 'updated_partial'
            else:
                category = 'updated_patched'
        else:
            category = 'patched'
        outcomes.append({'path': row['path'], 'category': category,
                         'translated': row.get('translated', 0),
                         'unmatched': row.get('unmatched', 0),
                         'status': row.get('status'),
                         'provider': row.get('provider')})
    skipped_categories = {
        'not_installed': 'removed',
        'not_enabled': 'disabled',
        'updated_plugin_needs_record_backend': 'updated_untranslated',
        'new_plugin_no_base_translation_match': 'new_no_match',
        'new_plugin_provider_missing': 'new_unavailable',
        'new_plugin_outside_mo2': 'new_unavailable',
    }
    for row in report.get('skipped', []):
        if Path(row.get('path', '')).suffix.casefold() not in PLUGIN_SUFFIXES:
            continue
        category = skipped_categories.get(row.get('reason'))
        if not category:
            continue
        outcomes.append({'path': row['path'], 'category': category,
                         'translated': row.get('translated', 0),
                         'unmatched': row.get('unmatched', row.get('base_record_mismatches', 0)),
                         'reason': row.get('reason'), 'provider': row.get('provider')})
    return outcomes


def format_plugin_report(report):
    labels = [
        ('runtime_manual_activation', '별도 한국어 UI·라디오 플러그인 - 수동 활성화 필요'),
        ('patched', '정상 패치'),
        ('already_patched', '이미 한글 적용됨 - 검증된 결과 재사용'),
        ('updated_patched', '업데이트 감지 - 번역 전체 적용'),
        ('updated_partial', '업데이트 감지 - 일부 문구 미적용'),
        ('updated_untranslated', '업데이트 감지 - 한글 적용 없음'),
        ('removed', '이번 설치에서 제거됨 - 번역 플러그인 생성 안 함'),
        ('disabled', '설치되어 있지만 비활성 - 생성 안 함'),
        ('new_inherited', '신규 플러그인 - Fixed ESM 동일 레코드 번역 상속'),
        ('new_no_match', '신규 플러그인 - 상속 가능한 동일 레코드 없음'),
        ('new_unavailable', '신규 플러그인 - 소스에 접근할 수 없어 건너뜀'),
    ]
    grouped = defaultdict(list)
    for row in report.get('plugin_outcomes', []):
        grouped[row['category']].append(row)
    lines = [
        'Nuclear Sunset 한국어 패쳐 결과',
        f"프로필: {report.get('profile', '')}",
        f"생성 시각(UTC): {report.get('created_utc', '')}",
        ('개발 검수용 출력 · 정식 릴리즈 아님 · 게임 내 검증 필요'
         if report.get('channel') == 'development' else '정식 카탈로그 출력'),
        '',
    ]
    for category, title in labels:
        rows = grouped.get(category, [])
        lines.append(f'[{title}] {len(rows)}개')
        if not rows:
            lines.append('- 없음')
        for row in rows:
            details = []
            if row.get('translated'):
                details.append(f"번역 {row['translated']}개")
            if row.get('unmatched'):
                details.append(f"미대응 {row['unmatched']}개")
            if row.get('provider'):
                details.append(f"원본 모드: {row['provider']}")
            suffix = ' · ' + ' · '.join(details) if details else ''
            lines.append(f"- {row['path']}{suffix}")
        lines.append('')
    lines.extend([
        ('개발용 시험에서는 신규 플러그인 자동 상속을 사용하지 않습니다.'
         if report.get('channel') == 'development' else
         '신규 플러그인 자동 상속은 FalloutNV.esm 및 공식 DLC ESM의 검증된 번역만 사용합니다.'),
        '원 소유자, FormID, 레코드 타입, 필드 경로, 현재 영문 원문이 모두 일치할 때만 번역합니다.',
        '모드가 원문을 변경한 레코드는 자동 번역하지 않습니다.',
        '프로필은 읽기 전용이며 modlist.txt·plugins.txt·loadorder.txt를 생성하거나 변경하지 않습니다.',
        'Output의 번역 파일만 복사하고, 필요한 한국어 모드·플러그인은 MO2에서 직접 활성화하세요.',
        '',
    ])
    return '\n'.join(lines)


def stable_context(obj, pointer):
    """Use setting bindings when present; otherwise MCM's persistent object ID."""
    current, bound = obj, None
    for depth, part in enumerate(pointer[:-1]):
        current = current[part]
        if isinstance(current, dict) and isinstance(current.get('vars'), list):
            refs = [{k: value[k] for k in ('configINI', 'form', 'numVar', 'strVar') if k in value}
                    for value in current['vars'] if isinstance(value, dict)]
            if refs and any(refs):
                bound = (refs, pointer[depth + 1:])
    identity = ['binding', *bound] if bound else ['pointer', pointer]
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def ini_rows(text):
    section = ''
    for index, line in enumerate(text.splitlines(keepends=True)):
        body = line.rstrip('\r\n')
        stripped = body.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section = stripped
        if not stripped or stripped.startswith((';', '#', '[')) or '=' not in body:
            continue
        lhs, rhs = body.split('=', 1)
        value = rhs.strip()
        quoted = len(value) >= 2 and value.startswith('"') and value.endswith('"')
        source = value[1:-1] if quoted else value
        if source:
            yield {'line': index, 'section': section, 'key': lhs.strip(), 'source': source}


def check_pair(source, dest):
    if not isinstance(dest, str) or not dest or '\n' in dest or '\r' in dest:
        raise ValueError('Invalid translation text')
    if Counter(TOKEN.findall(source)) != Counter(TOKEN.findall(dest)):
        raise ValueError('Translation changes protected tokens')
    import re
    prefix = re.match(r'#\d+\|', source)
    if prefix and not dest.startswith(prefix.group()):
        raise ValueError('Translation moves message prefix')


def make_catalog(workspace, work_dir, output, plugin_maps=None, plugin_fields=None):
    """Package text mappings and user-completed plugins, not proprietary originals."""
    if output.exists():
        raise FileExistsError(output)
    work = nskr.read_json(work_dir / 'work.json')
    translations = nskr.read_json(work_dir / 'translations.json')
    baseline = nskr.read_json(workspace / 'source_manifest.json')
    base_plugins = {row['data_path'].casefold(): row for row in baseline['files']
                    if row['category'] == '01_Plugins'}
    files, payloads, rejected = [], [], []
    native = nskr.read_json(plugin_maps) if plugin_maps else None
    if native and not plugin_fields:
        raise ValueError('Native mappings require the verified plugin display schema')
    for info in work['files']:
        original = workspace / info['path']
        if nskr.sha256(original) != info['sha256']:
            raise ValueError(f'Translation source changed: {original}')
        parts = Path(info['path']).parts
        relative = nskr.virtual_path(Path(*parts[2:]).as_posix())
        text, _ = decode(original)
        obj = json.loads(text) if original.suffix.lower() == '.json' else None
        mappings = []
        for entry in work['entries']:
            if entry['path'] != info['path']:
                continue
            dest = translations[entry['id']]
            check_pair(entry['source'], dest)
            row = {'source': entry['source'], 'dest': dest}
            if obj is not None:
                row['context'] = stable_context(obj, entry['pointer'])
            else:
                row.update(section=entry['section'], key=entry['key'])
            mappings.append(row)
        files.append({'path': relative, 'kind': 'json' if obj is not None else 'ini',
                      'original_provider': parts[1], 'baseline_sha256': info['sha256'],
                      'mappings': mappings})
    for plugin in sorted((workspace / '01_Plugins/번역 완료').glob('*')):
        if plugin.suffix.casefold() not in {'.esp', '.esm'}:
            continue
        reference = base_plugins[plugin.name.casefold()]
        if native:
            accepted = []
            for row in native['mappings'][plugin.name]:
                try:
                    nskr_xedit.validate_mapping(row)
                except ValueError as error:
                    rejected.append({'plugin': plugin.name, **row, 'reason': str(error)})
                else:
                    accepted.append(row)
            files.append({'path': plugin.name, 'kind': 'plugin-records',
                          'baseline_sha256': reference['sha256'], 'mappings': accepted,
                          'review': 'user_completed_texts; output_structure_readback_required',
                          'input_validation_scope': native.get('validation_scope', 'native_nontext_comparison')})
            continue
        payload = f'plugins/{plugin.name}'
        files.append({'path': plugin.name, 'kind': 'plugin-copy',
                      'baseline_sha256': reference['sha256'],
                      'payload': payload, 'payload_sha256': nskr.sha256(plugin),
                      'review': 'user_completed; record_validation_pending'})
        payloads.append((plugin, payload))
    # User-completed optional copies stay in their own installed provider folders.
    # Inactive variants are translated without enabling them or changing profiles.
    for number, reference in enumerate(row for row in baseline['files'] if row['category'] == '99_Optional_Plugins'):
        plugin = workspace / reference['output']
        if not plugin.is_file():
            continue
        if native:
            optional_key = f"{reference['provider']}/{reference['data_path']}"
            optional_rows = native.get('optional_mappings', {}).get(optional_key)
            if optional_rows is None:
                raise ValueError(f'Missing optional record mappings: {optional_key}')
            accepted = []
            for row in optional_rows:
                try:
                    nskr_xedit.validate_mapping(row)
                except ValueError as error:
                    rejected.append({'plugin': plugin.name, 'provider': reference['provider'], **row, 'reason': str(error)})
                else:
                    accepted.append(row)
            files.append({'path': nskr.virtual_path(reference['data_path']), 'kind': 'plugin-records',
                          'provider': nskr.virtual_path(reference['provider']), 'optional': True,
                          'baseline_sha256': reference['sha256'], 'mappings': accepted,
                          'review': 'user_completed_texts; output_structure_readback_required'})
            continue
        payload = f'optional/{number}/{plugin.name}'
        files.append({'path': nskr.virtual_path(reference['data_path']), 'kind': 'plugin-copy',
                      'provider': nskr.virtual_path(reference['provider']), 'optional': True,
                      'baseline_sha256': reference['sha256'],
                      'payload': payload, 'payload_sha256': nskr.sha256(plugin),
                      'review': 'user_completed; record_validation_pending'})
        payloads.append((plugin, payload))
    if not files:
        raise ValueError('No translation data')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.nskr-catalog-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'catalog'
        stage.mkdir()
        for source, relative in payloads:
            target = nskr.contained(stage, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        metadata = {'schema_version': SCHEMA, 'files': files,
            'updated_plugin_backend': 'Python ctypes + XEditLib' if native else 'not_available',
            'game_validation': 'not_run'}
        if native:
            metadata['plugin_fields'] = nskr.read_json(plugin_fields)['fields']
            metadata['mapping_review'] = native.get('report', [])
            metadata['input_validation_scope'] = native.get('validation_scope', 'native_nontext_comparison')
            metadata['output_verification'] = 'fresh_native_readback_required'
            metadata['rejected_mappings'] = rejected
        nskr.write_json(stage / 'catalog.json', metadata)
        stage.rename(output)
    return {'files': len(files), 'catalog': str(output)}


def translation_companion(installation, virtual):
    """MCM/Name.json is kept original when MCM/Translations/Name.ini exists."""
    path = Path(nskr.virtual_path(virtual))
    if path.suffix.casefold() != '.json' or path.parent.as_posix().casefold() != 'mcm':
        return None
    companion = f'MCM/Translations/{path.stem}.ini'
    chain = installation.providers.get(companion.casefold())
    return chain[-1]['path'] if chain else None


def merge_loose(source, entry):
    text, encoding = decode(source)
    matches = defaultdict(set)
    for row in entry['mappings']:
        check_pair(row['source'], row['dest'])
        identity = row['context'] if entry['kind'] == 'json' else (row['section'], row['key'])
        matches[(identity, row['source'])].add(row['dest'])
    missing, translated, unchanged = [], 0, 0
    approved_identities = {identity for identity, source in matches}
    replacements = {}
    if entry['kind'] == 'json':
        obj = json.loads(text)
        items = [{'pointer': list(pointer), 'source': value,
                  'context': stable_context(obj, list(pointer))} for pointer, value in json_values(obj)]
    else:
        items = list(ini_rows(text))
        lines = text.splitlines(keepends=True)
    for item in items:
        identity = item['context'] if entry['kind'] == 'json' else (item['section'], item['key'])
        if entry.get('display_mappings_only') and identity not in approved_identities:
            unchanged += 1
            continue
        destinations = matches.get((identity, item['source']), set())
        if len(destinations) != 1:
            missing.append({**item, 'reason': 'ambiguous' if destinations else 'unmatched'})
            continue
        dest = next(iter(destinations))
        if dest == item['source']:
            unchanged += 1
            continue
        translated += 1
        if entry['kind'] == 'json':
            replacements[tuple(item['pointer'])] = dest
        else:
            line = lines[item['line']]
            newline = '\r\n' if line.endswith('\r\n') else ('\n' if line.endswith('\n') else '')
            body = line[:-len(newline)] if newline else line
            lhs, rhs = body.split('=', 1)
            lead, trail = rhs[:len(rhs) - len(rhs.lstrip())], rhs[len(rhs.rstrip()):]
            quoted = rhs.strip().startswith('"') and rhs.strip().endswith('"')
            lines[item['line']] = lhs + '=' + lead + ('"' + dest + '"' if quoted else dest) + trail + newline
    result = (render_json(text, replacements)
              if entry['kind'] == 'json' else ''.join(lines))
    return result.encode(encoding), {'translated': translated, 'unchanged_by_design': unchanged,
                                   'unmatched': len(missing), 'unmatched_entries': missing}


def fixed_esm_mod(installation):
    """Return the enabled MO2 mod folder that provides FalloutNV.esm."""
    chain = installation.providers.get('falloutnv.esm', [])
    if not chain:
        raise ValueError('Enabled Fixed ESMs provider for FalloutNV.esm was not found')
    provider_file = Path(chain[-1]['physical']).resolve()
    if not provider_file.is_relative_to(installation.mods):
        raise ValueError('FalloutNV.esm is not provided by the enabled Fixed ESMs mod in the configured MO2 Mods directory')
    relative = provider_file.relative_to(installation.mods)
    if len(relative.parts) < 2:
        raise ValueError('Invalid Fixed ESMs provider path')
    return relative.parts[0]


def source_for_plugin(installation, plugin):
    """Resolve the effective MO2/VFS source with VNV-specific official-master rules."""
    key = plugin.casefold()
    chain = installation.providers.get(key)
    if chain:
        source = installation.source(plugin)
        provider = chain[-1]['provider']
        if key in FIXED_ESM_MASTERS and not installation.is_ttw and source.resolve().is_relative_to(installation.data.resolve()):
            raise ValueError(
                f'{plugin} is coming from raw game Data. '
                'A normal VNV install must provide this core/DLC master from Fixed ESMs.')
        return source, provider
    if key in STARTER_PACK_MASTERS:
        source = (installation.data / plugin).resolve()
        if source.is_file():
            return source, 'game:Data'
    raise ValueError(f'No enabled translation source: {plugin}')


def destination(installation, source, virtual=None):
    """Map a physical provider to the portable manual-copy Output tree."""
    resolved = source.resolve()
    if resolved.is_relative_to(installation.mods):
        relative = resolved.relative_to(installation.mods)
        return nskr.virtual_path((Path('mods') / relative).as_posix())
    if resolved.is_relative_to(installation.overwrite):
        relative = resolved.relative_to(installation.overwrite)
        return nskr.virtual_path((Path('overwrite') / relative).as_posix())
    if virtual and resolved.is_relative_to(installation.data.resolve()):
        # The four Courier's Stash pack ESMs are normally only in the real game
        # Data directory. Never overwrite Data: publish translated copies into
        # the enabled Fixed ESMs mod so MO2 wins them at runtime.
        return nskr.virtual_path(f'mods/Nuclear Sunset Korean - Base Masters/{virtual}')
    if resolved.is_relative_to(installation.root):
        return nskr.virtual_path(resolved.relative_to(installation.root).as_posix())
    raise ValueError(f'Source is outside the configured MO2 storage; cannot mirror it in Output: {source}')


def verified_delta(entry, catalog_dir, source):
    spec = entry.get('verified_delta')
    if not spec:
        return None
    for key in ('source_sha256', 'target_sha256', 'payload_sha256'):
        if not isinstance(spec.get(key), str) or not nskr.HASH.fullmatch(spec[key]):
            raise ValueError(f'Invalid verified delta metadata: {entry["path"]}')
    if type(spec.get('target_size')) is not int or spec['target_size'] < 0:
        raise ValueError(f'Invalid verified delta size: {entry["path"]}')
    current_hash = nskr.sha256(source)
    if current_hash == spec['target_sha256'] and source.stat().st_size == spec['target_size']:
        return {'mode': 'already_patched', 'spec': spec}
    if current_hash != spec['source_sha256']:
        return None
    patch = nskr.contained(catalog_dir, spec['payload'])
    if nskr.sha256(patch) != spec['payload_sha256']:
        raise ValueError(f'Verified delta integrity mismatch: {entry["path"]}')
    return {'mode': 'delta', 'patch': patch, 'spec': spec}


def output_catalog(catalog, development=False, scopes=None, only_plugins=None):
    """Keep release approval separate from explicit, limited development tests."""
    if catalog.get('schema_version') != SCHEMA or catalog.get('target_modlist') != 'nuclear-sunset-ttw':
        raise ValueError('Nuclear Sunset용 번역 데이터가 필요합니다.')
    if not development:
        if catalog.get('translation_ready') is not True or catalog.get('channel') == 'development':
            raise ValueError('Nuclear Sunset용 검증된 번역 데이터가 필요합니다. 정식 출력은 아직 차단되어 있습니다.')
        if scopes is not None or only_plugins:
            raise ValueError('범위 선택은 개발용 출력에서만 지원합니다.')
        return catalog
    if catalog.get('channel') != 'development' or catalog.get('translation_ready') is not False:
        raise ValueError('명시적인 미배포 개발용 카탈로그가 필요합니다.')
    selected = set(scopes if scopes is not None else ('ui', 'fonts'))
    if not selected or selected - {'ui', 'fonts', 'plugins'}:
        raise ValueError('번역 범위를 하나 이상 올바르게 선택해주세요.')
    result = dict(catalog)
    result['selected_scopes'] = sorted(selected)
    result.pop('asset_bundle', None)
    if 'ui' not in selected:
        result.pop('runtime_mods', None)
    elif any(spec.get('review_status') not in {
                 'validated_gmst_only_candidate', 'snapshot_verified_caption_candidate',
                 'validated_runtime_dictionary_candidate'}
             for spec in result.get('runtime_mods', [])):
        raise ValueError('출처가 확인되지 않은 UI·라디오 시험 데이터입니다.')
    if 'fonts' not in selected:
        result.pop('font_bundle', None)
    files = []
    for entry in catalog.get('files', []):
        kind = entry.get('kind')
        if kind in {'json', 'ini'} and 'ui' in selected:
            if entry.get('review_status') != 'ui_reviewed':
                raise ValueError('검수되지 않은 MCM/INI 데이터입니다.')
            files.append(entry)
        elif kind == 'plugin-records' and 'plugins' in selected:
            full = catalog.get('full_translation_catalog') is True
            allowed_origins = ({'sst_direct', 'gemini_candidate', 'ttw_donor',
                                'base_translation_inherited'} if full else {'sst_direct'})
            expected_review = 'source_matched_candidate' if full else 'existing_sst_candidate'
            if (entry.get('review_status') != expected_review
                    or catalog.get('strict_plugin_paths') is not True
                    or any(not row.get('path') or row.get('origin') not in allowed_origins
                           for row in entry.get('mappings', []))):
                raise ValueError('번역 시험은 현재 원문과 정확한 레코드 경로로 대응된 데이터만 허용합니다.')
            files.append(entry)
        elif kind not in {'json', 'ini', 'plugin-records'}:
            raise ValueError('개발용 출력에 허용되지 않는 데이터 종류입니다.')
    if only_plugins:
        wanted = {name.casefold() for name in only_plugins}
        available = {entry['path'].casefold() for entry in files if entry['kind'] == 'plugin-records'}
        if 'plugins' not in selected or wanted - available:
            raise ValueError('요청한 SST 시험 플러그인이 카탈로그에 없습니다.')
        files = [entry for entry in files if entry['kind'] != 'plugin-records'
                 or entry['path'].casefold() in wanted]
    result['files'] = files
    if not files and not result.get('font_bundle'):
        raise ValueError('선택한 범위에 출력할 번역 데이터가 없습니다.')
    return result


def original_installation(installation, excluded):
    """Ignore explicitly named test overlays in memory, never change a profile."""
    result = copy(installation)
    excluded = set(excluded)
    result.mods_enabled = [x for x in installation.mods_enabled if x not in excluded]
    result.providers = {key: filtered for key, chain in installation.providers.items()
                        if (filtered := [x for x in chain if x["provider"] not in excluded])}
    return result


def installed_catalog(installation, catalog):
    """Expand known translations to every installed physical mod variant."""
    result = copy(installation)
    excluded = set(catalog.get('excluded_test_providers', []))
    excluded.update(spec['mod'] for spec in catalog.get('runtime_mods', []))
    if catalog.get('font_bundle'):
        excluded.add(catalog['font_bundle']['default_mod'])
    result = original_installation(result, excluded)
    result.providers = {key: list(chain) for key, chain in result.providers.items()}
    entries, seen = [], set()
    variants = {(entry['path'].casefold(), entry['provider']): entry
                for entry in catalog['files'] if entry.get('optional')}
    for entry in catalog['files']:
        key = entry['path'].casefold()
        chain = result.providers.get(key, [])
        if entry.get('optional'):
            chain = [row for row in chain if row['provider'] == entry['provider']]
        elif chain:
            preferred = next((row for row in chain if row['provider'] == entry.get('provider')), chain[-1])
            chain = [row for row in chain if row is not preferred] + [preferred]
            result.providers[key] = chain
        for row in chain:
            # Raw Data is a fallback only; installed mod copies are all retained.
            if row['provider'] == 'game:Data' and len(chain) > 1:
                continue
            identity = (key, row['provider'])
            if identity in seen:
                continue
            seen.add(identity)
            item = dict(variants.get(identity, entry))
            item['provider'] = row['provider']
            if row is not chain[-1] or entry.get('optional'):
                item['optional'] = True
            elif not entry.get('optional'):
                item.pop('optional', None)
            entries.append(item)
        if not chain and not entry.get('optional'):
            entries.append(entry)
    result.active = [chain[-1]['path'] for chain in result.providers.values()
                     if chain[-1]['category'] == 'plugin']
    result.active_keys = {name.casefold() for name in result.active}
    return result, {**catalog, 'files': entries}


def build_output(installation, catalog_dir, output, progress=None, *,
                 development=False, scopes=None, only_plugins=None):
    output = output.resolve()
    installation.guard_output(output)
    # This interface prepares manual overwrite files outside MO2, never a live mod.
    if output.is_relative_to(installation.root) or output.is_relative_to(installation.mods):
        raise ValueError('Output must be outside the MO2 installation and mods directories')
    report_path = output.with_name(output.name + '.report.json')
    report_text_path = output.with_name(output.name + '.report.txt')
    if report_path.exists():
        raise FileExistsError(report_path)
    if report_text_path.exists():
        raise FileExistsError(report_text_path)
    catalog = output_catalog(nskr.read_json(catalog_dir / 'catalog.json'),
                             development, scopes, only_plugins)
    if development and catalog.get('full_translation_catalog'):
        installation = original_installation(installation, catalog.get('excluded_test_providers', []))
    if getattr(installation, 'all_installed', False):
        installation, catalog = installed_catalog(installation, catalog)
    if development and not {'fallout3.esm', 'taleoftwowastelands.esm'}.issubset(installation.active_keys):
        raise ValueError('선택한 프로필에서 Fallout 3 및 TTW 마스터를 확인할 수 없습니다.')
    # Optional providers may deliberately contain the same virtual plugin name.
    if catalog['files'] or not (catalog.get('font_bundle') or catalog.get('asset_bundle')):
        nskr.validate_entries([{'path': (f"optional/{nskr.virtual_path(e['provider'])}/{e['path']}"
                                         if e.get('optional') else f"active/{e['path']}")}
                               for e in catalog['files']])

    def emit(message):
        if progress:
            progress(message)

    emit('설치된 전체 번역 대상의 원본을 확인하고 있습니다.'
         if getattr(installation, 'all_installed', False)
         else f'Nuclear Sunset 프로필 "{installation.profile}"의 현재 원본을 확인하고 있습니다.')
    inheritance_memory = [] if development else base_translation_memory(catalog)
    if inheritance_memory:
        inherited_entries, discovery_skipped = discover_new_plugin_entries(installation, catalog)
    else:
        inherited_entries, discovery_skipped = [], []
    work_entries = [*catalog['files'], *inherited_entries]
    # Every non-official plugin may inherit exact vanilla/DLC strings that it
    # overrides. Direct SST mappings still take priority inside the worker.
    fallback_targets = {
        entry['path'] for entry in work_entries
        if entry.get('kind') == 'plugin-records'
        and entry['path'].casefold() not in BASE_TRANSLATION_MASTERS
    }

    report = {'mo2_root': str(installation.root), 'profile': installation.profile,
              'target_scope': ('all_installed_catalog_providers'
                               if getattr(installation, 'all_installed', False) else 'selected_profile'),
              'channel': 'development' if development else 'release',
              'translation_ready': not development,
              'selected_scopes': catalog.get('selected_scopes'),
              'output': str(output), 'created_utc': datetime.now(timezone.utc).isoformat(),
              'files': [], 'skipped': list(discovery_skipped), 'warnings': installation.warnings,
              'install_state': 'manual_copy_required', 'game_validation': 'not_run',
              'updated_plugin_backend': catalog.get('updated_plugin_backend', 'not_available'),
              'auto_inheritance': {
                  'enabled': bool(inheritance_memory),
                  'source_masters': sorted(BASE_TRANSLATION_MASTERS),
                  'translation_memory_rows': len(inheritance_memory),
                  'discovered_active_plugins': len(inherited_entries) + len(discovery_skipped),
                  'safety': 'owner+FormID+signature+field+exact_path+current_source must match',
              }}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.nskr-output-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'Output'
        stage.mkdir()
        seen = set()
        active_native = [entry for entry in work_entries if entry['kind'] == 'plugin-records'
                         and not entry.get('optional')
                         and entry['path'].casefold() in installation.active_keys
                         and (entry['path'].casefold() in installation.providers
                              or (entry['path'].casefold() in STARTER_PACK_MASTERS
                                  and (installation.data / entry['path']).is_file()))]
        fast_native = {}
        for entry in active_native:
            source, _provider = source_for_plugin(installation, entry['path'])
            fast = verified_delta(entry, catalog_dir, source)
            if fast:
                fast_native[entry['path'].casefold()] = fast
        native_entries = [entry for entry in active_native if entry['path'].casefold() not in fast_native]
        native_files, native_stats = (None, {})
        if native_entries:
            emit(f'플러그인 {len(native_entries)}개에 SST 번역을 적용합니다.')
            native_target_names = {entry['path'] for entry in native_entries}
            starter_overrides = {
                entry['path']: (installation.data / entry['path']).resolve()
                for entry in native_entries
                if entry['path'].casefold() in STARTER_PACK_MASTERS
                and entry['path'].casefold() not in installation.providers
            }
            native_files, native_stats = nskr_xedit.merge_plugins(
                installation, native_entries, catalog, Path(tmp) / 'NativeJob',
                source_overrides=starter_overrides,
                fallback_mappings=inheritance_memory,
                fallback_targets=fallback_targets & native_target_names,
                progress=progress)
        optional_native = {}
        if getattr(installation, 'all_installed', False):
            pending = [entry for entry in work_entries
                       if entry['kind'] == 'plugin-records' and entry.get('optional')
                       and not verified_delta(entry, catalog_dir,
                                              nskr.contained(installation.mods, f"{entry['provider']}/{entry['path']}"))]
            batch_number = 0
            while pending:
                batch, rest, names = [], [], set()
                for entry in pending:
                    key = entry['path'].casefold()
                    if key in names:
                        rest.append(entry)
                    else:
                        names.add(key)
                        batch.append(entry)
                overrides = {entry['path']: nskr.contained(
                    installation.mods, f"{entry['provider']}/{entry['path']}") for entry in batch}
                files, stats = nskr_xedit.merge_plugins(
                    installation, batch, catalog, Path(tmp) / f'InstalledVariants{batch_number}',
                    source_overrides=overrides, fallback_mappings=inheritance_memory,
                    fallback_targets=fallback_targets & set(overrides), progress=progress)
                for entry in batch:
                    optional_native[(entry['path'].casefold(), entry['provider'])] = (
                        files / entry['path'], stats[entry['path']])
                pending = rest
                batch_number += 1
        delta_engine = None
        for entry in work_entries:
            key = entry['path'].casefold()
            chain = installation.providers.get(key)
            if entry.get('optional'):
                allowed = {'plugin-copy', 'plugin-records'}
                if getattr(installation, 'all_installed', False):
                    allowed.update({'json', 'ini'})
                if entry['kind'] not in allowed or '/' in nskr.virtual_path(entry['provider']):
                    raise ValueError('Invalid optional provider')
                source = nskr.contained(installation.mods, f"{entry['provider']}/{entry['path']}")
                chain = [{'provider': entry['provider']}]
                if not source.is_file():
                    report['skipped'].append({'path': entry['path'], 'provider': entry['provider'], 'reason': 'not_installed'})
                    continue
            else:
                if entry['kind'] in {'plugin-copy', 'plugin-records'} and key not in installation.active_keys:
                    report['skipped'].append({'path': entry['path'], 'reason': 'not_enabled'})
                    continue
                if not chain:
                    if key in STARTER_PACK_MASTERS and (installation.data / entry['path']).is_file():
                        source = (installation.data / entry['path']).resolve()
                        chain = [{'provider': 'game:Data'}]
                    elif key in FIXED_ESM_MASTERS:
                        raise ValueError(
                            f'{entry["path"]} has no enabled MO2 provider. '
                            'VNV core/DLC ESMs must come from the enabled Fixed ESMs mod.')
                    else:
                        report['skipped'].append({'path': entry['path'], 'reason': 'not_installed'})
                        continue
                else:
                    if entry['kind'] in {'plugin-copy', 'plugin-records'}:
                        source, _resolved_provider = source_for_plugin(installation, entry['path'])
                    else:
                        source = installation.source(entry['path'])
            original_hash = nskr.sha256(source)
            if development and entry['kind'] in {'json', 'ini'}:
                if (original_hash != entry['baseline_sha256']
                        or chain[-1]['provider'] != entry['provider']) and not getattr(installation, 'all_installed', False):
                    report['skipped'].append({'path': entry['path'],
                                             'reason': 'reviewed_ui_source_or_provider_changed',
                                             'translation_applied': False})
                    continue
            relative = destination(installation, source, entry['path'])
            if relative.casefold() in seen:
                raise ValueError(f'Duplicate physical output: {relative}')
            seen.add(relative.casefold())
            target = nskr.contained(stage, relative)
            result = {'path': entry['path'], 'output_path': relative,
                      'provider': chain[-1]['provider'], 'source_sha256': original_hash,
                      'source_updated': original_hash != entry['baseline_sha256']}
            if entry.get('auto_inherited'):
                result.update(discovered_plugin=True, translation_source='base_dlc_sst_fallback')
            if entry['kind'] == 'plugin-records':
                fast = (verified_delta(entry, catalog_dir, source) if entry.get('optional')
                        else fast_native.get(key))
                if fast:
                    spec = fast['spec']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if fast['mode'] == 'already_patched':
                        shutil.copyfile(source, target)
                        status = 'already_patched_verified'
                    else:
                        patch = fast['patch']
                        if delta_engine is None:
                            delta_engine = nskr.engine(None)
                        nskr.delta(delta_engine, 'decode', source, patch, target)
                        if target.stat().st_size != spec['target_size'] or nskr.sha256(target) != spec['target_sha256']:
                            raise ValueError(f'Verified delta output mismatch: {entry["path"]}')
                        status = 'exact_source_verified_delta'
                    statistics = {'translated': spec.get('translated', len(entry['mappings'])),
                                  'unmatched': spec.get('unmatched', 0),
                                  'records_verified': spec.get('records_verified', 0),
                                  'verification': spec.get('verification', 'verified_delta_roundtrip')}
                    result.update(statistics, status=status)
                else:
                    if (key, entry.get('provider')) in optional_native:
                        native_source, statistics = optional_native[(key, entry['provider'])]
                    elif entry.get('optional'):
                        # A same-name inactive variant gets its own copied session.
                        # Never swap a live provider or alter profile activation.
                        emit(f'선택 플러그인 {entry["path"]}을(를) 레코드 단위로 처리합니다.')
                        optional_files, optional_stats = nskr_xedit.merge_plugins(
                            installation, [entry], catalog, Path(tmp) / f'OptionalJob{len(seen)}',
                            source_overrides={entry['path']: source},
                            fallback_mappings=inheritance_memory,
                            fallback_targets=({entry['path']}
                                              if entry['path'].casefold() not in BASE_TRANSLATION_MASTERS
                                              else set()),
                            progress=progress)
                        native_source, statistics = optional_files / entry['path'], optional_stats[entry['path']]
                    else:
                        native_source, statistics = native_files / entry['path'], native_stats[entry['path']]
                    if entry.get('auto_inherited') and statistics.get('translated', 0) == 0:
                        report['skipped'].append({
                            **result, **statistics,
                            'reason': 'new_plugin_no_base_translation_match',
                            'base_record_mismatches': statistics.get('unmatched', 0),
                            'translation_applied': False,
                        })
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(native_source, target)
                    status = ('auto_inherited_base_dlc_sst; native_readback_verified'
                              if entry.get('auto_inherited')
                              else 'sst_matched_text_only; native_readback_verified')
                    result.update(statistics, status=status)
            elif entry['kind'] == 'plugin-copy':
                payload = nskr.contained(catalog_dir, entry['payload'])
                if nskr.sha256(payload) != entry['payload_sha256']:
                    raise ValueError(f'Plugin payload integrity mismatch: {entry["path"]}')
                if original_hash != entry['baseline_sha256']:
                    report['skipped'].append({**result, 'reason': 'updated_plugin_needs_record_backend',
                                             'translation_applied': False})
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(payload, target)
                result['status'] = 'user_completed_copy; record_validation_pending'
            elif entry['kind'] in {'ini', 'json'}:
                if getattr(installation, 'all_installed', False):
                    path = Path(entry['path'])
                    companion_file = source.parent / 'Translations' / (path.stem + '.ini')
                    companion = (f'MCM/Translations/{path.stem}.ini'
                                 if path.parent.as_posix().casefold() == 'mcm'
                                 and path.suffix.casefold() == '.json'
                                 and companion_file.is_file() else None)
                else:
                    companion = translation_companion(installation, entry['path'])
                if companion:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
                    result.update(translated=0, unmatched=0,
                                  status='original_json_preserved_translation_companion',
                                  translation_companion=companion)
                    if nskr.sha256(source) != original_hash:
                        raise ValueError(f'Source changed during generation: {source}')
                    result['output_sha256'] = nskr.sha256(target)
                    report['files'].append(result)
                    continue
                raw, stats = merge_loose(source, entry)
                if (development and stats['unmatched']
                        and not (catalog.get('full_translation_catalog')
                                 and entry.get('updated_source_exact_matches_only'))):
                    raise ValueError(f'검수된 UI 번역 대응 실패: {entry["path"]}')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                result.update(stats, status='merged_into_current_source')
            else:
                raise ValueError(f'Unsupported translation kind: {entry["kind"]}')
            if nskr.sha256(source) != original_hash:
                raise ValueError(f'Source changed during generation: {source}')
            result['output_sha256'] = nskr.sha256(target)
            report['files'].append(result)
        if catalog.get('font_bundle'):
            font_files, font_status = nskr_fonts.build_fonts(installation, catalog_dir,
                                                            catalog['font_bundle'], stage, seen)
            report['files'].extend(font_files)
            report['fonts'] = font_status
        if catalog.get('asset_bundle'):
            asset_files, asset_status = build_assets(installation, catalog_dir, catalog['asset_bundle'], stage, seen,
                                                    report.get('fonts', {}).get('mod'))
            report['files'].extend(asset_files)
            report['assets'] = asset_status
        if catalog.get('runtime_mods'):
            runtime_files, runtime_status = build_runtime_mods(installation, catalog_dir, catalog['runtime_mods'], stage, seen)
            report['files'].extend(runtime_files)
            report['runtime_mods'] = runtime_status
        if not report['files']:
            raise ValueError('No applicable translation files; no Output was published')
        report['plugin_outcomes'] = plugin_outcomes(report)
        report['report_json'] = str(report_path)
        report['report_text'] = str(report_text_path)
        # Read back every artifact before publishing the tree.
        for row in report['files']:
            if nskr.sha256(nskr.contained(stage, row['output_path'])) != row['output_sha256']:
                raise ValueError('Output readback failed')
        stage.rename(output)
    nskr.write_json(report_path, report)
    report_text_path.write_text(format_plugin_report(report), encoding='utf-8-sig')
    return report

def build_runtime_mods(installation, catalog_dir, specs, stage, seen):
    """Publish small Korean runtime mods that do not replace existing VNV providers."""
    files, activate_mods, activate_plugins = [], set(), set()
    for spec in specs:
        mod = nskr.virtual_path(spec['mod'])
        if '/' in mod:
            raise ValueError('Invalid runtime mod folder')
        if mod not in installation.mods_enabled:
            activate_mods.add(mod)
        for plugin in spec.get('plugins', []):
            activate_plugins.add(nskr.virtual_path(plugin))
        for entry in spec['files']:
            relative = nskr.virtual_path(entry['path'])
            payload = nskr.contained(catalog_dir, entry['payload'])
            if nskr.sha256(payload) != entry['payload_sha256']:
                raise ValueError(f'Runtime payload integrity mismatch: {mod}/{relative}')
            output_path = f'mods/{mod}/{relative}'
            if output_path.casefold() in seen:
                raise ValueError(f'Duplicate runtime output: {output_path}')
            seen.add(output_path.casefold())
            target = nskr.contained(stage, output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(payload, target)
            files.append({'path': relative, 'output_path': output_path, 'provider': mod,
                          'source_sha256': None, 'output_sha256': nskr.sha256(target),
                          'status': 'runtime_mod_copy'})
    return files, {'mods_requiring_activation': sorted(activate_mods),
                   'plugins_requiring_activation': sorted(activate_plugins),
                   'game_validation': 'not_run'}


def build_assets(installation, catalog_dir, spec, stage, seen, fallback_provider=None):
    """Mirror the current loose asset provider, or use the Korean font overlay."""
    default = nskr.virtual_path(fallback_provider or spec['default_mod'])
    if '/' in default:
        raise ValueError('Invalid asset mod folder')
    files, activation = [], set()
    for entry in spec['files']:
        relative = nskr.virtual_path(entry['path'])
        if not relative.casefold().startswith('textures/') or Path(relative).suffix.casefold() != '.dds':
            raise ValueError('Unexpected translated texture path')
        payload = nskr.contained(catalog_dir, entry['payload'])
        if nskr.sha256(payload) != entry['payload_sha256']:
            raise ValueError('Texture payload integrity mismatch')
        candidates = [nskr.contained(installation.mods, f'{name}/{relative}')
                      for name in reversed(installation.mods_enabled)]
        candidates.insert(0, nskr.contained(installation.overwrite, relative))
        source = next((p for p in candidates if p.is_file()), None)
        if source:
            output_path = destination(installation, source, relative)
            provider = (source.relative_to(installation.mods).parts[0]
                        if source.is_relative_to(installation.mods) else 'MO2:overwrite')
        else:
            provider, output_path = default, f'mods/{default}/{relative}'
            if default not in installation.mods_enabled:
                activation.add(default)
        if output_path.casefold() in seen:
            raise ValueError(f'Duplicate asset output: {output_path}')
        seen.add(output_path.casefold())
        before = nskr.sha256(source) if source else None
        target = nskr.contained(stage, output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(payload, target)
        if source and nskr.sha256(source) != before:
            raise ValueError('Texture source changed during generation')
        files.append({'path': relative, 'output_path': output_path, 'provider': provider,
                      'source_sha256': before, 'output_sha256': nskr.sha256(target),
                      'status': 'translated_texture_copy'})
    return files, {'mods_requiring_activation': sorted(activation), 'game_validation': 'not_run'}


def main():
    parser = argparse.ArgumentParser(description='Generate a manual-copy VNV Korean Output tree')
    commands = parser.add_subparsers(dest='command', required=True)
    catalog = commands.add_parser('catalog')
    catalog.add_argument('--workspace', type=Path, required=True)
    catalog.add_argument('--work-dir', type=Path, required=True)
    catalog.add_argument('--output', type=Path, required=True)
    catalog.add_argument('--plugin-maps', type=Path)
    catalog.add_argument('--plugin-fields', type=Path)
    run = commands.add_parser('output')
    run.add_argument('--mo2-root', type=Path, required=True)
    run.add_argument('--profile')
    run.add_argument('--catalog', type=Path, required=True)
    run.add_argument('--output', type=Path, default=Path('Output'))
    args = parser.parse_args()
    if args.command == 'catalog':
        result = make_catalog(args.workspace, args.work_dir, args.output, args.plugin_maps, args.plugin_fields)
    else:
        result = build_output(nskr.Installation(args.mo2_root, args.profile), args.catalog, args.output)
        result = {'files': len(result['files']), 'skipped': len(result['skipped']),
                  'output': str(args.output.resolve()), 'report': str(args.output.resolve()) + '.report.json'}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
