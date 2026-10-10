# Nuclear Sunset 비공식 한국어판 — 검수 현황

기준: 2026-10-10  
원본: https://github.com/FinalCatalyst/Nuclear-Sunset  
원본 소스 고정 커밋: `50a606c7d43ffe0a338d22812661c5bfeba64dce` (2026-09-05)

## 한국어 문서 대응 파일: 63 / 63 (100%, **파일 기준**)

| 문서 분류 | 원본 | 한국어 대응 파일 | 번역 범위 |
| --- | ---: | ---: | --- |
| main | 14 | 14 | 본문 번역 |
| resources | 7 | 7 | 본문·지침 번역 |
| changelog | 9 | 9 | 수정·변경 설명 현지화, 모드명·버전 그대로 |
| NSVS | 2 | 2 | 소개 번역 / 원본 setup은 본문 없음 |
| gallery | 30 | 30 | **문서 제목 현지화**; 이미지·React 컴포넌트 원본 유지 |
| videointro | 1 | 1 | 제목 현지화; 원본 임베드 유지 |
| **총합** | **63** | **63** | 영어 원본을 기본으로 하는 미포함 Markdown 없음 |

> 100%는 원본 Markdown의 경로가 모두 한국어판에 대응한다는 뜻입니다. 모든 이미지의 설명·코드 내부 문자열·갤러리 컴포넌트의 텍스트까지 전부 번역하고 육안으로 검증했다는 뜻은 아닙니다.

## 핵심 검수 완료

- Windows 설치 안내 `docs/main/setup.md`: 23구간 번역, 원본 스크린샷 56개 및 URL 75개 대조
- Linux 설치 안내 `docs/main/linux.md`: 13구간 번역, 이미지 12개 및 URL 15개 대조
- FAQ `docs/main/faq.md`: 97/97개 질문과 답변 번역, 빈 답변 0건, 이미지 3개 및 URL 31개 보존
- 모드 특징 `docs/main/highlights.md`: 모드 70개 설명 번역
- `docs/resources/sweetrecommendedmods.md`: 설명 39개 번역
- STARS `docs/resources/stars.md`: 전체 설치 절차 번역, 원본 다운로드 URL 96개와 파일·INI 명칭 보존
- 릴리스 변경 이력 `docs/changelog/`: 9/9개 파일 번역 완료

## 별도 확인이 필요한 사항

- 원본 Linux 설치 지침에는 `FNVBackup`과 `NVBackup`이라는 백업 폴더명의 불일치가 있습니다. 번역문에 경고를 추가했습니다.
- 원본 STARS의 Sea Captain Hat 압축 해제 절차에 Spice of Life 폴더명을 잘못 언급한 부분이 있어 대상 경로를 확인하도록 안내했습니다.
- Windows 백신 제외, Windows Defender 비활성화, Mandatory ASLR 변경, Steam DLL 접근 권한 변경, Linux `rm -rf` 명령어는 보안 또는 데이터 손실 위험이 있습니다. 원문과 별도로 한국어 주의사항을 추가했습니다.
- 원본의 일부 다운로드 링크는 시한부 서명 URL이므로 링크 유효성 확인이 필요합니다.
- 실제 Windows/Linux 환경의 설치 동작과 모든 모드의 게임 내 동작은 별도 실사용 테스트 대상입니다.
- 갤러리 30개는 제목만 번역했으며, 이미지 속 문구나 갤러리 React 컴포넌트의 모든 부가 문자열까지 현지화한 것은 아닙니다.

## 배포

자동 빌드는 `.github/workflows/build-korean-site.yml`을 사용합니다. 원본의 Docusaurus 구조와 이미지를 그대로 불러오고 `translations/docs/`의 한국어 문서를 덮어씌워 `gh-pages` 브랜치에 게시합니다.

- Actions: https://github.com/munument1/-KR-Nuclear-Sunset/actions/workflows/build-korean-site.yml
- Pages: https://github.com/munument1/-KR-Nuclear-Sunset/settings/pages
- 공개 예정 사이트: https://munument1.github.io/-KR-Nuclear-Sunset/

**마지막 문서 커밋의 빌드와 공개 페이지까지 자동으로 성공했다고 추정하지 않습니다.** GitHub Actions의 마지막 빌드 성공 및 Pages의 `gh-pages /(root)` 설정, 실제 URL 접속을 별도로 확인해야 합니다.

## 최종 검수 작업

1. 최신 커밋 기준 GitHub Actions 성공 확인
2. 전체 페이지의 내부 링크·URL·원본 이미지·React 갤러리 작동 확인
3. 원문과 한국어 문서의 섹션·리스트 구조를 추가 검사
4. 화면 폭별 메뉴·폰트·표·스크린샷 표시 확인
5. 원본 업데이트 때 설치 절차와 설정값 변경 여부를 비교
