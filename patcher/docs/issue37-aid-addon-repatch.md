# 이슈 #37 재현 및 후보 검증

[이슈 #37](https://github.com/munument1/-KR-Nuclear-Sunset/issues/37)의 제보자는 이전 Output을
원본 모드 폴더에 덮어썼다고 답했고, 파일 SHA-256 스크린샷을 제공했습니다.

- 제보 파일 SHA-256: `00f6027550251ee498063205c2ddd71c8162fdc421876c75b42690cb10327270`
- 검수된 영문 원본: `dbdb4d5a09026746dd87678879065f66298a496fff8e582c4294085e35a9902f`
- 정식 v1.1.3 전체 ZIP: `98a33551c77bbdab465f57df1cd814469c8fdc761bb81718b7b8d7a4641936fb`

정식 v1.1.3 실행 파일과 배포 카탈로그의 Aid Addon 항목을 사용해 영문 원본에서
제보 파일과 **전체 SHA-256이 같은 결과물**을 만들었습니다. 그 결과물을 입력으로
v1.1.3을 다시 실행하면 동일한 `SCPTUpdateDummyNamesCall` 해시 오류가 발생합니다.
제보자의 실제 파일을 직접 전달받지는 않았습니다.

기존 PR #38의 검증 로직은 이전 한국어 SCTX/SCDA 치환을 되돌린 뒤 영문 스크립트의
전체 해시를 검사하고, 다시 번역한 바이트까지 비교합니다. 정확히 일치하는 기존
결과만 보존하며 검수되지 않은 코드·부분 번역은 계속 거부합니다.

## 실행 파일 검사

별도 MO2 시험 폴더에 원본 ESP를 복사하고 실제 게임의 마스터 파일을 읽기만 합니다.
설치된 mods나 프로필에는 쓰지 않습니다. 후보 ZIP을 새 폴더에 푼 실행 파일로 검사했습니다.

| 입력 및 실행 파일 | 결과 |
| --- | --- |
| 영문 원본 → 정식 v1.1.3 | 성공, 제보 해시와 일치 |
| 위 결과 → 정식 v1.1.3 | 제보와 동일한 해시 오류, Output 미발행 |
| 위 결과 → v1.1.4 후보 | 성공, 두 스크립트 `already_translated`, 같은 해시 |
| 후보 결과 → v1.1.4 후보 재실행 | 성공, 같은 해시 |
| 영문 원본 → v1.1.4 후보 | 성공, 두 스크립트 `translated`, 같은 해시 |
| 한국어 스크립트 소스를 임의 변경 → 후보 | 해시 오류, Output 미발행, 입력 보존 |

검사 후 설치된 원본 ESP의 바이트가 유지되는지도 확인합니다.

```powershell
python tools/verify_issue37_repatch.py --baseline PATH_TO_1_1_3_PACKAGE --candidate PATH_TO_CANDIDATE_PACKAGE --mo2 PATH_TO_ORIGINAL_MO2 --work NEW_DETACHED_WORK_FOLDER
```

## 패키지 및 회귀 검사

후보 빌드는 정식 v1.1.3 ZIP 해시를 고정하고, 메인 Python 모듈 중
`nskr_medical_bag.py`와 `nskr.py`의 버전 문자열만 바뀌었는지 확인합니다.
번역 카탈로그는 버전만 바꾸며, 번역 매핑·폰트·tNVSE DLL·기존 대응 소스·
XEdit 실행 파일과 런타임·백엔드는 원본 ZIP의 바이트와 대조합니다.
23개 카탈로그 페이로드, 전체 ZIP CRC, 압축 해제 후 실행 파일 자체 검사도 수행합니다.

```powershell
python tools/build_v1_1_4_release.py --base PATH_TO_PINNED_1_1_3_ZIP --work NEW_DETACHED_BUILD_FOLDER
python -m unittest discover -s tests -p test_medical_bag.py -v
python -m unittest discover -s tests -p test_compiled_scpt.py -v
python -m unittest discover -s tests -p test_dynamic_display.py -v
```

전체 195개 테스트 중 B42 외부 비교 결과 폴더가 필요한 2개는 자료 부재로 실패했습니다.
그 2개를 제외한 193개 실행에서는 189개 통과, 4개 건너뜀, 실패 0개입니다.
누락된 외부 기대값을 현재 구현으로 생성해 검사를 통과시키지 않았습니다.

정식 배포본에도 같은 실행 파일 검증 절차를 적용합니다. 제보자의 실제 환경 및 실게임 확인이
남아 있으므로 이슈를 닫지 않습니다.
