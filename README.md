# Nuclear Sunset 비공식 한국어 번역

원본 Nuclear Sunset 웹사이트의 한국어 번역 프로젝트입니다. 원작자의 번역 허락을 받았으며, 공식 Nuclear Sunset Team 웹사이트와는 별도로 운영됩니다.

- 원본 사이트: https://nuclearsunset.com/
- 원본 소스: https://github.com/FinalCatalyst/Nuclear-Sunset
- 한국어 사이트 주소: https://munument1.github.io/-KR-Nuclear-Sunset/
- 배포 상태: GitHub Actions 결과 및 Pages 설정을 확인해야 함
- 원본 기준 커밋: `50a606c7d43ffe0a338d22812661c5bfeba64dce` (2026-09-05)

## 번역 및 빌드 구조

### 게임 한국어 패치 — 시험 배포판

- [패쳐 v0.1.0-beta.1 다운로드](https://github.com/munument1/-KR-Nuclear-Sunset/releases/tag/v0.1.0-beta.1)
- [설치 및 복구 안내](https://munument1.github.io/-KR-Nuclear-Sunset/docs/main/korean-patch)
- [패쳐 소스와 검증 범위](patcher/README.md)

원본 모드와 프로필을 직접 수정하지 않고 별도 Output을 생성합니다. 전체 출력 자동 검사는 통과했지만 전 구간 문맥·게임 안정성 검수는 미완료입니다. 배포 패키지는 게임 원본과 전체 번역 Output을 포함하지 않습니다.

- `translations/docs/`: 영어 원본 경로를 그대로 따른 한국어 Markdown 문서
- `scripts/configure-site.cjs`: 원본 Docusaurus의 언어, 제목, URL, 탐색 메뉴 현지화
- `.github/workflows/build-korean-site.yml`: 원본 GitHub 소스를 체크아웃해 한국어 문서를 덮어쓰고 사이트를 빌드하는 배포 작업
- `TRANSLATION_STATUS.md`: 문서별 작업 범위와 남은 작업

대용량 원본 스크린샷이나 소스 코드 전체를 이 저장소 `main`에 다시 복제하지 않습니다. 배포 시 원본의 이미지를 포함한 Docusaurus 프로젝트를 특정 커밋으로 체크아웃하고 한국어 내용을 반영하여 `gh-pages` 브랜치에 정적 사이트를 생성합니다. 이 방식은 원본 디자인 및 모든 갤러리 컴포넌트의 호환성을 유지합니다.

현재는 일부 문서만 한국어로 번역되었습니다. **미번역 문서는 그대로 영어로 표시됩니다.** 번역 작업의 진행률은 문서 제목 현지화와 본문 전체 번역을 구분하여 관리합니다.

## GitHub Pages 활성화

1. 저장소 **Actions** 탭에서 `Build Korean Nuclear Sunset` 작업이 성공했는지 확인합니다.
2. **Settings → Pages → Build and deployment**에서 `Deploy from a branch`를 선택합니다.
3. `gh-pages` 브랜치와 `/(root)` 폴더를 선택하고 저장합니다.
4. 사이트의 링크와 이미지·페이지를 확인합니다.

이전에 만든 `index.html`은 초기 한국어 안내 사이트이며 `main` 브랜치에 남아 있습니다. 전체 원본 기반 Docusaurus 번역판은 `gh-pages` 브랜치로 배포됩니다.

## 번역 원칙

- 모드명, 실행 파일명, 폴더명, 설정 키와 프로그램 내 버튼 이름은 원문 유지
- 설치 지침과 FAQ의 단계 순서·위험 경고·예외 규칙은 원문을 정확하게 보존
- 이미지·링크·코드 블록·표·갤러리 import는 유지
- 원본 및 모든 기여자에 대한 출처 표기 유지
- 업스트림 변경 사항을 비교·검수한 다음 워크플로에서 고정된 커밋을 갱신

## 출처 및 저작권

Nuclear Sunset의 원본 제작진은 [Nuclear Sunset Team](https://nuclearsunset.com/docs/main/credits/)입니다. 원본 텍스트·이미지·기타 자산의 권리는 각 권리자에게 있으며, 각 모드의 이용 허락은 해당 제작자의 정책에 따릅니다. 한국어 번역 및 운영: [munument1](https://github.com/munument1).
