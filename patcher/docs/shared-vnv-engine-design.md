# Nuclear Sunset 한국어 패쳐 — VNV 공통 엔진 운영 원칙

2026-10-10. 개발 브랜치 설계 문서. Nuclear Sunset(TTW) 한국어 패쳐는 Viva New Vegas(VNV) 패쳐를 기반으로 하되, **번역 엔진을 공통으로 유지하고 모드팩별 번역 데이터·설치 경로·마스터 인식을 분리**한다.

## 재사용할 VNV 기능

| 기능 | 공통 엔진 유지 | Nuclear Sunset 특화 |
|---|---|---|
| SSU8/SSU9 SST 읽기 | `vnvkr_sst.py`와 `nskr_sst.py` 동기화 | FO3/TTW/Sunset SST 및 원문 일치 검증 |
| XEditLib ESP/ESM 레코드 치환 | XEditLib 연결부와 작업자 처리 공통화 | 실행 파일 이름/프로세스 환경변수, TTW 마스터 목록 |
| MCM JSON 및 번역 INI | VNV 병합·변환 방식 재사용 | 실제 설치된 Nuclear Sunset 파일에서 경로 발견 |
| 한글 폰트 및 tNVSE | **VNV의 수정 tNVSE 71 DLL**과 UTF-8 설정, 폰트 4종 재사용 | 기존 `tNVSE` 및 `tNVSE Default Config`보다 높은 MO2 우선순위의 독립 모드 |
| 라디오 자막 | VNV의 Mojave Radio Captions 자막 모드 기반 | TTW 라디오/오디오 및 대사 충돌 실게임 검증 |
| 설치 결과 | MO2 외부 임시 Output → 수동 복사 및 활성화 | Nuclear Sunset MO2 프로필 및 TTW/Fallout3 마스터 처리 |

## 소스 동기화

현재 소스 대조에서 다음 4개 공통 모듈은 **VNV 원본을 모듈명·실행파일명만 Nuclear Sunset 명명으로 변경했을 때 정확히 일치**했다.

- `vnvkr_sst.py` ↔ `nskr_sst.py`
- `vnvkr_xelib.py` ↔ `nskr_xelib.py`
- `vnvkr_xedit.py` ↔ `nskr_xedit.py`
- `vnvkr_xedit_worker.py` ↔ `nskr_xedit_worker.py`

VNV 수정을 Nuclear Sunset에 도입할 때에는 기존 NS 전용 변경 내용이 사라지는 일이 없도록 **차이 비교 → 백업 → 단위 테스트**를 거친다. `nskr.py`, `nskr_output.py`, `nskr_fonts.py`, `nskr_gui.py`는 TTW 전용 동작을 포함하므로 일괄 덮어쓰지 않는다. 각각의 설치 파일은 여전히 독립 실행 가능한 상태를 목표로 한다.

## 번역 데이터 안전 조건

- Gemini 번역 JSON 배치 **859/859개** 생성·구조 검증 완료, 실패 배치 0개.
- 신규 번역 후보 **42,021개**에서 내부 메타데이터 **4,526개는 적용 제외**.
- 남은 **37,495개**는 아직 승인 완료된 번역이 아니다.
- 최초 QA **3,016개 경고**: 18개는 `{Song ...}` 라디오 식별자로 확인하여 원문 유지 대상으로 분리. 나머지 **2,998개는 추가 검수 필요**.
- `<Laughs>`·`{Speech Check}` 등의 연출/대화 표기를 단순 태그 비교로 기술 오류로 분류하지 않도록 주의할 것. `%s`, 실제 HTML 마크업 태그, 줄바꿈 손상 등은 별도 엄격한 검증을 한다.
- WWG 검수 CSV와 사용자 제공 `TTW KOR Radio + UI.esp`는 로컬에 보관하며 GitHub에는 게임 원문/번역 전문/API 키/바이너리를 업로드하지 않는다.

## 릴리즈 전 통과 조건

1. 영문 원문과 37,495개 번역 후보의 레코드·필드·FormID 대응 및 적합성 검수
2. 내부 메타데이터 제외 및 토큰/줄바꿈/한국어 인코딩 재검사
3. FO3/TTW 신규 마스터, GMST, 라디오, MCM 데이터 충돌 확인
4. VNV 한국어 수정 tNVSE와 한글 폰트를 Nuclear Sunset MO2 우선순위에 맞게 설치한 **실게임 테스트**
5. 테스트 통과 후에만 개발 카탈로그 `translation_ready` 활성화 및 정식 패쳐 릴리즈

이 문서는 설계·검수 현황이며, **현재 정식 번역 패쳐가 완성됐다는 뜻은 아니다**.
