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
- **수도 황무지:**
    - **Point Lookout (Low Level Point Lookout 적용)** — 5~10
    - **The Pitt** — 15~20
    - **Mothership Zeta (Hardcore Zeta 적용)** — 20~25
    - **Operation Anchorage (Anchorage Gameplay Expansion 적용)** — 25~30
  - **모하비 황무지:**
    - **Autumn Leaves** — 1
    - **Dry Wells** — 5~10
    - **Into the Deep** — 5~10
    - **Race To The Bottom** — 10~15
    - **Honest Hearts** — 10~15
    - **Zion Trails** — 15~20
    - **Old World Blues** — 25~30
    - **Dead Money (Dead Money Tweaks 적용)** — 25~30
    - **Lonesome Road** — 40~45

- **모드 비활성화 — 특정 모드를 꺼도 되나요?**
- 안전하게 켜거나 끌 수 있는 것은 `Optional` 구분선 아래에 있는 모드뿐입니다.

- **변장 — 변장 시스템은 어떻게 되었나요?**
- 기본 구현에 해결하기 어려운 오류가 있어 제거했습니다.

- **DMP 파일 — MO2 실행 시 충돌하면서 DMP 파일 3개가 열립니다.**
- 런타임이 오래되었기 때문입니다. [설치 요구 사항](https://nuclearsunset.com/docs/main/requirements)에서 런타임 업데이트 방법을 확인하세요.

- **Failed or Slow Nexus Downloads - Why are my downloads slow or failing?**  
  - Relog into your Nexus account in the Wabbajack settings.

- **Fallout 3 - Is Fallout 3 absolutely required to play Nuclear Sunset?**  
  - Yes. There is no way to play Nuclear Sunset without owning Fallout 3 and the associated DLCs.

- **Fast Traveling - Can I fast travel in Nuclear Sunset?**  
  - Yes. The only circumstances in which fast travel is prohibited is when over-encumbered, while in combat, or while prohibited by quest content.

- **First Time Playing - Is this list suitable for a Fallout newcomer?**  
  - Yes. This list is ideal for anyone seeking a challenging experience. If Nuclear Sunset feels overwhelming, consider enabling `Softercore` in the [Optional Mods](https://nuclearsunset.com/docs/main/setup#-optional-mods-0) section of MO2.

- **First Time Playing/FO3 Vault Intro - I want to experience the intro/Fallout 3 Vault 101 sequence.**  
  - To experience the intro sequence, disable the `[#] [INF] - Quick Start & Associated Addons - Nuclear Sunset Merge` mod in the Mod Organizer 2 `Optional - Gameplay` separator.  

- **First Time Playing - Do you have any tips on how to be successful?**  
  - Avoid reducing any SPECIAL stat too low during character creation. No stat is useless in Nuclear Sunset, despite this being contrary to standard Fallout: New Vegas.
  - Choose two weapon skills to focus on at the start of the game. Ammo is scarce, as are skill points. Melee is powerful, though weapons break easily.
  - All perks and traits have been overhauled. Review their effects carefully, as they may have unintended consequences later on.
  - Trash is important. Scavenge for everything possible. Selling trash will be important to gaining enough caps to afford food, ammo, and aid.
  - Empty bottles are invaluable for water collection.
  - Food will not provide much healing. The best ways to heal are by sleeping and by visiting doctors.
  - Chems and alcohol can give strong transient buffs, though are also associated with severe drawbacks during times of addiction. Visiting a doctor about the player's addiction will only help for a period of time while the player takes time to naturally recover from their addiction.
  - Some crafting items have unexpected uses. Study crafting stations carefully.
  - Carry multiple weapons that require different ammo types. Ammo scarcity will require you to switch weapons frequently.
  - Forget any preconceptions of the utility of certain weapons or items in standard Fallout: New Vegas or Fallout 3. Everything in Nuclear Sunset has been completely rebalanced, and weapons that were weak previously may now be much more useful.

- **FPS/Stutter - How can I increase FPS/Reduce Stutter in Nuclear Sunset?**  
  - If using NVIDIA, ensure that the [Applying NVIDIA Profile](https://nuclearsunset.com/docs/main/setup#-nvidia-users---applying-nvidia-profile-) instructions have been followed.
  - If using AMD, ensure that the [Disabling Ultra-Low Power State (ULPS)](https://nuclearsunset.com/docs/main/setup#-amd-users---disabling-ultra-low-power-state-ulps-) instructions have been followed.
  - Reduce the [Nuclear Sunset Profile](https://nuclearsunset.com/docs/main/setup#-selecting-a-nuclear-sunset-profile-) quality.
  - Reduce the `Detail` quality in [Configuring Game Settings](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-).
  - If using a 4k monitor, try reducing resolution to 2k in [Configuring Game Settings](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-), your computers `Display Settings`, and in `[#] [INF] [DB] - OneTweak - Custom INI`.
  - Consider trying [Lossless Scaling](https://nuclearsunset.com/docs/resources/lossless).
    - Please note that the Nuclear Sunset team has no affiliation with Lossless Scaling and does not provide support for it.

- **FPS Limiters - Do I need a separate FPS limiter?**  
  - Yes. RTSS utilizes CPU-based functions to limit FPS, which offers lower latency and better consistency than GPU-based methods, especially in Fallout: New Vegas.

- **Gambling - I used to be able to easily win gambling and earn free money, but now it's harder. Why?**
  - Luck plays a much smaller part of gambling that before thanks to [Gambling Luck Rebalance](https://www.nexusmods.com/newvegas/mods/92152). The effects luck has while gambling can be found on the mod page.

- **Hardcore - Can I disable the hardcore mode?**  
  - No. Many mods in Nuclear Sunset rely on hardcore mode, and the list is designed around it.

- **Hardercore - What changes does the Hardercore Optional Mod change?**  
  - The changes for hardercore can be found in the [Optional Mods Section](https://nuclearsunset.com/docs/main/setup#-optional-mods-) of the Setup Instructions

- **Healing - When I pay a doctor to heal me, I do not heal fully. Why?**  
  - This is an intentional balance design. You will need to pay for several different healing sessions or heal through other means to fully heal.

- **HDR - The launcher is configured with HDR on, but my monitor doesn't support HDR. Should I turn it off?**  
  - No, Fallout: New Vegas uses the term HDR to reference the quality of rendering, which is independent of your monitor.

- **Humbled/Traveling to the Mojave/Capital Wasteland - What do I get to keep when I transition from from one Wasteland to the other (get humbled/Benny'd)?**
  - The players level, skills, and karma are reset. Perks are retained. Skills gained from skill books are retained. Caps are stolen and permanently removed. Gear is stolen, though can later be recovered.

- **Items - What does ___ item do?**
  - **Air Scrubber** - Used to repair gas masks and other items that provide radiation resistance.
  - **Bypass Module** - Uses a combination of modules and microfusion cells to bypass terminal hacking. The amount of material required depends on the hacking difficulty.
  - **Grinder** - Uses a combination of discs and small energy cells to bypass door locks. The amount of material required depends on the lock difficulty.
  - **Power Drill** - Uses a combination of drill bits and small energy cells to bypass container locks. The amount of material required depends on the lock difficulty.
  - **Skill Items** - Add specified skill bonuses while held in the players inventory.
  - **Welding Torch** - Used to augment armor and weapon repair, alongside flamer fuel, and silver or gold coins.
 
- **Items - Where is ___ item located? It used to be in this very specific location!**  
  - Please enjoy the thrill of discovery, rather than focusing on what used to be. Any missing items you encounter have been relocated as part of an intentional overhaul. No, we will not tell you the new location.

- **Keybinds - How can I view Nuclear Sunset’s keybinds?**  
  - Press `K` in the pause menu.

- **Launch/Start - When I launch Nuclear Sunset after finishing the installation process, it launches unmodded/vanilla Fallout: New Vegas. How do I fix it?**
  - Re-run the Nuclear Sunset Wabbajack installer, it will fix repair any incorrect filepaths.
  - Ensure the game is not being launched from the launcher.

- **Loading & Saving - In Skyrim I am told I can't quicksave or quickload. Is this also true in Nuclear Sunset?**
  - No. Quicksaves, autosaves, and full saves are also functionally similar, and none of these negatively impact the game. Similarly, reloading will not negatively impact your game.

- **Level Cap - What is the level cap in Nuclear Sunset?**  
  - 60, as set by Tale of Two Wastelands.

- **Long Load Screens - I have very long load screens, why?**  
  - You likely capped your FPS at too low a value.

- **Manual Installs - Why must I manually install TTW?**  
  - TTW requires manual installation due to ModPub restrictions.

- **Meat - Why don't animals drop meat?**
  - Without the Hunter perk, you struggle to hunt and harvest meat from your kills.

- **Megaton Bomb - How do I defuse the megaton bomb?**
  - The formula now depends on intelligence, science, repair, and explosives levels. The player must be a defusal skill level of 90, which is calculated by the defusal skill formula, `((Intelligence * Science) * .05) + Repair + Explosives`.

- **Mod Order/Load Order - I accidentally messed up my mod order/load order. How do I fix it?**  
  - A backup is pre-bundled with Nuclear Sunset. You can either restore from the backup or re-run the Nuclear Sunset Wabbajack Installer, which will revert the modlist and load order to default configuration.

- **Mod Organizer 2 - Mod Organizer 2 isn't locking when I launch the game. Why?**
  - This is intentional in order to avoid long refresh times with BSA archive parsing enabled.

- **Modularity - Can I customize Nuclear Sunset to my preferences?**  
  - Nuclear Sunset is not inherently modular. Due to various complicated optimizations, plugin merges, and custom updates, modified lists are unsupported.

- **Mod Configuration Menu (MCM) - Can I change settings in the MCM?**
  - Doing so is considered modifying the list and will invalidate support.

- **Modifying Nuclear Sunset - Can I modify the mods?**
  - Modifying the list voids official support. Use the [support-modified-list](https://discord.com/channels/1445447774035251323/1445462031221264538) Discord channel for community assistance.

- **Mods - Why are there so many empty mods or mods that are completely overwritten in Nuclear Sunset?**
  - They have been merged or optimized in some fashion, though they are still included in an empty state to ensure the author receives appropriate downloads, donation points, and recognition for their creation.

- **New Vegas Heap Replacer (NVHR) - Why don't you include NVHR in the Nuclear Sunset installation?**
  - It is no longer recommended. xNVSE has built in changes to the vanilla heap that are superior to those found in NVHR, but without the massively increased memory usage that results from NVHR.

- **Nexus Upload - A new update to LODGen/Facegen/SOFT AF was posted to the Nexus page. Should I download it?**
  - No. This was uploaded in preparation for a future update, and may break the game if downloaded in isolation. Mods should only be updated when included as part of Nuclear Sunset update or when instructed to.

- **NoDelete - What does [NoDelete] mean?**  
  - This tag prevents Wabbajack from modifying the contents of tagged folders during updates.

- **NVIDIA Profile Inspector Unhandled Exception - I received an error that there is an unhandled exception when trying to run the NVIDIA Profile Inspector. How do I fix it?**
  - Update or reinstall your graphics card drivers.

- **Optimization - How is Nuclear Sunset optimized?**  
  - We used Cathedral Asset Optimizer and Nvidia Texture Tools to compress textures, downsize to 2k, and generate mipmaps. These are subsequently further adjusted by SNIFF when appropriate. Animations are compressed then BSA-packed with BSArchPro, LOD distances are optimized, and priority flags are set to load only necessary items.

- **Optional Mods - How do I use the bundled optional mods?**
  - Instructions are provided in the [Optional Mods](https://nuclearsunset.com/docs/main/setup#-optional-mods-) section.

- **Other Modded Instances - Can I keep my other modded setups while playing Nuclear Sunset?**  
  - Yes. Nuclear Sunset is self-contained in the Stock New Vegas folder and won’t interfere with other setups.

- **Overwolf - Can I use Overwolf with Nuclear Sunset?**
  - No. Overwolf causes the game to crash.

- **Pagefile - Should I increase the pagefile size for New Vegas?**  
  - No. Fallout: New Vegas has a 3.9GB memory limit, meaning that the pagefile will not even be used prior to memory-related crashes.

- **Parse Errors - Are parse errors during installation an issue?**  
  - No, as long as the installer shows "Complete" at the end.

- **Pink Screen - Why do I see pink transition screens?**  
  - You likely skipped the 4GB patching process (`FNVPatch.exe` in `[NoDelete] Stock New Vegas`).

- **Plugin No Longer Present/Mod Missing - I'm notified that certain plugins are missing. Is this an issue?**  
  - No, unless specifically noted. Some plugins may be merged or removed during optimization, which will not have a major impact on your save unless otherwise specified.

- **Purifier - Why do I return to main menu after activating the purifier? Is this a bug?**
  - You died. Try a different method of activating the purifier.

- **Radiation - ___ is too irradiated to complete! What can I do?**
  - Use a combination of a Radiation Suits, Rad-x, Radaway, and Alcohol to mitigate the effects of radiation. However, if an area is too irradiated to even be possible, please report the location in the [bug-reports](https://discord.com/channels/1445447774035251323/1445462772442857574) Discord channel.

- **Reflections - Why are landscape reflections visible in windows despite there being a building or object behind me?**  
  - This is intentional to prevent significant performance degradation.

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
