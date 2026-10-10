# Nuclear Sunset xEditLib native validation — 2026-10-10

개발 브랜치 `feature/nuclear-sunset-patcher`의 **실제 ESP/ESM 적용 및 재로드 검증** 결과다. 원본은 `C:\Modlists\NuclearSunset`의 활성 MO2 플러그인을 사용했으며, 적용·저장·재로드는 별도의 `.local` 검증 환경에서만 진행했다.

## 검증 결과

| 플러그인 | SST 문자열 후보 | 네이티브로 실제 적용 | 구조가 검증된 수정 레코드 | 후보 미적용 | xEdit UTF-8 재로드 |
|---|---:|---:|---:|---:|---|
| `AutumnLeaves.esp` (Uncreative Edition) | 4,296 | **4,266** | 1,783 | 30 | **통과** |
| `ZionTrail.esm` (Revised Rewritten Revoiced) | 2,162 | **2,033** | 1,316 | 129 | **통과** |
| `ThePitt.esm` (사용자 보유 `FO3 KR.esm`에서 추출) | 3,200 | **3,200** | 2,283 | 0 | **통과** |
| **합계** | **9,658** | **9,499** | **5,382** | **159** | 3/3 통과 |

번역의 질·문맥·게임 화면 출력·MCM·FOJP 자막/외부 파일까지 검증한 것은 아니다. **번역 적용을 통과한 플러그인 3개**라는 표현만 정확하다. 전체 252개 플러그인의 실제 적용 검증은 아직 남아 있다.

### 자세한 근거

검증은 기존 VNV 패쳐에서 사용했던 Python/XEditLib worker와 네이티브 DLL을 `patcher/.tools`에 **로컬로만 복사**하여 수행했다. 각 대상과 필요한 원본 마스터만 분리한 게임 `Data` 복사본을 만들고 SST 매핑을 적용하여 출력 플러그인을 생성했다. 이후 생성물을 **새 로딩 세션으로 다시 읽어** 수정 필드의 번역 문자열과 수정 레코드의 구조 해시, 마스터 목록, 파일 헤더와 레코드 인덱스를 검증했다.

로컬 기록:
- `patcher/.local/native-validation-20261010-v2/summary.json`
- `patcher/.local/native-validation-20261010-v2/candidate-coverage-summary.json`
- `patcher/.local/native-validation-thepitt-20261010/result_summary.json`

현재 **9,499건은 실제 적용과 신선한 재로드 검증을 모두 통과했다**. 159건은 후보로 추출됐지만 적용되지 않았다.

- Autumn Leaves: 30건 — `INFO` 21, `REFR` 8, `ALCH` 1
- Zion Trail: 129건 — `INFO` 80, `NOTE` 36, `DIAL` 12, `MESG` 1
- The Pitt: 후보 3,200건 모두 적용

참고: XEditLib의 `direct_sst_no_match` 경고 수치(Autumn Leaves 2,543, Zion Trail 741, The Pitt 2,107)는 **SST 후보 미적용 건수와 다르다**. 이는 번역 가능한 레코드에 포함된 다른 비매칭 원문 필드까지 확인하는 진단 수치이므로 단순히 번역 실패 건수로 합산하지 않는다.

## 다음 퀘스트 모드 우선순위 (기존 252개 전수 감사)

다음 항목들은 **현재 직접 매칭되는 SST가 없는 활성 플러그인**이며, 자체 영문 표시 필드 수로 정렬했다. 다른 모드의 번역 재사용 가능성 및 Nexus 사용자 번역 파일 존재 여부는 별도 확인이 필요하다.

| 우선 | 플러그인 | 고유 영문 필드 후보 |
|---|---|---:|
| 1 | `LoneWandererThemeTTW.esm` | 3,637 |
| 2 | `RaceToTheBottom.esm` | 2,915 |
| 3 | `Party Banter 2.esm` | 2,472 |
| 4 | `Into The Deep.esm` | 2,393 |
| 5 | `AWorldOfPainFO3.esm` | 2,350 |

`NS.esm`, `NS.esp`, `NSNPCs.esp`의 고유 영문 필드(기존 검사 기준 각각 273, 105, 34건)도 Nuclear Sunset 전용 추가 번역의 대상이다.

## 아직 미완료

- 전체 로컬 카탈로그 직접 SST **38개 플러그인 / 225,311건 후보** 중 이번에 검증한 것은 위 3개뿐이다.
- 최신 카탈로그는 `patcher/.local/ns-sst-with-nexus-quest-esp-v2/catalog.json`; `translation_ready=false`를 유지한다.
- MCM JSON 24개와 관련 INI 13개는 별도로 검수해야 한다.
- 나머지 모드의 FOJP/ESP 번역 데이터 확보, xEdit 경로·중복 필드 문제 해결, 실제 게임 내 표시 테스트, 출처·배포 권한 검토가 남았다.
- GitHub에는 검사 도구와 요약 보고서만 올리고, 원본 ESM/ESP 및 번역 본문 데이터는 업로드하지 않는다.

## 재현 방법

별도 사용자 Windows PC/MO2 설치 경로가 전제된다. 기존 VNV 네이티브 워커와 라이브러리가 현지 `.tools`에 있어야 하며 자동 재배포하지 않는다.

```powershell
cd "D:\Codex_Trans\NuclearSunsetPatcherRepo\patcher"
py -3 tools\verify_nexus_sst_native.py
py -3 tools\verify_thepitt_native.py
py -3 tools\audit_native_candidate_misses.py
```

위 검증 스크립트는 산출물이 이미 존재하면 안전상 덮어쓰지 않으므로 재실행 시 새 검증용 실행 디렉터리를 지정해야 한다.
