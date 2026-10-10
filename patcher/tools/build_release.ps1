param(
    [string]$Python = ".venv\Scripts\python.exe",
    [string]$Catalog = "bundles\ns-sst"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path "$Catalog\catalog.json")) {
    throw "SST catalog is missing: $Catalog"
}

$env:PYTHONPATH = $root
& $Python -c "from pathlib import Path; import nskr; from tools.prepare_release_package import validate_catalog; validate_catalog(nskr.read_json(Path(r'$Catalog')/'catalog.json')); print('catalog validation: OK')"
if ($LASTEXITCODE -ne 0) { throw 'Catalog validation failed' }
& $Python -c "import json,sys; d=json.load(open(r'$Catalog\catalog.json', encoding='utf-8-sig'));sys.exit(0 if d.get('target_modlist')=='nuclear-sunset-ttw' and d.get('translation_ready') is True else 1)"
if ($LASTEXITCODE -ne 0) { throw 'TTW catalog not production ready' }

Remove-Item -Recurse -Force 'build\NuclearSunsetKoreanPatcher','build\NSKRXEditWorker' -ErrorAction SilentlyContinue
Remove-Item -Force 'dist\NuclearSunsetKoreanPatcher.exe','dist\NSKRXEditWorker.exe' -ErrorAction SilentlyContinue

$workerArgs = @(
    '-m','PyInstaller','--noconfirm','--onefile','--console',
    '--name','NSKRXEditWorker',
    '--manifest','tools\xedit_worker_utf8.manifest',
    'nskr_xedit_worker.py'
)
& $Python @workerArgs
if ($LASTEXITCODE -ne 0) { throw 'XEdit worker build failed' }

$mainArgs = @(
    '-m','PyInstaller','--noconfirm','--onefile','--windowed',
    '--name','NuclearSunsetKoreanPatcher',
    '--add-data',"$Catalog;TranslationData",
    '--add-binary','dist\NSKRXEditWorker.exe;.',
    '--add-binary','.tools\xeditlib-native\XEditLib.dll;Backend',
    '--add-data','.tools\xeditlib-native\FalloutNV.Hardcoded.dat;Backend',
    '--add-data','.tools\xeditlib-native\icudtl.dat;Backend',
    '--add-data','.tools\xeditlib-native\LICENSE;Backend',
    'nskr_gui.py'
)
& $Python @mainArgs
if ($LASTEXITCODE -ne 0) { throw 'Patcher build failed' }

$exe = Resolve-Path 'dist\NuclearSunsetKoreanPatcher.exe'
$hash = Get-FileHash $exe -Algorithm SHA256
$size = (Get-Item $exe).Length
Write-Host 'Single-file release:' $exe
Write-Host 'Size MB:' ([math]::Round($size / 1MB, 1))
Write-Host 'SHA256:' $hash.Hash
