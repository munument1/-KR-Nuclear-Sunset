# 특성 설명 인코딩 및 실행 중 영문 덧붙임 수정

사용자가 제공한 2026-10-24 화면의 대상은 Vegas Elysium의
`ELYPerkSixgunSamurai`(03019ED7), `ELYPerkFeministAgenda`(03000821),
FalloutNV의 `PiercingStrike`(0014609F)이다.

두 Elysium PERK의 설치된 DESC는 정상 UTF-8 한글이다. 한편 다른
번역 공급자에는 CP949 문자열도 존재한다. tNVSE는 표시할 문자열
전체가 유효한 UTF-8일 때 변환하므로, 이미 CP949로 준비된 요구 조건과
UTF-8 DESC를 합치는 경로에서는 이 판별이 실패할 수 있다.
이는 정적 파일과 렌더러 소스에 근거한 원인 판단이며, 수정 후 같은
레벨업 화면의 게임 내 재검증이 필요하다.

`nskr_perk_display.py`는 한국어 UTF-8 PERK/DESC를 CP949로 맞춘다.
지원하지 않는 글자를 `?`로 버리지 않는다. 검토한 EM DASH 두 개는
CP949가 지원하는 HORIZONTAL BAR로 바꾸고, 나머지 비표현 문자는 실패 처리한다.
원문 문자열, UTF-8 source, CP949 renderer 사이의 의미를 유지한다.

`New Blood.esp`의 `SCPTNewBloodStartup`은 관통 타격의 기존 설명 뒤에
영어 출혈 문장을 실행 중 덧붙인다. 이 문장과 NS의 Coiled Snake,
S6S의 Careful Handling/Good Natured 덮어쓰기 문구도 번역한다.
이미 번역한 Educated/Headhunter/Fast Metabolism의 실행 문자열은 CP949로 맞춘다.

SCDA 문자열은 앞의 uint16 길이를 확인한 뒤 원래 바이트 예산 안에서
공백으로 패딩한다. SCDA 길이, 명령, 참조, SCHR 및 제어 흐름은 바뀌지 않는다.
SCTX는 같은 의미의 UTF-8 소스를 유지한다. 각 레코드는 편집 필드만
되돌려 원래 레코드와 바이트 단위로 일치함을 검증하고, 두 번째 파싱에서
변경이 없어야 한다. 전체 플러그인/그룹 크기는 기존 검증된 walker로 계산한다.

활성 플러그인의 최종 override를 소유자+하위 FormID로 대조한 결과,
전체 영어로 남은 정적 특성 설명은 기존 예외 처리였던 Concentrated Fire 하나였다.
정확한 FormID/EDID/영어 원문 두 변형에만 한국어 CP949 설명을 복원한다.

로컬 적용: `D:\Codex_Trans\비바\perk-fix-20261024`.
54개 기존 플러그인 파일, 980개 텍스트 편집. 새 ESP 및 로드 순서 변경 없음.
적용 전 파일과 SHA-256, 수정본, 백업, 적용 결과를 별도로 보관한다.
전체 테스트 111개 통과. 기존 원본 SHA 검사는 이미 번역된 설치 파일 대신
설치 전 원본 백업을 사용했다. 게임 내 결과는 아직 미검증이다.
