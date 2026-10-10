---
sidebar_position: 9
title: 자주 묻는 질문
hide_title: true
sidebar_label: 자주 묻는 질문
---

# ![Frequently Asked Questions Banner](https://github.com/user-attachments/assets/75ff4d9d-f408-4a7c-b2d5-315bf2758679)

:::tip
원하는 정보를 빠르게 찾으려면 `Ctrl + F`를 눌러 관련 단어를 검색하세요.
:::

:::danger 문제 해결
설치 오류, 게임 시작 시 충돌 또는 실행 화면 멈춤이 발생하면 다음 단계를 **순서대로** 적용하되, 매 단계 후 문제가 해결됐는지 다시 시험하세요.
<details><summary>
펼치기 - 문제 해결 단계
</summary>

- [설치 요구 사항](https://nuclearsunset.com/docs/main/requirements)에 따라 지원되는 `Fallout: New Vegas` 및 `Fallout 3` 버전과 두 게임의 모든 DLC를 보유했는지 확인합니다.
- [Nuclear Sunset 설치](https://nuclearsunset.com/docs/main/setup#-installing-nuclear-sunset-)에 설명된 대로 Wabbajack에서 Nexus 계정에서 로그아웃한 뒤 다시 로그인합니다.
- [설치 요구 사항](https://nuclearsunset.com/docs/main/requirements)에 따라 필수 .NET Framework와 Visual C++ Runtime Libraries를 재설치합니다.
- [백신 제외 설정](https://nuclearsunset.com/docs/main/setup#-creating-antivirus-exclusions-)에서 안내한 제외 설정이 올바른지 확인합니다.
- 타사 백신 프로그램을 비활성화하거나 제거합니다.
- VPN을 비활성화합니다.
- Steam, Overwolf, Afterburner, Discord, Nvidia 등의 오버레이를 비활성화합니다. Xbox Game Bar는 비활성화할 필요가 없습니다.
- Windows Defender를 비활성화합니다.
- 완제품 PC나 노트북을 사용하는 경우 Omen Gaming Hub와 같은 제조사 전용 프로그램을 닫거나 제거합니다.
- Nuclear Sunset 폴더를 마우스 오른쪽 버튼으로 클릭하고 `Read-only`(읽기 전용)를 해제합니다.
- MO2에서 `Tools > Settings > Paths`로 이동하여 `Managed Game` 경로가 `Stock New Vegas` 폴더의 실행 파일을 가리키는지 확인합니다.
- 컴퓨터를 다시 시작합니다.
- Steam/GOG에서 Fallout: New Vegas를 한 번 더 실행한 다음 Mod Organizer 2로 다시 실행해 봅니다.
- Nuclear Sunset Wabbajack 설치 프로그램을 다시 실행합니다. 오류를 복구하는 작업이며 처음 설치할 때보다 훨씬 빠릅니다.
- [Tale of Two Wastelands(TTW) 설치](https://nuclearsunset.com/docs/main/setup#-installing-tale-of-two-wastelands-ttw-)에 명시된 경로 및 모드 크기가 일치하는지 확인합니다. TTW는 반드시 `Nuclear Sunset > Mods` 폴더 **내부**에 있어야 합니다.
- [4GB 패치 실행](https://nuclearsunset.com/docs/main/setup#-running-4gb-patcher-) 단계를 다시 진행합니다.
- 오래된 그래픽 카드를 사용한다면 [Intel 내장 GPU 또는 Vulkan 미지원 GPU의 DXVK 다운그레이드](https://nuclearsunset.com/docs/resources/troubleshooting#-intel-igpu-users-and-gpus-without-vulkan-support---downgrading-dxvk-)에 따라 적절한 DXVK를 설치했는지 확인합니다.
- `Stock New Vegas` 폴더에서 `d3d9.dll`을 `d3d9.dll.backup`으로 이름을 바꾸어 DXVK 자체를 꺼 보세요. 일부 GPU와 드라이버는 DXVK와 호환되지 않을 수 있습니다.
- 문제가 계속된다면 `Nuclear Sunset` 폴더를 삭제하고 처음부터 설치를 다시 시작합니다.
- 추가 지원이 필요하다면 `Nuclear Sunset > [NoDelete] Stock New Vegas > Crash Logs`에 있는 충돌 로그를 공식 Discord의 [support-unmodified-list](https://discord.com/channels/1445447774035251323/1445462089970880674) 채널에 공유합니다.
</details>
:::

:::caution 한국어판 보안 참고
원본 문제 해결 지침에는 백신 및 Windows Defender 비활성화가 포함되어 있습니다. 이러한 조치는 악성코드 방어 기능을 약화시킬 수 있으므로 원인을 확인하지 않은 채 상시 적용하지 마세요. 가능한 한 필요한 범위에서만 점검하고, 사용 후 보안 기능을 복구하세요. 기존 데이터를 삭제하기 전에는 백업하세요.
:::

- **3인칭 시점 — 3인칭으로 플레이해도 되나요?**
- 부분적으로 지원합니다. Fallout: New Vegas 모딩 환경에는 품질 높은 3인칭 애니메이션 교체 모드가 부족해 외형과 게임 밸런스에 영향을 미칩니다. 3인칭은 화면 감상용 카메라로만 사용하는 편을 권장합니다.

- **4GB Patcher — GOG판에는 이미 4GB 패치가 포함되어 있는데도 실행해야 하나요?**
- Nuclear Sunset에서 사용하도록 안내하는 유틸리티는 GOG에 동봉된 것과 다릅니다. 여기서 사용하는 4GB 패처는 게임이 xNVSE를 사용하도록 패치합니다. 이 작업을 생략하면 Nuclear Sunset에 포함된 대다수 모드가 작동하지 않습니다.

- **약어 — MO2의 모드 이름에 붙은 약어는 무엇을 뜻하나요?**
- 이 약어들은 Nuclear Sunset을 정리하고 관리하기 위한 표기입니다.
    - **ALT** — 수정된 모드.
    - **OP** — 최적화된 모드.
    - **MG** — 마스터 패치에 플러그인이 병합된 모드.
    - **HID** — 병합 후 플러그인이 숨김 처리된 모드.
    - **FL** — ESM 플래그를 지정한 플러그인.
    - **INF** — Nuclear Sunset Wabbajack 설치 프로그램에 통합된 모드.
    - **AEN** — 포함되어 있으나 기본적으로 비활성화되는 모드.
    - **CDN** — Wabbajack 서버에 호스팅된 모드.
    - **BOS** — Base Object Swapper를 이용하는 모드.
    - **SOFT AF** — OrgasmicSneeze가 Nuclear Sunset 전용으로 제작한 모드.
    - **LQ, VLQ, DB** — Low, Very Low Quality, Debug 프로필에서 활성화 또는 비활성화되는 모드.

- **중독 — Nuclear Sunset에서는 중독이 어떻게 작동하나요?**
- 금단 증상을 3일 동안 겪으면 시간이 지나면서 중독에서 회복됩니다. 중독을 일으킨 약물을 다시 복용하면 3일 타이머가 초기화됩니다.
  - 의사에게 중독 치료비를 내거나 Fixer를 사용하면 일정 시간 동안 중독의 부정적 효과가 억제됩니다. 중독 자체는 기존과 같은 속도로 자연 회복됩니다.

- **모드 추가 — 다른 모드를 추가하려면 어떻게 하나요?**
- Nuclear Sunset 지원팀은 다른 모드를 추가하는 방법을 안내할 의무가 없습니다. 사용자가 위험을 감수하고 모드를 추가할 수는 있지만, 이 경우 공식 지원을 받을 수 없습니다.

- **탄약 종류 — 구경별 여러 탄약은 어떤 차이가 있나요?**
- **AP** — 비싸고 희귀합니다. 무기 피해량은 감소하지만 적의 DT(피해 임계값)를 크게 낮춥니다. 강력한 장갑 적에게 매우 효과적입니다.
  - **HP** — 비싸고 희귀합니다. 무기 피해량이 증가하지만 적의 DT도 배가됩니다. 장갑이 없는 약한 적에게 매우 효과적입니다.
  - **Regular** — 저렴하고 흔하지만 장갑을 입은 적에게는 효과가 떨어집니다.
  - **Junk/Surplus** — 저렴하고 흔하지만 무기 상태가 더 빨리 나빠지고 피해량도 낮습니다.
  - **Other** — SWC, JSP, Match 등 별도 설명이 없는 특수 탄약은 대체로 일반 탄약보다 특정 성능이 우수합니다.

- **Application Load Error P:0000065432 — 해결 방법은?**
- [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-)에 있는 Steam PCR 사용자 지침을 따르세요.

- **Application Load Error P:0000065434 — 해결 방법은?**
- Steam이 실행 중인지 확인하고 [새 INI 파일 생성](https://nuclearsunset.com/docs/main/setup#-generating-fresh-ini-files-)과 [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-) 단계를 반복합니다.

- **BASS Init/XD3 Input 오류 — TTW 설치 중 오류가 발생합니다.**
- Fallout: New Vegas 또는 Fallout 3가 영어판이 아니거나, 필요한 DLC가 없거나, [깨끗한 게임 설치](https://nuclearsunset.com/docs/main/setup#-creating-clean-installs-and-backups-)를 제대로 완료하지 않았을 가능성이 있습니다.

- **검은 화면 — 화면이 계속 검은색으로 멈춥니다.**
- MO2에 올바른 실행 파일 경로가 설정되어 있는지 확인합니다. 상단 바의 ![image](https://github.com/user-attachments/assets/1e998eb6-90a5-46ae-acae-3ddb4771c369) 아이콘을 클릭하고 `Paths`를 연 뒤 `Managed Game`이 `Stock New Vegas` 폴더의 실행 파일을 가리키는지 확인하세요.

- **보블헤드·기술 서적 — 원래 있던 위치에서 찾을 수 없는 이유는?**
- 모두 다른 위치로 옮겨졌습니다. 이제 익숙한 장소에서 SPECIAL과 기술 점수를 쉽게 얻을 수 없습니다. 새롭게 탐색하며 발견하는 재미를 즐겨 보세요.

- **식인 특전 — 식인 기능이 작동하지 않습니다.**
- 식인 기능을 사용하려면 웅크린 상태여야 합니다.

- **동료 전투 — 동료가 무모하게 돌진해 죽습니다.**
- `C`를 눌러 Companion Command and Control 메뉴를 연 다음 전술을 `stay back`(뒤에 머무르기)과 `prefer ranged combat`(원거리 전투 선호)으로 바꿔 보세요.
  - 동료에게 무기, 탄약, 의약품을 제공했는지도 확인하세요.

- **동료 치료 — 동료를 어떻게 치료하나요?**
- 플레이어와 같은 방식으로 치료합니다. 의약품을 지급하거나 의사에게 치료비를 지불하거나 잠을 자세요. 의사는 플레이어를 치료할 때 동료도 함께 치료하고, 동료는 플레이어가 잠잘 때 같이 잡니다.

- **동료 영입 — 특정 동료를 영입할 수 없는 이유는?**
- 동료 영입 수는 플레이어의 **영구적인 카리스마 수치**에 따라 결정됩니다. 장비나 약물 등 일시적 보정치는 포함되지 않습니다. 카리스마 4일 때 동료 1명, 7일 때 2명, 10일 때 3명을 영입할 수 있습니다.

- **컨트롤러 — 컨트롤러를 지원하나요?**
- 지원하지만 Steam 버전만 가능합니다. GOG 또는 Epic Games 사용자에게는 비슷한 기능을 제공하는 적절한 타사 도구가 없습니다. Steam Input을 사용하고 [공식 Steam 컨트롤러 안내](https://nuclearsunset.com/docs/main/controller)를 따르세요.

- **콘솔 명령 — 게임에서 사용해도 안전한가요?**
- 아니요. 거의 모든 콘솔 명령은 예상치 못한 후속 문제를 일으킬 수 있습니다. 콘솔 명령을 사용하면 공식 지원을 받을 수 없습니다.

- **부상 — 불구가 된 팔다리는 어떻게 치료하나요?**
- 의사를 방문합니다.
  - Doctor's Bag 또는 Splint를 사용합니다.
  - 체력이 최대인 상태에서도 치료 아이템을 추가로 사용합니다.
  - 체력이 최대인 상태에서도 수면으로 추가 회복합니다.

- **DT와 DR — 피해 임계값과 피해 저항은 어떻게 작동하나요?**
- **Damage Threshold(DT)** — 피해량을 일정한 수치만큼 감소시킵니다. DR 적용 **후**에 계산됩니다. 원래 피해량의 최대 20%까지 경감할 수 있다는 제한이 적용됩니다. 예를 들어 DT가 10이면 피해량 40이 30으로 감소합니다.
  - **Damage Resistance(DR)** — 피해량을 비율로 감소시킵니다. DT 적용 **전**에 계산됩니다. 최대 피해 경감률은 85%입니다. 예를 들어 DR이 30이면 받는 피해량이 30% 줄어듭니다.

- **대화 기술 표시 — 왜 제거했나요?**
- 몰입도를 높이고 게임 외부 지식을 활용한 선택(메타게이밍)을 방지하기 위해 의도적으로 제거했습니다.

- **DLC — 각 DLC는 어떻게 시작하나요?**
- **수도 황무지:**
    - **Point Lookout** — 시타델을 지나 강가의 배 쪽으로 가면 경적이 울립니다.
    - **The Pitt** — 오아시스 근처에서 라디오 방송을 듣습니다.
    - **Mothership Zeta** — MDPL-13 발전소 근처에서 라디오 방송을 듣습니다.
    - **Operation Anchorage** — 베일리 교차로 근처에서 라디오 방송을 듣습니다.
  - **모하비 황무지:**
    - **Autumn Leaves** — 히파티아를 방문합니다.
    - **Into the Deep** — 샴블을 방문합니다.
    - **Dry Wells** — Blue Paradise Vacation Rentals를 방문합니다.
    - **Zion Trails** — 모하비 황무지 최북서쪽 모퉁이를 탐험합니다.
    - **Race To The Bottom** — 프리사이드 협동조합을 방문합니다.
    - **Honest Hearts** — 프리사이드 근처에서 라디오 방송을 듣습니다.
    - **Old World Blues** — 추락한 인공위성 근처에서 라디오 방송을 듣습니다.
    - **Dead Money** — 헬리오스 원 근처에서 라디오 방송을 듣습니다.
    - **Lonesome Road** — 협곡 잔해를 방문합니다.

- **DLC·퀘스트 모드 — 권장 레벨은?**
- **Nexus 다운로드 오류·지연 — 다운로드가 느리거나 실패합니다.**
- Wabbajack 설정에서 Nexus 계정에 다시 로그인하세요.

- **Fallout 3 — Nuclear Sunset을 플레이하려면 반드시 필요한가요?**
- 네. Fallout 3와 그 DLC를 보유하지 않고 Nuclear Sunset을 플레이할 수는 없습니다.

- **빠른 이동 — Nuclear Sunset에서도 가능한가요?**
- 네. 과적 상태이거나 전투 중이거나 퀘스트 진행상 빠른 이동이 제한된 상황이 아니라면 사용할 수 있습니다.

- **처음 플레이 — Fallout 초보자에게도 적합한가요?**
- 네. 도전적인 게임 플레이를 원하는 사용자에게 적합합니다. Nuclear Sunset이 지나치게 어렵다면 MO2의 [선택 모드](https://nuclearsunset.com/docs/main/setup#-optional-mods-0)에서 `Softercore`를 활성화해 보세요.

- **처음 플레이·볼트 101 — Fallout 3 도입부를 직접 경험하고 싶습니다.**
- Fallout 3의 도입부를 플레이하려면 MO2의 `Optional - Gameplay` 구분선에서 `[#] [INF] - Quick Start & Associated Addons - Nuclear Sunset Merge` 모드를 비활성화하세요.

- **처음 플레이 — 잘 살아남기 위한 팁이 있나요?**
- 캐릭터 생성 시 SPECIAL 능력치를 지나치게 낮추지 마세요. 일반적인 Fallout: New Vegas와 달리 Nuclear Sunset에는 쓸모없는 능력치가 없습니다.
  - 게임 초반에는 무기 기술 두 가지를 선택해 집중적으로 육성하세요. 탄약과 기술 점수가 모두 부족합니다. 근접 전투도 강력하지만 무기가 쉽게 파손됩니다.
  - 모든 특전과 특성이 개편되었습니다. 이후 예상치 못한 결과를 낳을 수 있으므로 효과를 주의 깊게 읽으세요.
  - 잡동사니가 중요합니다. 가능한 모든 것을 수집하세요. 잡동사니를 팔아야 식량, 탄약, 의약품을 마련할 캡을 충분히 모을 수 있습니다.
  - 빈 병은 물을 모으는 데 매우 유용합니다.
  - 음식은 체력을 많이 회복시키지 않습니다. 수면과 의사 방문이 더 효과적인 회복 수단입니다.
  - 약물과 술은 잠시 강력한 강화 효과를 주지만 중독 상태에서는 심각한 불이익이 생길 수 있습니다. 의사의 중독 치료는 일시적인 도움이 되며, 실제 중독에서 벗어나려면 자연 회복 시간이 필요합니다.
  - 일부 제작 재료는 예상하지 못한 용도로 사용됩니다. 제작대를 주의 깊게 살펴보세요.
  - 서로 다른 탄약을 사용하는 무기를 여러 개 휴대하세요. 탄약이 부족하기 때문에 무기를 자주 바꾸게 됩니다.
  - 기존 Fallout: New Vegas 또는 Fallout 3에서 특정 무기와 아이템이 얼마나 유용했는지는 잊으세요. Nuclear Sunset에서는 모든 요소의 균형을 전면 재조정하여 예전에 약했던 무기가 훨씬 유용해졌을 수도 있습니다.

- **FPS·화면 끊김 — 성능을 개선하려면 어떻게 하나요?**
- NVIDIA GPU 사용자라면 [NVIDIA 프로필 적용](https://nuclearsunset.com/docs/main/setup#-nvidia-users---applying-nvidia-profile-) 지침을 완료했는지 확인합니다.
  - AMD GPU 사용자라면 [ULPS 비활성화](https://nuclearsunset.com/docs/main/setup#-amd-users---disabling-ultra-low-power-state-ulps-) 지침을 완료했는지 확인합니다.
  - [Nuclear Sunset 프로필](https://nuclearsunset.com/docs/main/setup#-selecting-a-nuclear-sunset-profile-)의 품질을 낮춥니다.
  - [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-)에서 `Detail` 품질을 낮춥니다.
  - 4K 모니터를 사용한다면 [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-), 컴퓨터의 `Display Settings`, `[#] [INF] [DB] - OneTweak - Custom INI`에서 해상도를 2K로 낮춰 보세요.
  - [Lossless Scaling](https://nuclearsunset.com/docs/resources/lossless)을 사용하는 것도 고려할 수 있습니다.
    - Nuclear Sunset 팀은 Lossless Scaling과 제휴 관계가 없으며 해당 프로그램에 대한 지원을 제공하지 않습니다.

- **FPS 제한 프로그램 — 별도로 필요한가요?**
- 네. RTSS는 CPU 기반 기능으로 FPS를 제한하므로 GPU 기반 방식보다 지연 시간이 낮고 프레임 간격이 일정합니다. 특히 Fallout: New Vegas에서 효과적입니다.

- **도박 — 전에는 쉽게 돈을 벌었는데 지금은 어려워진 이유는?**
- [Gambling Luck Rebalance](https://www.nexusmods.com/newvegas/mods/92152)로 인해 행운이 도박 결과에 미치는 영향이 예전보다 훨씬 줄었습니다. 자세한 효과는 해당 모드 페이지에 설명되어 있습니다.

- **하드코어 — 하드코어 모드를 끌 수 있나요?**
- 아니요. Nuclear Sunset의 여러 모드는 하드코어 모드를 전제로 하며, 전체 목록 역시 이를 중심으로 설계되었습니다.

- **Hardercore — 선택 모드를 사용하면 무엇이 달라지나요?**
- 변경 사항은 설치 안내의 [선택 모드](https://nuclearsunset.com/docs/main/setup#-optional-mods-) 항목에서 확인할 수 있습니다.

- **치료 — 의사에게 돈을 내도 체력이 완전히 회복되지 않습니다.**
- 의도된 밸런스입니다. 완전히 회복하려면 여러 차례 치료비를 지불하거나 다른 회복 방법을 사용해야 합니다.

- **HDR — 모니터가 HDR을 지원하지 않는데 런처의 HDR을 꺼야 하나요?**
- 아니요. Fallout: New Vegas에서 HDR은 렌더링 품질을 가리키는 표현으로, 모니터의 HDR 지원 여부와 관계가 없습니다.

- **Humbled·황무지 간 이동 — 이동할 때 무엇을 유지하나요?**
- 플레이어의 레벨, 기술, 카르마가 초기화됩니다. 특전은 유지되며 기술 서적으로 얻은 기술 점수도 남습니다. 캡은 도난당해 영구적으로 사라집니다. 장비도 도난당하지만 나중에 되찾을 수 있습니다.

- **아이템 — 다음 도구들은 무엇에 사용하나요?**
- **Air Scrubber** — 방독면 및 방사능 저항을 제공하는 물품 수리에 사용합니다.
  - **Bypass Module** — 모듈과 마이크로퓨전 셀을 조합하여 터미널 해킹을 우회합니다. 필요한 재료량은 해킹 난이도에 따라 달라집니다.
  - **Grinder** — 연마 디스크와 소형 에너지 셀을 사용해 문 잠금장치를 우회합니다. 필요한 재료량은 잠금 난이도에 따라 달라집니다.
  - **Power Drill** — 드릴 비트와 소형 에너지 셀을 사용해 보관함 잠금장치를 우회합니다. 필요한 재료량은 잠금 난이도에 따라 달라집니다.
  - **Skill Items** — 플레이어의 소지품에 들어 있으면 지정된 기술 보너스를 제공합니다.
  - **Welding Torch** — 화염방사기 연료와 은화 또는 금화 등을 이용하여 방어구·무기 수리를 강화할 때 사용합니다.

- **아이템 위치 — 예전에 있던 곳에서 찾을 수 없습니다.**
- 이전 위치에 집착하기보다는 새로운 장소를 발견하는 재미를 즐겨 주세요. 사라진 아이템은 의도적인 개편에 따라 다른 위치로 옮겨졌습니다. 새로운 위치는 알려 드리지 않습니다.

- **단축키 — Nuclear Sunset 단축키 목록은 어디서 확인하나요?**
- 일시 정지 메뉴에서 `K`를 누르세요.

- **실행 — 설치 후 바닐라 Fallout: New Vegas만 실행됩니다.**
- Nuclear Sunset Wabbajack 설치 프로그램을 다시 실행하면 잘못된 파일 경로를 복구할 수 있습니다.
  - 게임 런처에서 직접 게임을 실행하지 않았는지 확인하세요.

- **저장·불러오기 — Skyrim처럼 빠른 저장과 빠른 불러오기를 피해야 하나요?**
- 아니요. 빠른 저장, 자동 저장, 일반 저장은 기능적으로 거의 같으며 게임에 부정적인 영향을 주지 않습니다. 마찬가지로 저장 파일을 다시 불러오는 행위도 게임의 안정성에 악영향을 주지 않습니다.

- **최대 레벨 — Nuclear Sunset의 레벨 상한은?**
- Tale of Two Wastelands에서 지정한 **60레벨**입니다.

- **로딩 — 로딩 화면이 너무 오래 지속됩니다.**
- FPS 제한값을 지나치게 낮게 설정했을 가능성이 큽니다.

- **수동 설치 — 왜 TTW는 직접 설치해야 하나요?**
- ModPub의 제한 사항 때문에 TTW는 수동으로 설치해야 합니다.

- **고기 — 동물이 고기를 떨어뜨리지 않는 이유는?**
- Hunter 특전이 없으면 사냥한 동물의 고기를 채취하기 어렵습니다.

- **메가톤 폭탄 — 폭탄을 해체하려면 어떻게 하나요?**
- 폭탄 해체 능력은 지능, 과학, 수리, 폭발물 수치에 따라 결정됩니다. 아래 공식으로 계산한 해체 능력치가 **90**이어야 합니다: `((Intelligence * Science) * .05) + Repair + Explosives`.

- **Mod Organizer 2 — 게임 실행 시 MO2가 잠기지 않는 이유는?**
- BSA 압축 파일 분석 기능이 활성화된 상태에서 목록 새로 고침이 지나치게 오래 걸리는 현상을 피하기 위한 의도된 동작입니다.

- **모듈화 — 원하는 대로 Nuclear Sunset을 수정할 수 있나요?**
- Nuclear Sunset은 기본적으로 모듈식으로 구성된 목록이 아닙니다. 복잡한 최적화, 플러그인 병합, 맞춤 업데이트 등으로 인해 변경된 목록은 공식 지원 대상에서 제외됩니다.

- **모드 설정 메뉴(MCM) — 설정을 바꿔도 되나요?**
- MCM 설정을 변경하는 것은 모드 목록을 수정하는 것으로 간주되며, 이 경우 공식 지원을 받을 수 없습니다.

- **Nuclear Sunset 수정 — 모드를 수정해도 되나요?**
- 모드 목록을 수정하면 공식 지원을 받을 수 없습니다. 커뮤니티의 도움이 필요하다면 Discord의 [support-modified-list](https://discord.com/channels/1445447774035251323/1445462031221264538) 채널을 이용하세요.

- **모드 — 비어 있거나 완전히 덮어씌워진 모드가 많은 이유는?**
- 이런 모드는 병합되거나 최적화되었지만, 제작자가 적절한 다운로드 수, Donation Points, 창작자 표시를 받을 수 있도록 빈 상태로도 목록에 포함해 두었습니다.

- **New Vegas Heap Replacer(NVHR) — 왜 포함하지 않았나요?**
- 현재는 권장하지 않습니다. xNVSE는 바닐라 힙 메모리 관리 방식을 자체적으로 개선했으며, NVHR처럼 메모리 사용량을 크게 늘리지 않고도 더 나은 결과를 제공합니다.

- **Nexus 업로드 — LODGen·Facegen·SOFT AF 업데이트를 별도로 설치해야 하나요?**
- 아니요. 향후 업데이트를 준비하기 위해 올라온 파일로, 따로 설치하면 게임이 손상될 수 있습니다. Nuclear Sunset의 정식 업데이트에 포함되었거나 별도 지시가 있을 때만 모드를 업데이트하세요.

- **NoDelete — [NoDelete]는 무슨 뜻인가요?**
- 이 표기가 붙은 폴더는 업데이트 과정에서 Wabbajack이 내부 파일을 수정하지 않도록 보호됩니다.

- **NVIDIA Profile Inspector 처리되지 않은 예외 — 어떻게 해결하나요?**
- 그래픽 카드 드라이버를 업데이트하거나 다시 설치하세요.

- **최적화 — Nuclear Sunset은 어떻게 최적화했나요?**
- Cathedral Asset Optimizer와 Nvidia Texture Tools를 이용하여 텍스처를 압축하고 2K로 축소하며 밉맵을 생성했습니다. 필요에 따라 SNIFF로 추가 조정합니다. 애니메이션은 압축한 뒤 BSArchPro로 BSA에 패킹하고, LOD 표시 거리를 최적화하며, 필요한 자원만 불러오도록 우선순위 플래그를 설정했습니다.

- **선택 모드 — 포함된 선택 모드는 어떻게 사용하나요?**
- [선택 모드](https://nuclearsunset.com/docs/main/setup#-optional-mods-) 항목을 참고하세요.

- **기존 모드 설치본 — Nuclear Sunset과 함께 유지할 수 있나요?**
- 네. Nuclear Sunset은 `Stock New Vegas` 폴더 안에서 독립적으로 실행되므로 다른 설치본에 영향을 주지 않습니다.

- **Overwolf — Nuclear Sunset과 함께 사용할 수 있나요?**
- 아니요. Overwolf는 게임 충돌을 일으킵니다.

- **페이지 파일 — New Vegas를 위해 페이지 파일 크기를 늘려야 하나요?**
- 아니요. Fallout: New Vegas의 메모리 한도는 3.9GB이므로 메모리 문제로 충돌하기 전에 페이지 파일이 사용되지 않습니다.

- **Parse 오류 — 설치 중 구문 분석 오류가 발생해도 괜찮나요?**
- 설치 프로그램이 마지막에 `Complete`를 표시했다면 문제없습니다.

- **분홍색 화면 — 장면 전환 화면이 분홍색으로 보입니다.**
- 4GB 패치 절차를 건너뛰었을 가능성이 큽니다. `[NoDelete] Stock New Vegas`에 있는 `FNVPatch.exe`를 확인하세요.

- **플러그인 누락·모드 없음 — 특정 플러그인이 없다는 알림이 나타납니다.**
- 특별히 고지한 경우가 아니라면 문제가 아닙니다. 일부 플러그인은 최적화 과정에서 병합되거나 제거되며, 별도 안내가 없다면 저장 파일에 큰 영향을 주지 않습니다.

- **정화 장치 — 활성화한 뒤 메인 메뉴로 돌아갑니다. 버그인가요?**
- 플레이어가 사망한 것입니다. 정화 장치를 활성화하는 다른 방법을 시도해 보세요.

- **방사능 — 방사능이 너무 심해 진행할 수 없습니다.**
- 방호복, Rad-X, RadAway, 술 등을 조합하여 방사능의 영향을 줄이세요. 어느 지역이든 도저히 진행할 수 없을 정도로 방사능이 심하다면 공식 Discord의 [bug-reports](https://discord.com/channels/1445447774035251323/1445462772442857574) 채널에 해당 위치를 알려 주세요.

- **반사 효과 — 뒤에 건물이나 물체가 있는데도 창문에 지형이 비칩니다.**
- 심각한 성능 저하를 피하기 위해 의도한 동작입니다.

- **런타임 오류 — 게임 실행 시 런타임 오류가 발생합니다.**
- `Stock New Vegas` 폴더를 만들기 전에 MO2를 실행했을 가능성이 큽니다. Nuclear Sunset Wabbajack 설치 프로그램을 다시 실행하면 오류를 복구할 수 있습니다. 최초 설치보다 훨씬 빠릅니다.

- **저장 — Nuclear Sunset에서는 저장이 어떻게 작동하나요?**
- 수동 저장 외에도 1분 간격으로 자동 저장 파일 10개를 순환하여 기록하는 기능이 있습니다.

- **그림자 — 그림자가 부드럽게 움직이지 않고 갑자기 이동합니다.**
- 계속 움직이는 그림자에서 생기는 성능 부담과 깜빡임을 줄이기 위한 NVR의 의도된 설계입니다.

- **반짝임·섬광·반딧불 효과 — 일부 물체가 반짝이는 이유는?**
- NVR의 PBR 셰이더가 품질이 낮은 텍스처와 상호작용하면서 생기는 현상입니다. 이상적으로는 이런 텍스처를 점차 교체할 예정입니다.

- **용량 — Nuclear Sunset은 왜 이렇게 큰가요?**
- 최적화를 적용했지만 텍스처 개선 범위가 매우 넓습니다. 원본 다운로드 파일만으로도 50GB가 필요합니다.

- **Runtime Error - I’m getting a runtime error at launch. Why?**  
  - You likely opened MO2 before creating your Stock New Vegas folder. Re-run the Nuclear Sunset Wabbajack Installer to correct the error. This will repair any errors and will be much quicker than the initial installation.

- **Saving - How does saving work in Nuclear Sunset?**
  - In addition to manual saves, there is an auto-save function that rotates through 10 auto-saves on one minute save intervals.

- **Shadows - Why do my shadows suddenly jump, rather than move continuously?**
  - This is an intentional design choice in NVR to reduce associated performance cost and flicker that is introduced by continuously moving shadows.

- **Shimmering/Sparkling/Firefly Objects - Why do some objects shimmer?**  
  - This is an unfortunate consequence of the NVR PBR shader interacting with poorly made textures. Ideally, these textures will be gradually replaced.

- **Size - Why is Nuclear Sunset so large?**  
  - Despite optimizations, the list's texture enhancements are extensive, with the original downloads alone requiring 50GB.

- **Skill Tags - How do skill tags work in Nuclear Sunset? I do not see the 15 point increase I am used to?**
  - Nuclear Sunset uses classic skill tagging, meaning that that all skill points input into the tagged skill are doubled per level up (each one skill point you have per level up would count as 2 for a tagged skill).
 
- **Sky - Why is my sky black? How do I fix it?**
  - You used the `Low` preset in [Configuring Game Settings](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-), which breaks critical rendering functions.

- **SPECIAL - What do SPECIAL do in Nuclear Sunset?**
  - **All SPECIALS:**
    - All grant extra items in starting gear in both Wastelands and various DLCs.
    - Contribute the the players size during character creaton.
  - **Strength:**
    - Increased carry weight.
    - Increased melee damage.
    - Increased knockdown resistance.
    - Improved hip fire spread.
    - Improved recoil control.
  - **Perception:**
    - Improved NPC detection while sneaking.
    - Improved non-damaging forced entry bonus.
    - Improved bullet spread.
    - Improved degree of time dilation associated with Just Bullet Time.
  - **Endurance:**
    - Increased HP.
    - Increased radiation resistance.
    - Increased poison resistance.
    - Increased knockdown resistance.
    - Increased health regeneration over time.
    - Increased sleep and wait health regeneration.
    - Reduced addiction chance.
  - **Charisma:**
    - Improved companion damage and defense.
    - Higher number of recruitable companions.
    - Improved barter prices.
    - Easier dialogue checks.
    - Increased reputation gains and decreased reputation losses.
  - **Intelligence:**
    - Improved skill points per level.
    - Improved non-damaging forced entry bonus.
    - Enemy intelligence reduces success in dialogue checks.
  - **Agility:**
    - Increased AP.
    - Improved radiation decay.
    - Improved non-damaging forced entry bonus.
    - Improved lockpicking.
    - Faster swim speed.
    - Faster reload speed.
    - Faster draw and holster speed.
    - Faster weapon jam recovery speed.
  - **Luck:**
    - Improved chance for critical hit.
    - Improved chance for crippled limb recovery while sleeping at full health.
    - Reduced odds for item destruction during forced entry.
    - Reduced chance for bypass tool to be destroyed.
    - Improved outcomes in various scripted events, such as repairing electrical boxes.
    - Improved lockpicking chances.
    - Improved hacking chances when using Immersive Minigame Tweaks.
    - Reduced weapon jam chance.

- **Sound - Why is the music or sound cutting in and out or crackling?**
  - Bluetooth sound devices do not work correctly with Fallout: New Vegas. One solution is to play some type of video or music in the background when launching the game, which then can be turned off after loading.
    Another solution is to download and run the [Soundkeeper 64](https://veg.by/en/projects/soundkeeper/) executable. It plays a constant imperceptible tone to fix any audio lag or connection oddities when using bluetooth headphones.

- **Sped-up Game - Why is my game sped-up?**
  - Cap your FPS below 120, this is a byproduct of exceeding the maximum capable FPS.

- **Start - For some reason my game launches with unmodded Fallout: New Vegas instead of Nuclear Sunset. How do I fix it?**
  - This is due to incorrect filepaths. Rerun the Nuclear Sunset Wabbajack installer. This process will repair errors and is much quicker than the initial installation.

- **Start - How do I start in the Mojave Wasteland instead of the Capital Wasteland?**  
  - Select `memory` when prompted after leaving the Vault 101 cave.

- **Start - Which Wasteland should I choose to start in?**
  - Either! Mechanics are in place to promote balance regardless of starting location.

- **Storage - What can be safely deleted/uninstalled after Nuclear Sunset installation?**
  - Fallout 3 can be uninstalled from Steam/GOG and the `Nuclear Sunset > Downloads` folder can be deleted (though much of this will be redownloaded during updates).

- **Tale of Two Wastelands - Is TTW required for Nuclear Sunset?**  
  - Yes. The modlist cannot be installed or used without TTW.

- **Traits - I can choose 99 traits. Is this a bug?**  
  - No, this is intentional behavior. Most traits have both benefits and downsides, which provide balance in having additional traits. Having the ability to have many traits provides ample opportunity for unique character experiences.

- **Traits - I chose a trait that said I could immediately select a new perk, but I was not offered a new perk. Why?**
  - You will be able to choose this perk when you next level up.

- **Traits - Why can I sometimes select new traits upon leveling up?**
  - New trait selections occur every 4 levels (levels 5, 9, 13, 17, etc).

- **Tweaks - Can I change settings in Stewie's Tweaks?**
  - Doing so is considered modifying the list and will invalidate support.

- **Ultrawide - Can I use an ultrawide resolution with Nuclear Sunset?**  
  - Yes. Enable the appropriate preset corresponding to your monitor's aspect ratio in the `Optional - Settings` separator in Mod Organizer 2.
 
- **Updates - Will updating impact my saves?**  
  - Unless specified otherwise, your saves will still work, though updates after starting a save may introduce small bugs.

- **Updates - ___ mod updated. Should I update it?**  
  - No. Unless instructed otherwise, you should not manually update any mods.

- **VATS - Can I disable Bullet Time and enable VATS instead?**  
  - No. VATS is very difficult to balance and is inherently incompatible with other mods included in Nuclear Sunset. All perks and traits are functional with Bullet Time, which is a superior skill-based alternative to VATS.

- **Wabbajack - The Nuclear Sunset installation froze in Wabbajack. What do I do?**
  - Re-run the `Nuclear Sunset.wabbajack` installer. The installer will resume where it left off, correcting any errors that occurred along the way.

- **Weapon Sway - Why does my weapon sway around my crosshair?**
  - You do not meet the required SPECIAL and weapon skill recommended in order to use the weapon, which are specified in the weapon statstics once you hover over the weapon in the Pip-Boy.

- **Wordle/Hacking - How do I play wordle?**
  - Letters are categorized into three categories when words are played:
    - Solid green highlight means the letter is in the correct position.
    - Solid yellow/orange highlight means the letter is in the word but in the wrong position.
    - No highlight means the letter is not in the word.
  - Previously utilized letters that are not in the word will be darkened on the bottom keyboard.

  ![image](https://github.com/user-attachments/assets/b7be4085-6be8-4df9-bd14-a3dc546b5d44)

- **XP - I do not always get XP when I kill enemies. Why?**  
  - XP is reported collectively at the end of combat and the player will not be rewarded XP for companion kills.
