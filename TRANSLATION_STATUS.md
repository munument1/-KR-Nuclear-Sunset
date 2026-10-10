# Nuclear Sunset 한국어 번역 진행 현황

기준: 2026-10-10 · 원본 [FinalCatalyst/Nuclear-Sunset](https://github.com/FinalCatalyst/Nuclear-Sunset), 커밋 `50a606c7d43ffe0a338d22812661c5bfeba64dce`

## 현재 상태

- 원본 Markdown 문서: **63개**
- 한국어 덮어쓰기 문서: **52개 (82.5%, 파일 기준)**
- 이미지 및 갤러리 컴포넌트: 원본 자산 그대로 사용
- 갤러리 제목 현지화: **30/30** (사진 자체와 갤러리 컴포넌트는 원본)
- 설치 지침: `docs/main/setup.md` **전체 23구간 번역 완료**, 스크린샷 56개/URL 75개 보존 확인
- Linux 안내: `docs/main/linux.md` **전체 13구간 번역 완료**, 이미지 12개/원문 URL 15개 보존 확인
- 주요 모드 소개: `docs/main/highlights.md` **70개 설명 번역 완료**
- Sweet 추천 모드: **39개 설명 번역 완료**, 링크 48개 보존 확인
- 기타 주요 본문: 소개, 기능, 요구 사양, 설정 참고표, 업데이트, 컨트롤러, 지원, 크레딧, 후원, NSVS 소개 등
- 자료실: 7개 중 6개 번역 완료 (`stars.md` 제외)
- Docusaurus 자동 빌드: 기존 성공 실행 확인. **최신 커밋의 배포 완료 여부는 Actions에서 별도 확인 필요**

> **82.5%는 파일 수 기준**입니다. 30개 갤러리는 문서 제목만 한국어로 바뀌었고, 남은 FAQ·STARS·변경 이력은 상대적으로 분량이 커서 실제 번역 분량 완성도와 동일하게 볼 수 없습니다.

## 미번역 문서 11개

- `docs/main/faq.md` — FAQ 전수, 설치 오류 및 각종 기술 지원
- `docs/resources/stars.md` — STARS 상세 설명
- `docs/changelog/1.0.0.0.md`
- `docs/changelog/1.0.0.1.md`
- `docs/changelog/1.0.0.2.md`
- `docs/changelog/1.0.1.0.md`
- `docs/changelog/1.0.1.1.md`
- `docs/changelog/1.0.1.2.md`
- `docs/changelog/1.0.2.0.md`
- `docs/changelog/1.0.2.1.md`
- `docs/changelog/1.0.2.2.md`

## 고위험 검수

- 게임 및 OS 설정값, 명령어, 경로, 모드 이름과 플러그인 파일명은 원문 표기를 유지합니다.
- 백신 제외, ASLR 해제, Steam DLL 권한 변경, `rm -rf` 명령어는 보안이나 데이터 손실에 영향을 줄 수 있어 한국어판에 별도 주의사항을 추가했습니다.
- 원본 Linux 지침에 Flatpak 백업 폴더명 `FNVBackup` / `NVBackup` 불일치가 있어 확인을 권고했습니다.
- 원본 AMD MSI Afterburner 다운로드 주소에 만료 가능성이 있는 인증 토큰이 포함되어 있습니다.
- 새 버전의 설치 지침 변경은 영어 원본과 비교 검수한 뒤 반영해야 합니다.

## 배포

`.github/workflows/build-korean-site.yml`이 고정한 업스트림 Docusaurus 프로젝트에 `translations/docs/`의 한국어 파일을 덮어쓰고 `gh-pages` 브랜치로 게시합니다.

- 배포 워크플로: https://github.com/munument1/-KR-Nuclear-Sunset/actions/workflows/build-korean-site.yml
- 사이트 예정 주소: https://munument1.github.io/-KR-Nuclear-Sunset/
- GitHub Pages 설정의 게시 브랜치는 `gh-pages /(root)`이어야 합니다.

## 다음 작업

1. FAQ 97개 질문 및 문제 해결 지침 전수 번역
2. STARS 문서 전체 번역
3. 9개 과거 변경 이력 번역
4. 빌드·내부 링크·목차·스크린샷·모바일 화면 최종 점검
