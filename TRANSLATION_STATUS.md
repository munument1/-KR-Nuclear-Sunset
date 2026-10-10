# Nuclear Sunset 한국어 번역 진행 현황

기준: 2026-10-10 · 원본 [FinalCatalyst/Nuclear-Sunset](https://github.com/FinalCatalyst/Nuclear-Sunset), 커밋 `50a606c7d43ffe0a338d22812661c5bfeba64dce`

## 현재

- 원본 Markdown 문서: **63개**
- 한국어 덮어쓰기 파일: **43개**
- 갤러리 제목 현지화: **30/30** (이미지·컴포넌트는 원본과 동일, 사진 설명의 추가 번역은 필요 시 별도 작업)
- 주요 본문 한국어 번역: `main/intro`, `main/features`, `main/requirements`, `main/specs`, `main/updating`, `main/support`, `main/controller`, `main/credits`, `main/donations`, `main/reference`, `resources/overview`, `NSVS/intro`
- `NSVS/setup`은 원본과 마찬가지로 본문 없이 제목만 있습니다.
- 아직 한국어 덮어쓰기 파일이 없는 원본 문서: **20개**

문서 파일 수는 번역 분량과 같지 않습니다. 특히 설치 지침·FAQ·변경 이력 등 장문은 아직 영어 원문을 사용합니다. 이 자료를 한국어로 번역한 것으로 간주하면 안 됩니다.

## 우선순위

1. `docs/main/setup.md` — Windows 설치 절차(경로·단축키·OS 보안 설정까지 교차 검증)
2. `docs/main/faq.md` — 설치 오류, 성능, 기술 지원 문답
3. `docs/main/linux.md` — Linux 설치(명령어와 경로 불변)
4. `docs/main/highlights.md` — 모드별 특징
5. `docs/resources/*.md` — 리소스 안내
6. `docs/changelog/*.md` — 릴리즈별 변경 이력 9개
7. `docs/videointro.md` — 동영상 소개 문서

## 검수 규칙

- 코드 블록, 이미지 URL, 외부 다운로드 주소, 파일명 및 경로는 원문과 동일하게 유지합니다.
- 원문에 오류가 의심되면 설치 절차를 임의로 고치지 않고 별도 검토 항목으로 남깁니다.
- 기술적 경고, 예외 조건, 구분된 플랫폼 절차를 생략하지 않습니다.
- 모든 수정은 `translations/docs/`에 기록하여 원문 업데이트와 별도 비교합니다.

## 게시

`Build Korean Nuclear Sunset`가 실행되면 원본 Docusaurus 소스를 바탕으로 `gh-pages` 브랜치에 배포 파일을 생성하도록 구성했습니다. 빌드 성공 여부와 Pages 접근 가능 여부를 각각 확인해야 합니다.
