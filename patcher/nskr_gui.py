"""Local Nuclear Sunset Output generator. Never writes to the installation."""
import argparse
from datetime import datetime
import os
from pathlib import Path
import queue
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import nskr
from nskr_output import build_output, output_catalog


def program_folder():
    return Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent


def resource_folder():
    if getattr(sys, 'frozen', False):
        folder = program_folder()
        if (folder / 'TranslationData/catalog.json').is_file():
            return folder
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent


def catalog_folder(explicit=None):
    if explicit is not None:
        return Path(explicit).resolve()
    primary = resource_folder() / 'TranslationData'
    return primary if (primary / 'catalog.json').is_file() else resource_folder() / 'bundles/ns-sst'


class App:
    def __init__(self, window, catalog=None):
        self.window = window
        self.folder = program_folder()
        self.catalog = catalog_folder(catalog)
        self.metadata = nskr.read_json(self.catalog / 'catalog.json')
        self.development = self.metadata.get('channel') == 'development'
        self.events = queue.Queue()
        self.output = None
        self.report_file = None
        suffix = ''
        window.title(f'Nuclear Sunset 한국어 패쳐 v{nskr.VERSION}{suffix}')
        window.minsize(840, 440)
        frame = ttk.Frame(window, padding=22)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        notice = ('기본 실행·자동 검증 완료 · 전 구간 플레이 테스트는 미완료입니다. 원본은 변경하지 않습니다.'
                  if self.development else '원본은 변경하지 않고 별도 Output만 생성합니다.')
        ttk.Label(frame, text=notice, foreground='#a33b12', wraplength=790).grid(
            row=0, column=0, columnspan=3, sticky='w', pady=(0, 16))
        ttk.Label(frame, text='Nuclear Sunset MO2 폴더').grid(row=1, column=0, columnspan=3, sticky='w')
        default = 'C:/Modlists/NuclearSunset' if Path('C:/Modlists/NuclearSunset/ModOrganizer.ini').is_file() else ''
        self.mo2 = tk.StringVar(value=default)
        ttk.Entry(frame, textvariable=self.mo2).grid(row=2, column=0, columnspan=2, sticky='ew', pady=(6, 12))
        self.browse = ttk.Button(frame, text='찾아보기', command=self.choose)
        self.browse.grid(row=2, column=2, padx=(8, 0), pady=(6, 12))
        ttk.Label(frame, text='프로필 선택 없이 설치된 전체 번역 대상을 처리합니다.').grid(
            row=3, column=0, columnspan=3, sticky='w')
        self.ui = tk.BooleanVar(value=True)
        self.fonts = tk.BooleanVar(value=True)
        self.plugins = tk.BooleanVar(value=self.metadata.get('full_translation_catalog') is True)
        self.scope_buttons = []
        if self.development:
            for row, text, variable in (
                (5, 'MCM·Translations 한국어 번역 + TTW UI·라디오', self.ui),
                (6, '한국어 폰트·수정 tNVSE DLL (별도 오버레이 모드)', self.fonts),
                (7, '전체 대상 플러그인 번역 (원문·레코드 경로가 일치하는 항목)', self.plugins),
            ):
                button = ttk.Checkbutton(frame, text=text, variable=variable)
                button.grid(row=row, column=0, columnspan=3, sticky='w', pady=2)
                self.scope_buttons.append(button)
        self.generate = ttk.Button(frame, text='Output 생성',
                                   command=self.start)
        self.generate.grid(row=8, column=0, sticky='w', pady=(16, 0))
        self.open_button = ttk.Button(frame, text='Output 폴더 열기', command=self.open_output, state='disabled')
        self.open_button.grid(row=8, column=1, padx=(8, 0), pady=(16, 0))
        self.report_button = ttk.Button(frame, text='결과 보고서 열기', command=self.open_report, state='disabled')
        self.report_button.grid(row=8, column=2, padx=(8, 0), pady=(16, 0))
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=3, sticky='ew', pady=(14, 0))
        self.status = tk.StringVar(value=(
            ('현재 설치본과 대응된 전체 플러그인 번역 후보, MCM·INI, UI·라디오, 폰트를 적용합니다.\n'
             if self.metadata.get('full_translation_catalog') else
             '기본 범위는 MCM·INI, 포함된 TTW UI·라디오, 폰트입니다. 미검수 Gemini 번역은 포함하지 않습니다.\n') +
            '게임 내 확인 전에는 Output을 설치 완료 또는 정식 번역으로 취급하지 마세요.'
            if self.development else 'Output 생성 후 보고서의 제외·미대응 항목을 확인해주세요.'))
        ttk.Label(frame, textvariable=self.status, wraplength=790, justify='left').grid(
            row=10, column=0, columnspan=3, sticky='w', pady=(14, 0))
        window.after(150, self.poll)

    def choose(self):
        folder = filedialog.askdirectory(title='ModOrganizer.ini가 있는 Nuclear Sunset 폴더 선택')
        if folder:
            self.mo2.set(folder)

    def busy(self, active):
        state = 'disabled' if active else 'normal'
        for widget in (self.generate, self.browse, *self.scope_buttons):
            widget.configure(state=state)
        if active:
            self.progress.start(12)
        else:
            self.progress.stop()

    def start(self):
        root = Path(self.mo2.get().strip())
        if not (root / 'ModOrganizer.ini').is_file():
            messagebox.showerror('폴더 확인', 'mods 폴더가 아니라 ModOrganizer.ini가 있는 Nuclear Sunset MO2 폴더를 선택해주세요.')
            return
        scopes = {name for name, value in (('ui', self.ui), ('fonts', self.fonts), ('plugins', self.plugins))
                  if value.get()} if self.development else None
        try:
            output_catalog(self.metadata, development=self.development, scopes=scopes)
        except ValueError as error:
            messagebox.showerror('번역 범위 확인', str(error))
            return
        target = self.folder / 'Output'
        if (target.exists() or target.with_name(target.name + '.report.json').exists()
                or target.with_name(target.name + '.report.txt').exists()):
            target = self.folder / ('Output-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        self.busy(True)
        self.open_button.configure(state='disabled')
        self.report_button.configure(state='disabled')
        self.report_file = None
        self.status.set('프로필과 활성 모드의 원본을 확인하고 있습니다. 설치 파일은 변경하지 않습니다.')

        def run():
            try:
                installation = nskr.Installation(root, all_installed=True)
                report = build_output(
                    installation, self.catalog, target, development=self.development, scopes=scopes,
                    progress=lambda message: self.events.put(('status', message)))
                self.events.put(('done', target, report))
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=run, daemon=True).start()

    def poll(self):
        try:
            event = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            if event[0] == 'status':
                self.status.set(event[1])
            else:
                self.busy(False)
                if event[0] == 'error':
                    self.status.set('Output 생성에 실패했습니다. 원본 설치는 변경하지 않았습니다.')
                    messagebox.showerror('생성 실패', event[1])
                else:
                    _, self.output, report = event
                    translated = sum(row.get('translated', 0) for row in report['files'])
                    already = sum(row.get('already_translated', 0) for row in report['files'])
                    unmatched = sum(row.get('unmatched', 0) for row in report['files'])
                    fonts = report.get('fonts', {})
                    activation = (f'\n폰트 사용 시 MO2에서 "{fonts["mod"]}"를 활성화하고 기존 tNVSE 설정보다 높은 우선순위로 배치하세요.'
                                  if fonts.get('requires_activation') else '')
                    extra = set(report.get('assets', {}).get('mods_requiring_activation', []))
                    runtime = report.get('runtime_mods', {})
                    extra.update(runtime.get('mods_requiring_activation', []))
                    perk_dict = report.get('perk_runtime_dictionary', {})
                    extra.update(perk_dict.get('mods_requiring_activation', []))
                    if fonts.get('requires_activation'):
                        extra.discard(fonts['mod'])
                    if extra:
                        activation += '\n별도 번역 모드 활성화 필요: ' + ', '.join(sorted(extra))
                    if runtime.get('plugins_requiring_activation'):
                        activation += '\n번역 ESP 활성화 필요: ' + ', '.join(runtime['plugins_requiring_activation'])
                    self.status.set(
                        f"프로필: {report['profile']}\n"
                        f"{len(report['files'])}개 파일 생성 · 새 번역 {translated}곳 · 이미 최신 한국어 {already}곳 · 미대응 {unmatched}곳 · "
                        f"제외 {len(report['skipped'])}개\n{self.output}\n"
                        f"결과 보고서를 확인하세요. 설치·프로필 변경은 자동으로 수행하지 않습니다.{activation}")
                    self.open_button.configure(state='normal')
                    self.report_file = Path(report['report_text'])
                    self.report_button.configure(state='normal')
        self.window.after(150, self.poll)

    def open_output(self):
        if self.output:
            os.startfile(self.output)

    def open_report(self):
        if self.report_file:
            os.startfile(self.report_file)


def packaged_resources_check(catalog=None):
    import subprocess
    resources = resource_folder()
    catalog = catalog_folder(catalog)
    metadata = nskr.read_json(catalog / 'catalog.json')
    development = metadata.get('channel') == 'development'
    output_catalog(metadata, development=development)
    native = [entry for entry in metadata.get('files', []) if entry.get('kind') == 'plugin-records']
    invalid = [entry['path'] for entry in native
               if not entry.get('mappings') and not entry.get('fallback_only')]
    if invalid:
        raise RuntimeError(f'Packaged plugin has no SST policy: {invalid}')
    for relative in ('NSKRXEditWorker.exe', 'Backend/XEditLib.dll',
                     'Backend/FalloutNV.Hardcoded.dat', 'Backend/icudtl.dat', 'Backend/LICENSE'):
        if not (resources / relative).is_file():
            raise FileNotFoundError(resources / relative)
    probe = subprocess.run(
        [str(resources / 'NSKRXEditWorker.exe'), '--print-acp'],
        capture_output=True, text=True, timeout=60,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if probe.returncode or probe.stdout.strip() != '65001':
        raise RuntimeError(f'Packaged XEdit worker is not UTF-8: {probe.stdout} {probe.stderr}')
    if sys.stdout:
        print(f'package-check OK: channel={metadata.get("channel", "release")} plugins={len(native)}')
    return catalog, development


def packaged_self_test(args):
    catalog, development = packaged_resources_check(args.catalog)
    scopes = ({'ui', 'fonts'} - ({'ui'} if args.no_ui else set())
              - ({'fonts'} if args.no_fonts else set())) if development else None
    if development and args.plugins:
        scopes.add('plugins')

    def generate(output):
        return build_output(nskr.Installation(Path(args.self_test), all_installed=True),
                            catalog, output, development=development, scopes=scopes,
                            only_plugins=args.only_plugin)

    if args.output:
        generate(args.output)
    else:
        with tempfile.TemporaryDirectory(prefix='nskr-packaged-selftest-') as tmp:
            generate(Path(tmp) / 'Output')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path)
    parser.add_argument('--package-check', action='store_true')
    parser.add_argument('--self-test', metavar='MO2')
    parser.add_argument('--profile')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--plugins', action='store_true')
    parser.add_argument('--only-plugin', action='append')
    parser.add_argument('--no-ui', action='store_true')
    parser.add_argument('--no-fonts', action='store_true')
    args = parser.parse_args()
    if args.package_check:
        packaged_resources_check(args.catalog)
        return 0
    if args.self_test:
        return packaged_self_test(args)
    window = tk.Tk()
    App(window, args.catalog)
    window.mainloop()
    return 0


def entrypoint():
    if not any(flag in sys.argv for flag in ('--self-test', '--package-check')):
        return main()
    try:
        return main()
    except Exception:
        import traceback
        error = traceback.format_exc()
        (program_folder() / 'NuclearSunset-self-test.error.log').write_text(
            error, encoding='utf-8')
        if sys.stderr:
            sys.stderr.write(error)
        return 1


if __name__ == '__main__':
    raise SystemExit(entrypoint())
