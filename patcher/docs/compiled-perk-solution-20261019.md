# Nuclear Sunset #11: 컴파일된 SCPT 특전 설명 번역 오버레이 (2026-10-19)

## 구현 결과

`patcher/nskr_perk_dictionary.py`는 두 모드의 컴파일된 실행 스크립트가 게임 중 영어 설명을 주입하는 문제를 **tNVSE 71의 UI 사전 번역**으로 처리한다. 설치된 ESP·SCPT·SCDA·INI·XML을 읽어 출처를 검증한 뒤, 별도의 MO2 모드 `Nuclear Sunset - Korean Perk Runtime`에 다음 3개 파일을 만든다.

- `NVSE/plugins/tnvse.ini` — 실제 활성 설정 또는 이번 Output에서 먼저 생성한 한국어 폰트용 INI를 보존하면서 `[Dictionary] bEnableDictionaryMixedSourceTranslation`만 `1`로 설정.
- `NVSE/plugins/tnvse_dictionary.xml` — 기존 tNVSE 사전 JSON 참조를 보존하고 별도 `NSKR_Perk_Descriptions.json`을 추가. tNVSE XML이 아예 없으면 이 특전 규칙만 담는 XML 생성.
- `NVSE/plugins/NSKR_Perk_Descriptions.json` — 검증한 원문 전체와 영문 꼬리말만 대상으로 하는 한국어 사전 4항목.

설치 원본은 수정하지 않는다. Output 디렉터리에 생성된 독립 모드를 MO2에 추가·활성화해야 하며, **기존 tNVSE, tNVSE Default Config, 한국어 폰트/사전 모드보다 우선순위가 높아야 한다**. `build_perk_dictionary(installation, stage, seen)` 인터페이스는 다른 Output 생성기와 같은 `(files, status)`를 반환한다.

GUI의 `Installation(root, all_installed=True)`는 전체 설치 모드를 알파벳순으로 조사하므로 실제 활성 프로필의 INI/XML 우선순위를 재현하지 않는다. 이 오버레이 생성기는 해당 입력을 받으면 `ModOrganizer.ini`에 기록된 **현재 선택 프로필**을 별도 `Installation(root)`로 읽어 검증·INI/XML/JSON 공급자를 고른다. 다른 번역 파일 생성에 사용되는 전체 설치 모드 목록과 원본 `installation` 객체는 유지한다. `source_profile`을 결과에 기록한다. 선택 프로필을 읽을 수 없으면 잘못된 전체 설치 모드 공급자로 대체하지 않고 해당 오버레이만 건너뛴다.

## SCPT 출처와 문장 일치 조건

| 특전 | 확인된 원본 스크립트 | 게임 중 덮어쓰는 설명 | 번역 방식 |
| --- | --- | --- | --- |
| HeadHunter | `NS.esp` / `SCPTPatchForJBT` / `0x91082F79` | Bullet Time 머리 명중 +25%, AP +50%, 2단계 엎드린 자세 재장전 +25%, 머리 치명타 피해 +15% | 전체 원문 **정확 일치**. 실제 `%` 표시 형태와 스크립트의 `%%` 형태를 각각 등록 |
| Fast Metabolism | `Sweet Consumables.esp` / `sssSCPTIngestiblesStartup` / `0x12001870` | `AlcoholRadHealing == 1`일 때 현재 설명 뒤에 ` Alcohol will also reduce your radiation twice as quickly.` 추가 | `[%] Alcohol will also reduce your radiation twice as quickly.` → `[%] 술을 마시면 방사능 수치도 두 배 빠르게 감소합니다.`; 기존 한국어 스팀팩 회복 +20% 앞 문장 캡처를 그대로 유지 |

원본 파일 SHA-256·FormID·마스터 소유자·EDID·SCHR/SCDA 길이·SCTX/SCDA 문자열을 `tools/audit_issue11_compiled_scripts.py`의 동일 검사로 재검증한다. 두 스크립트 또는 원본 버전이 변경되면 이 오버레이는 생성하지 않는다. 헤드헌터의 `%` 변형과 원래 `%%` 표현도 임의의 다른 설명으로 확대 적용하지 않는다.

## tNVSE 소스 검증

분석 기준은 시험 모드에 포함된 `tNVSE-71-KR-UI-source.zip`의 실제 C++ 구현이다.

1. `dictionary/dictionary_perk.cpp`의 `TryTranslatePerkDescription()`은 `Req:`, `Ranks:`, `Source:` 형식의 구조화된 특전 설명용이다. `bEnableDictionaryPerkDescriptionTranslation=1`만 켜서는 두 평문을 번역하지 못한다.
2. `dictionary/dictionary_prepare.cpp`의 `PrepareSourceForRegistration()`과 `dictionary/dictionary_translate.cpp`의 `PrepareSourceForLookupMapped()`는 한국어가 섞인 문자열을 서로 다르게 정규화할 수 있다. **한국어 문장 + 영어 꼬리말 전체를 정확 일치 키로 저장하는 방식은 신뢰할 수 없다.**
3. `dictionary/dictionary_translate.cpp`의 `allowPatternTranslation` 분기는 혼합 문장에 `bEnableDictionaryMixedSourceTranslation=1`이 필요함을 확인한다. `TryTranslateWildcardKey`는 긴 ASCII 꼬리말에만 대응하고 `RawMappedRange`로 원래 접두 문자열 바이트를 가져온다. `dictionary/dictionary_match.cpp`의 `TranslateCapture`는 DBCS 캡처를 그대로 유지한다.
4. INI 변경으로 기존 사전에도 혼합 와일드카드 규칙이 새로 적용될 수 있으므로 이 빌더는 **기존 JSON 원문에 `[%]` 항목이 하나라도 있으면 생성을 거부**한다. 또한 사전 번역·다중바이트·와일드카드가 활성 상태인지 확인하고, 정규식 번역 및 구조화된 특전 번역 옵션은 0이어야 한다. 검증한 시험용 `NSKR_UI_Translations.json`에는 4,611개 원문이 있고 `[%]` 항목은 0개였다.
5. 기존 INI·XML·JSON을 물리적 파일에서 읽으며, 선행 출력의 신규 폰트 INI 또는 사전 JSON이 있으면 해당 출력물을 우선해 최신 한국어 렌더링 설정을 보존한다.

이 방법은 원본 모드 `SetFormDescription` 실행 순서를 바꾸거나 SCDA 바이트 길이·분기 주소를 만지지 않는다. 사전 치환은 UI 화면 구성 시점에 적용되므로 다른 스크립트가 영어 설명을 나중에 기록하는 경우에도 최종 화면에는 한국어를 공급하도록 설계했다. 단, 실제 tNVSE/JIP 실행 중 `SetFormDescription`의 퍼센트 해석 및 한국어 UI 렌더링은 별도로 실게임 시험해야 한다.

## 확인과 실게임 남은 단계

검증 명령 (`patcher` 작업 디렉터리):

```powershell
python -m unittest discover -s tests -p test_perk_dictionary.py -v
python -m py_compile nskr_perk_dictionary.py
```

테스트는 이슈 #11 영문 리터럴·한국어 수치 보존, 한국어 전체 정확 키 배제, 엄격한 와일드카드, 변경된 INI 한 옵션/기존 XML 보존/반복 안전성, 기존 와일드카드/정규식 거부, 새로운 한국어 폰트 출력 우선순위, 원본 XML 없는 경우의 생성 경로를 검증한다. 실제 프로필에서 원본 두 ESP 검증 및 새 오버레이 3파일 생성도 실행했다.

추가 회귀 테스트는 비활성 `tNVSE Default Config`가 알파벳순으로 마지막 공급자가 되는 `all_installed=True` 상황을 재현한다. 이때 선택된 `KR Test` 프로필의 올바른 XML/JSON을 사용해 3파일을 생성하는지 검증한다. 실제 Nuclear Sunset 설치에서도 `Installation(root, all_installed=True)`로 호출하여 **3파일 생성 성공**, `source_profile=KR Test - h8at5ar1`, `source_literals_verified`를 확인했다.

게임 테스트는 **미실시**. MO2에서 새 모드를 기존 tNVSE와 한국어 UI 관련 모드보다 높은 우선순위로 활성화한 뒤 (1) HeadHunter 첫 단계 및 2단계 문구에 `25/50/25/15%` 수치와 한국어 전체 문장 표시, (2) Fast Metabolism에 기존 한국어 스팀팩 `20%` 문장과 술/방사능 `2배` 문장 표시, (3) 시작·로드·재로드 때 영어 또는 중복 문장 유무, (4) 다른 UI 사전 영향 없음을 확인해야 한다. 활성화를 해제하면 오버레이 효과는 사라진다.

`game_validation='not_run'`은 생성 보고서에 유지한다. 이 시험이 성공하기 전까지 사용자 화면의 완전한 수정은 입증하지 않았다.
