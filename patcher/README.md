# Nuclear Sunset Korean patcher (work in progress)

Adapted from the Viva New Vegas Korean patcher with TTW MO2 instance recognition. Source code only, no game plugins or packaged translations.

## Preflight
Run: py -3 ns_inventory.py --mo2 C:\Modlists\NuclearSunset

## Current state
TTW profile detection and Fallout 3/TTW master identity are ported. Native XEditLib translation logic, MCM/INI merger and font support are copied for adaptation. The included catalog is an EMPTY PLACEHOLDER with translation_ready=false, so patch creation and EXE release are intentionally blocked until a verified TTW catalog is prepared. Do not present this development branch as a finished patch.

All game master and mod files stay in their original installation, Output generation must be limited to a separate user-reviewed copy. The Korean website is independent. Permissions for website translation do not authorize redistribution of third-party ESP/ESM or other assets.

## TTW 사전 커버리지 사전 점검 (2026-10-10)
- 선택 프로필: A - Uranium Haze NVR High
- 활성 모드 1,633개, 활성 플러그인 252개 / 252개 소스 확인
- VNV SST와 이름이 겹치는 플러그인 19개, 사전 후보 87,571행 (실제 적용 건수 아님)
- 기존 MCM/INI 사전과 이름이 겹치는 텍스트 5개
- FO3, DLC 및 TTW 핵심 마스터 8개는 별도의 SST 검수 필요

사전 후보 생성: py -3 tools/import_vnv_catalog.py --vnv-catalog PATH_TO_EXISTING_VNV_CATALOG --output .local/ns-sst-candidate
