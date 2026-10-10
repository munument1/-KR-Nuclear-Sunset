---
sidebar_position: 6
title: 설치 안내
hide_title: true
sidebar_label: 설치 안내
---

# ![설치 안내 배너](https://github.com/user-attachments/assets/c33fd668-6295-4c27-be33-a3c99cc33993)

:::danger 중요
다음 지침을 **지정된 순서대로 정확하게** 따르세요. 단계를 건너뛰면 설치에 문제가 생길 수 있습니다.

지원 요청 전에 [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq)에서 일반적인 오류 해결 방법을 확인하세요.
:::

<br></br>
<br></br>

### <p align="center"> ![Installing on Linux](https://github.com/user-attachments/assets/56a10969-00a9-41a6-a8ca-2b488423a1e7)</p>
<details><summary>
펼치기 - Linux 설치 안내
</summary>

Linux에서는 운영체제에 관한 평균 이상의 지식과 문제 해결 능력이 필요합니다. Linux 관련 도움이 필요하다면 공식 Discord의 [#linux-support](https://discord.com/channels/1445447774035251323/1505659799398776873) 채널을 이용하세요.

Linux 설치 지침은 Discord의 queenglizzyandthelizzywizzy가 친절하게 제공했습니다. Liz님, 감사합니다!

[Linux 설치 안내](https://nuclearsunset.com/docs/main/linux)
</details>

<br></br>
<br></br>

### <p align="center"> ![Creating Necessary File Paths](https://github.com/user-attachments/assets/7f0a2b00-9990-434d-b7e6-bc8ed273f78c) </p>
- 드라이브의 `루트 디렉터리`(예: `C:\`, `D:\`)로 이동합니다.
- `Modding`이라는 폴더를 만들고 엽니다.
- 그 안에 `Wabbajack` 폴더를 만듭니다. (**아직 열지 마세요.**)
- `Nuclear Sunset` 폴더도 만들고 엽니다.
- `Nuclear Sunset` 안에 `downloads` 폴더를 만듭니다.

:::important 다시 확인하세요
다음 경로가 실제로 존재하는지 확인하세요. 루트 드라이브 문자는 달라도 됩니다.
- `C:\Modding\Nuclear Sunset\downloads`
- `C:\Modding\Wabbajack`
:::

<br></br>
<br></br>

### <p align="center"> ![Creating Antivirus Exclusions](https://github.com/user-attachments/assets/02361941-840d-42d9-9c62-172b14385880) </p>
:::tip 이 작업을 하는 이유
이 폴더들을 백신 프로그램의 예외 항목에 추가하면 Windows 또는 타사 백신이 필수 파일을 차단하는 일을 줄일 수 있습니다.
:::

- `Windows Security`(Windows 보안)를 엽니다.
- `Virus & Threat Protection`(바이러스 및 위협 방지)으로 이동합니다.
- `Virus & Threat Protection Settings`(바이러스 및 위협 방지 설정)의 `Manage Settings`(설정 관리)를 선택합니다.
- `Exclusions`(제외)까지 스크롤한 뒤 `Add or Remove Exclusions`(제외 추가 또는 제거)를 선택합니다.
- 다음 폴더를 예외 항목에 추가합니다.
  - `C:\Modding\Nuclear Sunset`
  - `C:\Modding\Wabbajack`

![Exclusions](https://github.com/user-attachments/assets/69897eb3-f0ed-427c-beb6-548934c2e1a6)

- 타사 백신을 사용하는 경우에도 동일한 설정을 진행합니다.

:::caution 한국어판 보안 참고
백신 예외 설정은 해당 폴더에 대한 악성코드 검사를 줄이므로 보안상 위험이 커질 수 있습니다. 원본 가이드의 절차를 소개한 것이며, 신뢰할 수 없는 파일에는 적용하지 마세요. 사용 중인 보안 정책과 위험을 확인한 후 결정하세요.
:::

<br></br>
<br></br>

### <p align="center"> ![Downloading Wabbajack](https://github.com/user-attachments/assets/25c0d463-f69c-4347-b7ad-ffc7d6780787) </p>
- [Wabbajack 설치 파일](https://www.wabbajack.org/)을 다운로드합니다.
- 다운로드한 파일을 `C:\Modding\Wabbajack`로 이동합니다.
- `Wabbajack.exe`의 이름을 `Wabbajack Launcher.exe`로 변경합니다.
- `Wabbajack Launcher.exe`를 실행해 설치를 완료합니다.
- Wabbajack을 닫습니다.

:::warning 버전 확인
기존에 설치해 둔 Wabbajack이나 이전에 만든 바로 가기를 **사용하지 마세요.**

Wabbajack은 **반드시** `Wabbajack Launcher.exe`를 통해 실행해야 합니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Creating Clean Installs and Backups](https://github.com/user-attachments/assets/7674881e-a80b-4cc3-94f7-9a8630e89980) </p>
:::tip 독립 실행형 설치
기존의 모드 설치 환경에 영향을 주지 않는 **독립적인 설치본**을 만드는 첫 번째 단계입니다.
:::

:::danger
깨끗한 게임 설치본을 제대로 만들지 않으면 Nuclear Sunset 설치가 실패합니다. Steam/GOG/Epic Games에서 게임을 제거하는 것만으로는 충분하지 않습니다.
:::

- `C:\[STEAM, GOG, or EPIC FILEPATH]`로 이동하여 다음 작업을 진행합니다.
  - `Fallout New Vegas` 폴더를 바탕 화면으로 이동합니다.
  - 백업이 필요하지 않다면 `Fallout New Vegas` 폴더를 삭제해도 됩니다.
  - `Fallout 3` 폴더를 삭제합니다.
- `C:\Users\[USERNAME]\Documents\My Games`로 이동하여 다음 작업을 진행합니다.
  - `FalloutNV` 폴더를 바탕 화면으로 이동합니다.
  - 백업이 필요하지 않다면 `FalloutNV` 폴더를 삭제해도 됩니다.
  - `Fallout3` 폴더를 삭제합니다.
- `Steam, GOG, or Epic`을 열어 다음 작업을 진행합니다.
  - `Fallout: New Vegas`와 `Fallout 3`가 여전히 설치된 것으로 표시된다면 제거합니다.
  - `Fallout: New Vegas`와 `Fallout 3`를 다시 설치합니다.

:::tip 기본 설치 경로
게임 런처별 기본 경로는 다음과 같습니다.
- Steam: `C:\Program Files\Steam\steamapps\common\[Fallout: New Vegas OR Fallout 3]`
- GOG: `C:\Program Files\GOG Galaxy\Games\[Fallout: New Vegas OR Fallout 3]`
- Epic: `C:\Program Files\Epic Games\[Fallout: New Vegas OR Fallout 3 (please note that these folders are nested within a second Fallout folder)]`

정확한 경로를 찾기 어렵다면 게임 런처에서 `Fallout: New Vegas`를 마우스 오른쪽 버튼으로 클릭하고 로컬 파일 위치를 여는 메뉴를 찾으세요.
:::

:::note
여기서 준비한 깨끗한 설치본과 백업은 뒤의 [깨끗한 Stock New Vegas 폴더 만들기](https://nuclearsunset.com/docs/main/setup#-creating-a-clean-stock-new-vegas-folder-)에서 사용합니다.
:::

:::caution 파일 삭제 전 확인
기존 설치 파일과 게임 설정·저장 파일을 보존하려면 먼저 별도 위치에 백업하세요. 삭제 작업은 되돌리기 어렵습니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Generating Fresh INI Files](https://github.com/user-attachments/assets/a72c56ce-9374-457b-8056-c79e2088c404) </p>
- `Steam/GOG/Epic Games`에서 Fallout: New Vegas를 실행합니다.
- `Detecting Video Hardware`(비디오 하드웨어 감지) 메시지가 나타나면 `OK`를 선택합니다.
- 런처를 닫습니다.
- Fallout 3에서도 동일한 과정을 반복합니다.

<br></br>
<br></br>

### <p align="center"> ![Installing Nuclear Sunset](https://github.com/user-attachments/assets/85079f81-db32-48ad-b319-c8a219fe85ca) </p>
- `Wabbajack application`을 실행합니다.
- `settings` 페이지를 열어 Nexus 계정으로 로그인합니다.

![WJLogIn](https://github.com/user-attachments/assets/365c2c63-67a1-48d0-be77-15a4b6dac42f)

- `Browse Lists` 페이지를 열어 `Non-featured` 항목을 체크하고, 검색창에 `Nuclear Sunset`을 입력한 뒤 `Nuclear Sunset modlist` 이미지를 클릭합니다.

![WJBrowse](https://github.com/user-attachments/assets/c0da4d4a-fd17-46d4-a0da-6b03939da4ea)

- `Download & Install`을 클릭합니다.

![WJDownload](https://github.com/user-attachments/assets/03a2825b-c428-4c72-81f9-0ae2866742dd)

- 필요한 경우 루트 드라이브 문자를 변경한 `C:\Modding\Nuclear Sunset` 경로를 **복사**(`Ctrl+C`)하여 `Installation Location`에 **붙여넣습니다**(`Ctrl+V`).
- `Download Location`에는 `C:\Modding\Nuclear Sunset\downloads`가 **자동으로 입력됩니다.**
- 확인한 후 `Install`을 클릭합니다.

![WJNSInstall](https://github.com/user-attachments/assets/06d99a21-e2dd-4aaf-983d-af2982ec0663)

- 설치를 시작하고 `Nexus Mods API request` 창이 표시되면 승인합니다.
- Nexus Mods Premium 구독자가 아니라면 모드마다 다운로드 버튼을 수동으로 눌러야 합니다.
- 설치가 완료되면 Wabbajack 상단에 `Finished Installing Nuclear Sunset` 메시지가 표시됩니다.
- Wabbajack을 닫습니다. `Create Desktop Shortcut` 옵션은 **선택하지 마세요.**

:::danger 빨간색 `INSTALLATION FAILED` 알림
지원을 요청하기 **전에** [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq)에서 일반적인 설치 오류에 대한 초기 문제 해결 절차를 확인하세요.
:::

:::warning 주의
뒤의 단계를 시작하기 전에 설치가 **완전히 종료될 때까지** 기다리세요.

지시가 나오기 **전에 Mod Organizer 2를 실행하지 마세요.**
:::

<br></br>
<br></br>

### <p align="center"> ![Creating a Clean Stock New Vegas Folder](https://github.com/user-attachments/assets/5007576c-8c12-4685-8ee6-ae4aea333c5e) </p>
:::tip 독립 실행형 설치
기존 모드 설치본에 영향을 주지 않는 **독립적인 설치본**을 만드는 두 번째 단계입니다.
:::

#### 1단계: 깨끗한 Stock New Vegas 폴더 생성
- **새로 설치한** `C:\[STEAM, GOG, or EPIC FILEPATH]\Fallout New Vegas` 폴더로 이동합니다. 폴더 안의 **모든 파일**을 **복사**(폴더 안에서 `Ctrl+A`, `Ctrl+C`)하여 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas` 폴더에 **붙여넣습니다**(`Ctrl+V`).

#### 2단계: 기존 설치본과 모드 설치본의 백업 복구
:::important
기존 Fallout: New Vegas 모드 설치본을 **백업하지 않았다면** 2단계는 **건너뛰세요.**
:::

- `Clean Stock New Vegas folder`를 올바르게 만든 뒤 이전에 백업한 파일들을 복구합니다.
  - 앞으로 Nuclear Sunset을 업데이트할 때 깨끗한 설치본이 다시 필요하므로, 복구 전에 이 깨끗한 폴더를 별도로 백업해 두세요.
  - 바탕 화면의 `Fallout New Vegas` 폴더를 원래 `C:\[STEAM, GOG, or EPIC FILEPATH]` 위치로 되돌리고, 메시지가 나타나면 `Replace`(바꾸기)를 선택합니다.
  - 바탕 화면의 `FalloutNV` 폴더를 원래 `C:\Users\[USERNAME]\Documents\My Games` 위치로 되돌리고, 메시지가 나타나면 `Replace`(바꾸기)를 선택합니다.

:::danger
깨끗한 `Stock New Vegas` 폴더를 올바르게 만들지 않으면 게임이 실행되지 않습니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Launching Mod Organizer 2 (MO2)](https://github.com/user-attachments/assets/9a2d0b71-6761-48b9-b27c-76e5640447c2) </p>
- `C:\Modding\Nuclear Sunset`에서 `ModOrganizer.exe`를 실행합니다.
- `FalloutNV_lang.esp`를 발견했다는 메시지가 나오면 `Yes`를 선택합니다.
- `register to handle nxm links`(nxm 링크 처리 등록) 메시지가 나오면 `Yes`를 선택합니다.

:::tip Epic Games 사용자
- `executable settings`(실행 파일 설정)을 엽니다. ![executable settings](https://github.com/user-attachments/assets/744ae726-8c62-452c-8bd5-a0f75515d083)
- `Nuclear Sunset`을 선택하고 `Arguments` 입력란에 `-EpicPortal`을 추가한 다음 `Apply`를 누릅니다.

![EPIC](https://github.com/user-attachments/assets/0992c94d-e5c2-49d3-9bcf-a1d43c03abf6)
:::

<br></br>
<br></br>

### <p align="center"> ![Configuring Game Settings](https://github.com/user-attachments/assets/df73a3a0-b0c7-4a1d-b406-74f44ee30be3) </p>
:::tip Steam 폴란드어·체코어·러시아어(PCR) 버전
- `executable settings`(실행 파일 설정)을 엽니다. ![352871292-1de0e254-e1a2-4d2a-bac2-df9630e0677b](https://github.com/user-attachments/assets/744ae726-8c62-452c-8bd5-a0f75515d083)
- `Configuring Game Settings`를 선택하고 `Overwrite Steam AppID`를 체크한 다음 입력란에 `22490`을 입력하고 `Apply`를 클릭합니다.
- `Application Load Error P:0000065432` 오류가 나타나면 `22490` 대신 `22380`을 시도합니다.

![PCR](https://github.com/user-attachments/assets/7f7280e7-9a20-4ad7-a085-57021c3d6845)
:::

- MO2 오른쪽 위의 `Nuclear Sunset` 드롭다운 메뉴를 열고 `Configuring Game Settings`를 선택합니다.
- `Run`을 클릭합니다.

![Configuring Game Settings](https://github.com/user-attachments/assets/f54f07cc-83e9-4ed2-add4-bf64c383e634)

- `Options`로 이동한 뒤 `Ultra` 프리셋을 선택합니다.

:::tip 세부 설명
- `Ultra`는 텍스처를 의도한 해상도로 표시합니다. 성능에 문제가 있다면 더 낮은 `Detail` 프리셋으로 Nuclear Sunset의 모든 텍스처 해상도를 일괄 낮출 수 있으므로 사양이 낮은 컴퓨터에 도움이 될 수 있습니다.
- **`Low` 프리셋은 사용하지 마세요.** 필수 렌더링 기능이 비활성화됩니다.

![Launcher Presets](https://github.com/user-attachments/assets/ed9051aa-1a8e-4212-afcc-604be9ced244)
:::

- `Windowed` 항목이 체크되어 있다면 해제하고 모니터 해상도를 선택합니다.
  - 해상도 목록에 모니터 해상도가 없다면 MO2의 INI 편집기를 열고 `Falloutprefs.ini` 탭의 `Display` 항목에서 `iSize W`(너비), `iSize H`(높이)를 실제 화면에 맞게 직접 수정합니다.
- `OK`를 누르고 런처를 닫습니다.

![Game Settings](https://github.com/user-attachments/assets/7b3de77d-03f8-4f86-82b2-8411b5f98dd0)

:::danger 게임 설정 구성 중 충돌
지원을 요청하기 전에 [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq)에서 일반적인 문제 해결 절차를 확인하세요.
:::

<br></br>
<br></br>

### <p align="center"> ![Installing Tale of Two Wastelands (TTW)](https://github.com/user-attachments/assets/883d2bfc-80b7-4dcd-afbc-bc0611aff0b9) </p>

:::danger Required Mod
:::

- Manual Download [Tale of Two Wastelands](https://mod.pub/ttw/133/files) and extract the archive.
- Open the extracted `Tale of Two Wastelands Installer` folder. Right-click `TTW Install.exe` and select `Run as Administrator`.
- Verify that the `Fallout 3` file path matches your Steam/GOG/Epic Games Fallout 3 installation path (this should already be auto-populated).
- Copy (`Ctrl+C`) `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`, changing the Root Directory path if necessary, and paste (`Ctrl+V`) it into the `Fallout New Vegas` file path.
- Copy (`Ctrl+C`) `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)`, changing the Root Directory path if necessary, and paste (`Ctrl+V`) it into the `Tale of Two Wastelands Installation Path`.

:::danger CRITICAL - Confirm the File Path
- Ensure the installation file path is `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)`. Installing outside of the `MODS` folder will prevent the game from launching.
- Do not create a new TTW folder if you cannot find the existing one. You are likely in the wrong filepath.

	![TTW Confirm](https://github.com/user-attachments/assets/69486d67-af7e-4357-afdf-5c2f09204bfd)
:::

- Click `Install`.
- Once the installation is complete and the confirmation screen appears, close the installer.

	![TTWComplete](https://github.com/user-attachments/assets/c99bd84b-0b28-4d45-a631-8b302cba49fb)

- Manual Download [YUPTTW](https://mod.pub/ttw/133/files) and extract the archive contents into `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - YUPTTW Update`

:::tip Double Check
Navigate to `C:\Modding\Nuclear Sunset\mods`, right-click the `[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)` folder, select `Properties`, and verify that the folder size is exactly 17GB.

If not, delete the `[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)` and `[NoDelete] Stock New Vegas` folders, then repeat the steps starting from [Creating Clean Installs and Backups](https://nuclearsunset.com/docs/main/setup#-creating-clean-installs-and-backups-).
:::

:::warning
The TTW Installer **MUST** run on the copy of Fallout: New Vegas inside the `[NoDelete] Stock New Vegas` folder. A prior TTW installation **CANNOT** be moved into the Nuclear Sunset TTW mod folder. The TTW installation process performs BSA decompression, binary patching, and sound file extension alterations, which are critical for a functional installation.
:::

<br></br>
<br></br>

### <p align="center"> ![Running 4GB Patcher](https://github.com/user-attachments/assets/940d8473-617e-4d26-8c12-8ec3b4814f77) </p>
- Navigate to `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas` and run `Patcher - GOG & Steam.exe` or `Patcher - Epic.exe` depending on your game version.
- A CMD prompt popup will appear, confirming `FalloutNV.exe patched!` or `Press any key to continue...` depending on your game version. `FalloutNV_backup.exe` will also appear in the `[NoDelete] Stock New Vegas` folder.

:::danger
Failure to run the 4GB Patch will result in a pink screen or crash when launching the game.
:::

<br></br>
<br></br>

### <p align="center"> ![Disabling Base Address Randomization](https://github.com/user-attachments/assets/1231e641-2ddb-4a40-b814-7b3d470559fe) </p>
:::tip Why?
This step can prevent unforeseen crashes.
:::

- Open `Windows Security` from the `Start Menu`.
- Open `App & Browser Control` from the left sidebar.
- Open `Exploit Protection Settings` under `Exploit Protection`.
- Set `Force Randomization for Images (Mandatory ASLR)` to `Use Default (Off)`.

  ![Base Address](https://github.com/user-attachments/assets/3a1fcb3d-8bee-4aa6-a394-ece70234160a)

<br></br>
<br></br>

### <p align="center"> ![Disabling DXVK Cache Storage](https://github.com/user-attachments/assets/2c315792-eea9-4ac5-b483-1ea8a504fa47) </p>
:::tip Why?
Disabling DXVK Cache Storage prevents memory-related crashes by halting the creation of the DXVK cache.
:::

- Press the `Windows` button.
- Search for `Env`, then select `Edit the system environmental variables`.
- In the dialog box, click `Environmental Variables`.
- Under `User variables for USER NAME`, click `New`.
- Enter `DXVK_STATE_CACHE` in the `Variable name` field.
- Enter `disable` in the `Variable value` field.
- Click `OK` and exit the `Environmental Variables` window.

  ![Cache](https://github.com/user-attachments/assets/6bb4cd54-1c6f-4e91-b3ff-006cd95576f7)

- Delete any existing DXVK Cache:
  - **Steam Users**:
    - Navigate to `Steam > steamapps > shadercache > 2490` and delete `DXVK_STATE_CACHE` if it exists.
  - **GOG Users**:
    - Navigate to `Nuclear Sunset > [NoDelete] Stock New Vegas > FalloutNV.dxvk-cache` and delete `DXVK_STATE_CACHE` if it exists.

- Restart your computer for changes to take effect.

<br></br>
<br></br>

### <p align="center"> ![Installing RivaTuner Statistics Server (RTSS)](https://github.com/user-attachments/assets/587122a3-6b03-4fe7-b342-6e844df0161e) </p>
:::tip Why?
FPS limiters make the game smoother by reducing rapid FPS fluctuations and preventing timescale desync bugs.
:::

- Download and install [RTSS](https://www.guru3d.com/download/rtss-rivatuner-statistics-server-download).
- Open the `System Tray` and click the `RTSS icon`.

![RTSS Icon](https://github.com/user-attachments/assets/f6542135-e257-4053-b6c7-b7c171024a7c)

- Press the green `Add` button and select `FalloutNV.exe` from `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`. Click `OK`.

![RTSS FNV](https://github.com/user-attachments/assets/306eecdd-482b-4011-a81b-51f0a95a8b3c)

- Select `FalloutNV.exe`.
- Set `Application Detection Level` to `Low`.
- Set `Framerate Limit` to `59.95`.

![RTSS Frame](https://github.com/user-attachments/assets/ab24c6ef-f166-4518-b2da-802d89d91c0a)

:::warning 
Exceeding this value, even on powerful machines, can result in significantly increased stuttering. Exceeding 120 can result in timesync abnormalities.
:::

- Open the settings using the `Setup` button.
- Enable `Passive Waiting` and set `Framerate Limiter` to `Front Edge Sync`.
- Click `OK`, then **MINIMIZE** (not close) RTSS back to the System Tray.

![RTSS Setup](https://github.com/user-attachments/assets/eb43544d-2143-446d-a86e-777da81d27f0)


<br></br>
<br></br>

### <p align="center"> ![Nvidia Users - Applying Nvidia Profile](https://github.com/user-attachments/assets/cfc3598f-9681-4a44-a96d-2246d0168b34) </p>
:::tip Why?
Enabling Flip Model (DXVK with DXGI) reduces latency and supports HDR and VRR.
:::

- Navigate to `Nuclear Sunset > xNVIDIA Utilities`.
- Run `nvidiaProfileInspector.exe`, click `Import user defined profiles`, then select `Import Profiles`.

  ![Import Nvidia Profile](https://github.com/user-attachments/assets/976cfd96-b6ff-4c95-ac87-2b888c2dbaa2)

- In `Nuclear Sunset > xNVIDIA Utilities`, select `[#] [INF] - FNV-NvidiaProfile.nip`, then click `Open`.

  ![NVIDIA Profile Select](https://github.com/user-attachments/assets/f516b1b3-d332-4b16-82d4-61360aace48e)

- Click `OK` on the `Profile Successfully Imported!` prompt.

  ![Nvidia Successfully Imported](https://github.com/user-attachments/assets/178cdbc0-cdf1-499c-bd7d-77aecc973e41)

- Click `Apply Changes`, then close the program.

  ![Apply Nvidia Profile](https://github.com/user-attachments/assets/3cf964e6-fb5d-4407-a0dc-16d0f45b90b7)

:::warning Driver Updates
Repeat this process after every Nvidia driver update.
:::

- Disable the `NVIDIA overlay` in the NVIDIA app settings, as it can reduce performance.

  ![NVIDIA Overlay](https://github.com/user-attachments/assets/284d36b6-6f22-4346-b93f-7e1b2edce48b)

<br></br>
<br></br>

### <p align="center"> ![AMD Users - Disabling Ultra-Low Power State (ULPS)](https://github.com/user-attachments/assets/5c4bb051-58fe-465b-865d-9c3e63456f6e) </p>
:::tip Why?
The Ultra-Low Power State (ULPS) setting is enabled by default on AMD GPUs and has been associated with significant performance impact.
:::

- Download [MSI Afterburner](https://download.msi.com/uti_exe/vga/MSIAfterburnerSetup.zip?__token__=exp=1749546321~acl=/*~hmac=23e15a4588ad2bbcf279cd596b33c6b1dc5a2d193ff9a50a4b2ad66d00a7ad15) and run `MSIAfterburnerInstaller465.exe`.
- Disable `Norton 360 for Gamer`, press `Install`, then unselect `RivaTuner Statistics Server` when prompted.

	![MSIAfterBurner Install](https://github.com/user-attachments/assets/76b2246c-3cef-4a72-abf3-df000e270814)

	![RTSS No](https://github.com/user-attachments/assets/06e72450-36db-4bfc-aefd-e69f071ed8fa)

- Open the `Settings` cogwheel, enabled `Disable ULPS`, click `Apply`, then `ok`.

	![MSI Afterburner 1](https://github.com/user-attachments/assets/8b7fa6e8-be93-4807-8df1-c3eb400076a7)
	![MSI Afterburner 2](https://github.com/user-attachments/assets/cb6278f0-94b4-4d9a-8ae6-6d43bb28b23d)

- Restart your computer for the changes to take effect.

<br></br>
<br></br>

### <p align="center"> ![Selecting a Nuclear Sunset Profile](https://github.com/user-attachments/assets/16974159-4dfb-46c5-ae36-77c33b1703a2) </p>

- In MO2, select `A - Uranium Haze NVR High` from the dropdown menu, then choose a profile.

  ![NS Profile](https://github.com/user-attachments/assets/7a0f18c1-3825-491f-b045-d2cbebd5b734)
 
  - **A - Uranium Haze NVR High**:
  	- Enables all mods, settings and NVR with the highest preset of Uranium Haze.
  - **B - Uranium Haze NVR Balanced**:
  	- Enables all mods, settings and NVR with the balanced preset of Uranium Haze.
  - **C - Uranium Haze NVR Performance**:
  	- Enables all mods, settings and NVR with the performance preset of Uranium Haze.
  - **D - Hikikomori NVR High**:
  	- Enables all mods, settings and NVR with the highest preset of Hikikomori.
  - **E - Hikikomori NVR Balanced**:
  	- Enables all mods, settings and NVR with the balanced preset of Hikikomori.
  - **F - Hikikomori NVR Performance**:
  	- Enables all mods, settings and NVR with the performance preset of Hikikomori.
  - **G - Hikikomori Legacy NVR High**:
  	- Enables all mods, settings and NVR with the highest legacy preset of Hikikomori.
  - **H - Hikikomori Legacy NVR Balanced**:
    - Enables all mods, settings and NVR with the balanced legacy preset of Hikikomori.
  - **I - Hikikomori Legacy NVR Performance**:
    - Enables all mods, settings and NVR with the performance legacy preset of Hikikomori.
  - **J - Nuclear Sunset - Low Quality Profile**:
  	- Disables New Vegas Reloaded and Real Time Reflections.
  - **K - Nuclear Sunset - Very Low Quality Profile**:
  	- Disables New Vegas Reloaded additional effect and lighting mods (e.g., disables Radiation Visuals, Real Time Reflections, Lumen, and Vending Machine Flicker Emits Light).
  - **L - Debugging Profile**:
  	- Minimal load order, only essential mods enabled.

:::tip Swapping profiles
When swapping profiles, the same save can be used safely. Experiment and find out what profile works best for you!

If performance remains a concern despite changing profiles, try the recommendations listed in the `FPS/Stutter - How can I increase FPS/Reduce Stutter in Nuclear Sunset?` section of the [Frequently Asked Questions](https://nuclearsunset.com/docs/main/faq).
:::

 <br></br>
 <br></br>
 
### <p align="center"> ![Optional Mods](https://github.com/user-attachments/assets/903a4ce3-c2bb-402f-b950-868a4a93206f) </p>

- Various optional mods with associated descriptions are bundled that the user can enable or disable without voiding support.
	- When enabling or disabling an optional mod, ensure that **all other mods sharing the root name** are also enabled or disabled.
 	- These will need to be re-configured with each update.
 
  ![OptionalSeparators](https://github.com/user-attachments/assets/976d0ff7-c70e-435f-83b7-fe3939ac1cfc)

<details><summary>
Expand - Optional Mod Descriptions
</summary>

- **Optional Mods - Gameplay:**
	- **Minigames - Wordle Hack** - Replaces the hacking minigame with Wordle.
	- **Quick Start & Associated Addons - Nuclear Sunset Merge** - A merge of quick-start related mods. May be disabled by those who want to experience the Fallout 3 introduction sequence.
	- **Perk Level Calibrator** - Relevels perk requirements based on the level cap of 60.

- **Optional Mods - Balance:**
  	- **Fast Travel Expenses** - Adds a distance-based cost when fast traveling. Highly recommended to keep enabled for appropriate balance.
  	- **Life After Death** - Adds punishments to death and reloads to prevent abuse of the save reload cycle. Recommended to enable to help push a "live with the consequence of your actions" type of gameplay loop.
  	- **Permadeath** - Enables permadeath mode, in which the player only has a finite number of lives.
  	  
- **Optional Mods - Difficulty Presets:**
	- **Nuclear Sunset Hardercore** - Various settings that dramatically increase the difficulty of Nuclear Sunset. The mod includes the following changes:
		- One perk is gained every 3 levels.
		- No perks are gained after being humbled (first time travel between wastelands) until the player reaches their pre-humbled level.
		- 2 Less skill points are gained per level.
		- 3 Less SPECIAL points to allocate when creating a character.
		- Max of 5 traits can be selected when creating a character (Wild Wasteland is free).
		- Hardcore need accumulation rate is doubled.
		- Overencumbrance has a much more dramatic impact on movement speed.
		- Sleeping will restore a much smaller amount of health. 
		- Radiation resist effects are reduced by 50%.
		- One follower can now be recruited at five permanent charisma, and two followers can be recruited at ten charisma.
		- Nearly all Perk Level requirements have been increased.
		- Pip-boy can no longer be used in combat.
		- Fast travel now costs caps. This effect scales based on distance traveled and weight carried.
		- Time dilation is halved when using quick select menus.
		- Weapon sway is increased when not meeting weapon requirements.
		- The Long Haul perk has been disabled, meaning the player can no longer fast travel when over encumbered.
		- Locks and Terminals have a random chance to be a higher lock level.
		- The Cola Comrade perk has been disabled.
		- Selected bonus to health, AP, or carry weight on level up has been reduced.
		- Higher level enemies will appear earlier. 
		- Difficulty starts at normal but can be changed to Hard or Very Hard
		- Addictions last 4 days
 	- **Nuclear Sunset Softercore** - Various settings that dramatically reduce the difficulty of Nuclear Sunset. The mod includes the following changes:
		- Hardcore needs accumulation rate is 33% of the base list.
		- Weapon requirement penalties are reduced.
		- Reduced lockpicking difficulty when unlocking locks that are higher level than the player.
		- Terminal shock punishment when failing to hack a terminal is reduced.
		- The radius of irradiated locations is reduced.
		- Increases the material used by the Ammo Press and reduces the cooldown.
		- Difficulty starts at normal but can be changed to Easy or Very Easy.
		- Caps have no weight
		- Barter settings are softened
    
- **Optional - Settings:**
	- **Tutorial - Nuclear Sunset Tutorial** - A Nuclear Sunset specific tutorial.
	- **UI - 16-10 Aspect Ratio Monitor Support** - Enables support for 16:10 monitors.
	- **UI - 21-9 Aspect Ratio Monitor (Ultrawide) Support** - Enables support for ultrawide (21:9) monitors.
	- **UI - 32-9 Aspect Ratio Monitor (Super Ultrawide) Support** - Enables support for super ultrawide (32:9) monitors.
</details>

<br></br>
<br></br>

### <p align="center"> ![Launching The Game](https://github.com/user-attachments/assets/35668840-c4e6-43ad-97f6-a8a1f0ed1797) </p>

- Launch the game via MO2 with the `Nuclear Sunset` option selected.

	![Launch](https://github.com/user-attachments/assets/8f571b67-5936-4d46-bc62-eda9f5b3c053)

- If prompted that INIs are read-only, select `Clear the Read Only Flag`.
- If launching results in the game launcher opening instead of Nuclear Sunset opening, repeat the [Configuring Game Settings](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-) steps.
- After starting a new game, press `K` in the pause menu to view `Keybinds and Legend`. For more details, see the [Mod Feature Reference List](https://nuclearsunset.com/docs/main/reference).

:::danger Launch Abnormalities
- Launch Crashes:
	- Overwolf is incompatible and will cause a launch crash.
	- For other sources of launch crashes, refer to [Frequently Asked Questions](https://nuclearsunset.com/docs/main/faq) for troubleshooting steps before requesting support.
- Unmodded Fallout: New Vegas launches:
	- Re-run the [Nuclear Sunset Wabbajack Installer](https://nuclearsunset.com/docs/main/setup#-installing-nuclear-sunset-). This will repair any incorrect filepaths.
 	- DO NOT select `Play` from the game launcher. If this menu opens, repeat the [Configuring Game Settings](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-) steps.
    
    ![NoPlay](https://github.com/user-attachments/assets/dd3d35e5-6461-444e-a8aa-dfbe8b87413d)
:::

<br></br>
<br></br>

### <p align="center"> ![Modders - Installing Geck](https://github.com/user-attachments/assets/e2c64e21-d14b-4e86-a7b6-ff4a9d2b9877) </p>
:::tip Authors Only
This step is only necessary for mod authors.
:::

- Steam users:
	- Navigate to Steam and install `GECK - New Vegas Edition`.
 	- Navigate to `C:\[STEAM FILEPATH]\Fallout New Vegas` and move `SSCE5432.dll` into `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`.
 	- Move `GECK.exe` from `C:\Modding\Nuclear Sunset` into `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`.
  
- GOG users:
	- Move `GECK.exe` from `C:\Modding\Nuclear Sunset` into `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`, selecting `Replace` when prompted.

<br></br>
<br></br>

### <p align="center"> ![Controller Users](https://github.com/user-attachments/assets/589b46e6-a3d4-487e-a8a0-b00a8eefc728) </p>
:::tip For Contoller Users Only

Please follow **ALL** instructions on the **[Controller Instructions](https://nuclearsunset.com/docs/main/controller) page**.
