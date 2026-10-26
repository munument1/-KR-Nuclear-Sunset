# tNVSE v1.0.8 변경 소스

v1.0.7에 포함된 tNVSE 소스의 다섯 파일을 수정했습니다. 전체 대응 소스와 의존성은
릴리스 패키지 Licenses-and-Source/tNVSE-71-KR-UI-source/tNVSE에 포함합니다.
이 폴더의 source.patch는 해당 원본에 적용할 수 있는 변경 내역입니다.
GPL-3.0 라이선스를 유지합니다.

UTF-8 유효성 검사·무손실 CP949 변환·문 안내 조각별 정규화와 엔진의 열쇠 필요 안내
접두부 번역을 보강했습니다. 접두부는 정확히 일치하고 사전에 번역이 있을 때만
처리하며 뒤의 열쇠 이름을 정규화합니다. 일반 혼합 문자열 추정은 하지 않습니다.

Win32 Release DLL SHA256: 0bb5c3c5387fb76679a1bef7dbdd2bced05c7fa9e849d3d80613d5814b58c52f
MSVC 18 BuildTools / Win32 / CMake Release, VC-LTL 5.3.1, DXSDK D3DX 9.29.952.8.
회귀 검사 140개 통과. 실게임 표시·호출 ABI 검증은 별도로 필요합니다.
