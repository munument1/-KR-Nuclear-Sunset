"""Assemble local review data without approving or importing Gemini candidates."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from nskr_output import output_catalog
from nskr_xedit import validate_mapping
from tools.translation_field_policy import skip_reason


def prepare(review, sst, installation, output, runtime=None):
    if output.exists():
        raise FileExistsError(output)
    ui = nskr.read_json(review / 'catalog.json')
    validation = nskr.read_json(review / 'validation.json')
    source = nskr.read_json(sst / 'catalog.json')
    if (ui.get('translation_ready') is not False or validation.get('errors') != 0
            or validation.get('missing') != 0 or len(ui.get('files', [])) != 37):
        raise ValueError('37개 파일의 완료된 UI 검수가 필요합니다.')
    if source.get('translation_ready') is not False or source.get('target_modlist') != 'nuclear-sunset-ttw':
        raise ValueError('기존 미배포 Nuclear Sunset SST 카탈로그가 필요합니다.')
    required_checks = {'source_and_installed_hashes', 'protected_tokens', 'encoding',
                       'line_endings', 'json_reparse', 'non_display_data', 'exact_mapping'}
    if not required_checks.issubset(validation.get('checks', [])):
        raise ValueError('UI 검증 항목이 부족합니다.')
    if not {'fallout3.esm', 'taleoftwowastelands.esm'}.issubset(installation.active_keys):
        raise ValueError('선택한 프로필은 Fallout 3 + TTW 프로필이 아닙니다.')
    before = {path: nskr.sha256(path) for path in (review / 'catalog.json', sst / 'catalog.json')}
    runtime_specs = []
    if runtime is not None:
        runtime_catalog = nskr.read_json(runtime / 'catalog.json')
        if runtime_catalog.get('translation_ready') is not False:
            raise ValueError('Runtime test data must remain unreleased')
        runtime_specs = runtime_catalog['runtime_mods']
        before[runtime / 'catalog.json'] = nskr.sha256(runtime / 'catalog.json')
        for spec in runtime_specs:
            if not {x.casefold() for x in spec['required_masters']}.issubset(installation.active_keys):
                raise ValueError('한국어 UI·라디오 플러그인의 마스터가 없습니다.')
    files, counts = [], Counter()
    for info in ui['files']:
        virtual = nskr.virtual_path(info['path'])
        current = installation.source(virtual)
        if (nskr.sha256(current) != info['baseline_sha256']
                or installation.providers[virtual.casefold()][-1]['provider'] != info['provider']):
            raise ValueError(f'UI 검수 후 원본 또는 활성 provider가 바뀌었습니다: {virtual}')
        files.append({**info, 'review_status': 'ui_reviewed'})
    for info in source['files']:
        if info['kind'] != 'plugin-records':
            continue
        virtual = nskr.virtual_path(info['path'])
        if virtual.casefold() not in installation.active_keys:
            counts['inactive_plugins_excluded'] += 1
            continue
        grouped = defaultdict(list)
        for row in info['mappings']:
            if row.get('origin') != 'sst_direct':
                counts['non_sst_rows_excluded'] += 1
                continue
            if not row.get('path'):
                counts['pathless_rows_excluded'] += 1
                continue
            if skip_reason(row['signature'], row['field'], row['source']):
                counts['non_display_rows_excluded'] += 1
                continue
            try:
                validate_mapping(row)
            except ValueError:
                counts['invalid_rows_excluded'] += 1
                continue
            if not row['source'] or not row['dest'] or row['source'] == row['dest']:
                counts['unchanged_rows_excluded'] += 1
                continue
            identity = (row['owner'].casefold(), row['id'].casefold(), row['signature'],
                        row['field'], row['path'], row['source'])
            grouped[identity].append(row)
        mappings = []
        for rows in grouped.values():
            if len({r['dest'] for r in rows}) != 1:
                counts['conflicting_rows_excluded'] += len(rows)
                continue
            row = rows[0]
            mappings.append({key: row[key] for key in
                             ('owner', 'id', 'signature', 'field', 'path', 'source', 'dest', 'origin')})
        if not mappings:
            counts['empty_plugins_excluded'] += 1
            continue
        current = installation.source(virtual)
        files.append({'path': virtual, 'kind': 'plugin-records',
                      'baseline_sha256': nskr.sha256(current),
                      'review_status': 'existing_sst_candidate', 'mappings': mappings})
        counts['sst_candidate_plugins'] += 1
        counts['sst_exact_path_candidate_rows'] += len(mappings)
    catalog = {'schema_version': 1, 'target_modlist': 'nuclear-sunset-ttw',
               'translation_ready': False, 'channel': 'development',
               'strict_plugin_paths': True, 'tested_profile': installation.profile,
               'game_validation': 'not_run', 'gemini_candidates_included': False,
               'automatic_inheritance': False, 'candidate_summary': dict(counts),
               'ui_review_counts': validation['counts'], 'files': files,
               'plugin_fields': source['plugin_fields'], 'font_bundle': source['font_bundle']}
    if runtime_specs:
        catalog['runtime_mods'] = runtime_specs
    if catalog['font_bundle'].get('provider_strategy') != 'separate_mod':
        raise ValueError('한국어 폰트는 별도 오버레이 모드여야 합니다.')
    output_catalog(catalog, development=True, scopes={'ui', 'fonts', 'plugins'})
    output.mkdir(parents=True)
    payloads = [catalog['font_bundle']['ini'], catalog['font_bundle']['xml'],
                *catalog['font_bundle']['assets']]
    for item in payloads:
        original = nskr.contained(sst, item['payload'])
        if nskr.sha256(original) != item['payload_sha256']:
            raise ValueError(f'Font payload integrity mismatch: {original}')
        target = nskr.contained(output, item['payload'])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        if nskr.sha256(target) != item['payload_sha256']:
            raise ValueError('Font copy integrity mismatch')
    for spec in runtime_specs:
        for item in spec['files']:
            original = nskr.contained(runtime, item['payload'])
            if nskr.sha256(original) != item['payload_sha256']:
                raise ValueError('Runtime payload integrity mismatch')
            target = nskr.contained(output, item['payload'])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            if nskr.sha256(target) != item['payload_sha256']:
                raise ValueError('Runtime copy integrity mismatch')
    for path, digest in before.items():
        if nskr.sha256(path) != digest:
            raise ValueError(f'Source catalog changed: {path}')
    nskr.write_json(output / 'catalog.json', catalog)
    return {'catalog': str(output), 'ui_files': 37, **counts, 'translation_ready': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--sst', type=Path, required=True)
    parser.add_argument('--mo2', type=Path, required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runtime', type=Path)
    args = parser.parse_args()
    import json
    print(json.dumps(prepare(args.review, args.sst, nskr.Installation(args.mo2, args.profile),
                             args.output, args.runtime), ensure_ascii=False))


if __name__ == '__main__':
    main()
