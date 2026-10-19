"""Native XEditLib translation backend for Nuclear Sunset."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from collections import Counter

import nskr

FORMAT = re.compile(
    r'%%|(?<!\d)%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[a-zA-Z]|'
    r'</?(?:font|br|img|div|p)(?:\s[^<>]*)?/?>',
    re.IGNORECASE,
)


def validate_mapping(row):
    from collections import Counter
    if not all(isinstance(row.get(k), str)
               for k in ('owner', 'id', 'signature', 'field', 'path', 'source', 'dest')):
        raise ValueError('Invalid plugin translation mapping')
    if not re.fullmatch(r'[0-9a-f]{6}', row['id'].lower()):
        raise ValueError('Invalid plugin record FormID')
    if not re.fullmatch(r'[A-Z0-9_]{4}', row['signature']):
        raise ValueError('Invalid plugin record signature')
    if '\ufffd' in row['source'] or '\ufffd' in row['dest']:
        raise ValueError('Unresolved plugin text encoding')
    if Counter(FORMAT.findall(row['source'])) != Counter(FORMAT.findall(row['dest'])):
        raise ValueError('Plugin translation changes protected tokens')
    previous = row.get('previous_dests', [])
    if (not isinstance(previous, list)
            or any(not isinstance(value, str) or not value or '\ufffd' in value
                   or Counter(FORMAT.findall(row['source'])) != Counter(FORMAT.findall(value))
                   for value in previous)):
        raise ValueError('Invalid previous translation text')


def runtime(worker_override=None):
    if getattr(sys, 'frozen', False):
        folder = Path(sys.executable).resolve().parent
        root = (folder if (folder / 'Backend/XEditLib.dll').is_file()
                else Path(getattr(sys, '_MEIPASS', folder)).resolve())
        worker = root / 'NSKRXEditWorker.exe'
        backend = root / 'Backend'
    else:
        root = Path(__file__).resolve().parent
        worker = root / '.tools/nskr-xedit-worker/NSKRXEditWorker.exe'
        backend = root / '.tools/xeditlib-native'
    if worker_override is not None:
        worker = Path(worker_override).resolve()
    for required in (
        worker,
        backend / 'XEditLib.dll',
        backend / 'FalloutNV.Hardcoded.dat',
        backend / 'icudtl.dat',
    ):
        if not required.is_file():
            raise FileNotFoundError(f'New Vegas record backend is missing: {required}')
    return worker, backend


def _xedit_isolation_args(request, job):
    """Keep xEdit profile/cache/temp/log I/O inside the current patch job."""
    root = job / 'XEditIsolation'
    paths = {name: root / name for name in ('Saves', 'Backups', 'Cache', 'Temp', 'Scripts')}
    for directory in (root, *paths.values()):
        directory.mkdir(parents=True, exist_ok=True)
    plugins_file = root / 'plugins.txt'
    plugins_file.write_text('\n'.join(request.get('plugins', ())) + '\n', encoding='cp1252')
    game = Path(request['game'])
    return [
        f'-D:{game / "Data"}',
        f'-M:{root}{os.sep}',
        f'-I:{root / "Fallout.ini"}',
        f'-CustomIni:{root / "FalloutCustom.ini"}',
        f'-G:{paths["Saves"]}{os.sep}',
        f'-P:{plugins_file}',
        f'-B:{paths["Backups"]}{os.sep}',
        f'-C:{paths["Cache"]}{os.sep}',
        f'-T:{paths["Temp"]}{os.sep}',
        f'-S:{paths["Scripts"]}{os.sep}',
        f'-R:{root / "xelib.log"}',
    ]


def run_worker(request, job, phase, worker_override=None):
    worker, backend = runtime(worker_override)
    path = job / f'{phase}.request.json'
    nskr.write_json(path, request)
    env = os.environ.copy()
    env['NSKR_XEDIT_RUNTIME'] = str(backend)
    command = [str(worker), str(path), *_xedit_isolation_args(request, job)]
    result = subprocess.run(
        command,
        capture_output=True,
        env=env,
        timeout=1800,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )
    (job / f'{phase}.log').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        message = (result.stderr or result.stdout).decode('utf-8', errors='replace').replace('\x00', '')[-4000:]
        raise ValueError(f'New Vegas record {phase} failed: {message}')
    return nskr.read_json(Path(request['output']))


def _session_plugins(installation, entries, source_overrides):
    """Use only the load-order prefix needed by the selected targets."""
    if getattr(installation, 'all_installed', False):
        from tools.tes4_text_scan import masters
        overrides = {name.casefold(): path for name, path in (source_overrides or {}).items()}
        ordered, visiting, done = [], set(), set()

        def visit(name):
            key = name.casefold()
            if key in done:
                return
            if key in visiting:
                raise ValueError(f'Circular plugin master dependency: {name}')
            visiting.add(key)
            source = overrides.get(key) or installation.source(name)
            for master in masters(source):
                visit(master)
            visiting.remove(key)
            done.add(key)
            ordered.append(name)

        for entry in entries:
            visit(entry['path'])
        return ordered
    active = list(installation.active)
    if source_overrides:
        plugins = active[:]
        present = {name.casefold() for name in plugins}
        plugins.extend(name for name in source_overrides if name.casefold() not in present)
        return plugins
    targets = {entry['path'].casefold() for entry in entries}
    positions = [index for index, name in enumerate(active) if name.casefold() in targets]
    if len(positions) != len(targets):
        return active
    return active[:max(positions) + 1] if positions else active


def merge_plugins(installation, entries, catalog, job, source_overrides=None,
                  fallback_mappings=None, fallback_targets=None, progress=None):
    """Apply SST text to current MO2 plugins and verify one fresh UTF-8 reload.

    There is deliberately no whole-plugin CP1252 snapshot/reload pass. Direct
    SST mapping is exact; base/DLC fallback is stricter still and requires the
    same owner/FormID/signature/field/path/source before a string is changed.
    """
    runtime()
    def emit(message):
        if progress:
            progress(message)

    job.mkdir()
    game = job / 'Game'
    data = game / 'Data'
    data.mkdir(parents=True)
    source_overrides = source_overrides or {}
    fallback_mappings = fallback_mappings or []
    fallback_targets = set(fallback_targets or ())
    overrides = {name.casefold(): source for name, source in source_overrides.items()}
    plugins = _session_plugins(installation, entries, source_overrides)

    original_hashes = {}
    for plugin in plugins:
        source = overrides.get(plugin.casefold()) or installation.source(plugin)
        original_hashes[source] = nskr.sha256(source)
        shutil.copyfile(source, data / plugin)

    maps = {}
    for entry in entries:
        for row in entry.get('mappings', []):
            validate_mapping(row)
        maps[entry['path']] = entry.get('mappings', [])
    for row in fallback_mappings:
        validate_mapping(row)

    translated = job / 'Translated'
    request = {
        'game': str(game),
        'plugins': plugins,
        'targets': list(maps),
        'fields': catalog['plugin_fields'],
        'mappings': maps,
        'strictPaths': catalog.get('strict_plugin_paths', False),
        'fallbackMappings': fallback_mappings,
        'fallbackTargets': sorted(fallback_targets),
        'mode': 'apply',
        'includeRows': False,
        'outDir': str(translated),
        'output': str(job / 'apply.json'),
    }

    emit('플러그인: 원문·경로가 일치하는 번역을 적용하고 있습니다.')
    applied = run_worker(request, job, 'apply')

    expected, changes, indexes, stats = {}, {}, {}, {}
    for file in applied['files']:
        plugin = file['plugin']
        expected[plugin] = file['beforeHashes']
        changes[plugin] = file['changed']
        indexes[plugin] = file['recordIndexHash']
        inherited = sum(row.get('mappingOrigin') == 'base_dlc_sst_fallback'
                        for row in file['changed'])
        origins = Counter(row.get('mappingOrigin', 'sst_direct') for row in file['changed'])
        stats[plugin] = {
            'translated': len(file['changed']),
            'already_translated': file.get('alreadyTranslated', 0),
            'fallback_translated': inherited,
            'direct_sst_translated': origins.get('sst_direct', 0),
            'translated_by_origin': dict(origins),
            'unmatched': len(file['missing']),
            'unmatched_entries': file['missing'],
            'records_verified': len(file['beforeHashes']),
            'records_indexed': file['recordCount'],
            'translation_source': '+'.join(sorted(origins)) or 'no_changes',
        }
        shutil.copyfile(translated / plugin, data / plugin)

    request.pop('fallbackMappings', None)
    request.pop('fallbackTargets', None)
    request.pop('outDir', None)
    request.update(
        mode='verify',
        expected=expected,
        changes=changes,
        expectedHeaders={file['plugin']: file['headerHash'] for file in applied['files']},
        expectedRecordIndexes=indexes,
        output=str(job / 'verify.json'),
    )

    emit('플러그인: 저장 결과를 한 번 다시 열어 검증하고 있습니다.')
    verified = run_worker(request, job, 'verify')
    by_name = {file['plugin']: file for file in verified['files']}
    for file in applied['files']:
        if file['masters'] != by_name[file['plugin']]['masters']:
            raise ValueError('Master list changed during translation')

    for values in stats.values():
        values['verification'] = (
            'Original-byte invariant verification; UTF8 nonmutating fresh readback; '
            'master/header/record-index + every approved string'
        )
    for source, before in original_hashes.items():
        if nskr.sha256(source) != before:
            raise ValueError(f'Source changed during generation: {source}')
    return translated, stats
