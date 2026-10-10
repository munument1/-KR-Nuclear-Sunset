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
:::danger 필수 모드
:::

- [Tale of Two Wastelands](https://mod.pub/ttw/133/files)를 **수동 다운로드**하여 압축을 풉니다.
- 압축을 푼 `Tale of Two Wastelands Installer` 폴더를 엽니다. `TTW Install.exe`를 마우스 오른쪽 버튼으로 클릭하고 `Run as Administrator`(관리자 권한으로 실행)를 선택합니다.
- `Fallout 3` 경로가 Steam/GOG/Epic Games에 설치된 실제 Fallout 3 경로와 일치하는지 확인합니다. 보통 자동으로 입력되어 있습니다.
- 필요한 경우 루트 드라이브 문자를 변경한 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`를 **복사**(`Ctrl+C`)해 `Fallout New Vegas` 경로에 **붙여넣습니다**(`Ctrl+V`).
- 필요한 경우 루트 드라이브 문자를 변경한 `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)`를 **복사**(`Ctrl+C`)해 `Tale of Two Wastelands Installation Path`에 **붙여넣습니다**(`Ctrl+V`).

:::danger 매우 중요 — 설치 경로를 반드시 확인하세요
- 설치 경로가 `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)`인지 확인하세요. `MODS` 폴더 바깥에 설치하면 게임이 실행되지 않습니다.
- 기존 TTW 폴더를 찾지 못하더라도 새 TTW 폴더를 만들지 마세요. 다른 경로를 살펴보고 있을 가능성이 큽니다.

![TTW Confirm](https://github.com/user-attachments/assets/69486d67-af7e-4357-afdf-5c2f09204bfd)
:::

- `Install`을 클릭합니다.
- 설치가 끝나 확인 화면이 나타나면 설치 프로그램을 종료합니다.

![TTWComplete](https://github.com/user-attachments/assets/c99bd84b-0b28-4d45-a631-8b302cba49fb)

- [YUPTTW](https://mod.pub/ttw/133/files)를 **수동 다운로드**하고 압축 내용을 `C:\Modding\Nuclear Sunset\MODS\[NoDelete] [INF] [DB] - YUPTTW Update`에 풉니다.

:::tip 다시 확인하세요
`C:\Modding\Nuclear Sunset\mods`로 이동하여 `[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)` 폴더를 마우스 오른쪽 버튼으로 클릭하고 `Properties`(속성)를 선택합니다. 폴더의 크기가 정확히 **17GB**인지 확인합니다.

크기가 다르면 `[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)` 및 `[NoDelete] Stock New Vegas` 폴더를 삭제하고 [깨끗한 게임 설치 및 백업](https://nuclearsunset.com/docs/main/setup#-creating-clean-installs-and-backups-) 단계부터 다시 진행합니다.
:::

:::warning
TTW 설치 프로그램은 **반드시** `[NoDelete] Stock New Vegas` 폴더에 들어 있는 Fallout: New Vegas 복사본을 대상으로 실행해야 합니다. 기존에 설치해 둔 TTW를 Nuclear Sunset의 TTW 모드 폴더로 옮기는 방식은 **사용할 수 없습니다.** TTW 설치 과정에서 정상 동작에 필요한 BSA 압축 해제, 바이너리 패치, 사운드 파일 확장자 변경이 수행되기 때문입니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Running 4GB Patcher](https://github.com/user-attachments/assets/940d8473-617e-4d26-8c12-8ec3b4814f77) </p>
- `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`로 이동하여 사용 중인 게임 버전에 따라 `Patcher - GOG & Steam.exe` 또는 `Patcher - Epic.exe`를 실행합니다.
- CMD 창이 나타나며 버전에 따라 `FalloutNV.exe patched!` 또는 `Press any key to continue...`라는 메시지가 표시됩니다. `[NoDelete] Stock New Vegas` 폴더에는 `FalloutNV_backup.exe`도 생성됩니다.

:::danger
4GB 패치를 실행하지 않으면 게임을 시작할 때 화면이 분홍색으로 변하거나 게임이 종료됩니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Disabling Base Address Randomization](https://github.com/user-attachments/assets/1231e641-2ddb-4a40-b814-7b3d470559fe) </p>
:::tip 이 작업을 하는 이유
예기치 못한 충돌을 방지하는 데 도움이 될 수 있습니다.
:::

- 시작 메뉴에서 `Windows Security`(Windows 보안)를 엽니다.
- 왼쪽 메뉴의 `App & Browser Control`(앱 및 브라우저 컨트롤)을 엽니다.
- `Exploit Protection`(Exploit Protection) 아래의 `Exploit Protection Settings`(설정)를 엽니다.
- `Force Randomization for Images (Mandatory ASLR)`(이미지 강제 임의 지정)를 `Use Default (Off)`(기본값 사용 — 끔)으로 지정합니다.

![Base Address](https://github.com/user-attachments/assets/3a1fcb3d-8bee-4aa6-a394-ece70234160a)

:::caution 한국어판 보안 참고
Mandatory ASLR은 보안 완화 기능입니다. 이를 변경하면 시스템 보안에 영향을 줄 수 있습니다. 이 단계는 원본 지침을 충실히 옮긴 것이며, 조직의 보안 정책과 설정 적용 범위를 확인한 뒤 진행하세요.
:::

<br></br>
<br></br>

### <p align="center"> ![Disabling DXVK Cache Storage](https://github.com/user-attachments/assets/2c315792-eea9-4ac5-b483-1ea8a504fa47) </p>
:::tip 이 작업을 하는 이유
DXVK 캐시 파일 생성을 중단하면 메모리 관련 충돌을 방지할 수 있습니다.
:::

- `Windows` 키를 누릅니다.
- `Env`를 검색하고 `Edit the system environmental variables`(시스템 환경 변수 편집)를 선택합니다.
- 대화 상자에서 `Environmental Variables`(환경 변수)를 클릭합니다.
- `User variables for USER NAME`(사용자 변수) 아래에서 `New`(새로 만들기)를 클릭합니다.
- `Variable name`(변수 이름)에 `DXVK_STATE_CACHE`를 입력합니다.
- `Variable value`(변수 값)에 `disable`을 입력합니다.
- `OK`를 누르고 환경 변수 창을 닫습니다.

![Cache](https://github.com/user-attachments/assets/6bb4cd54-1c6f-4e91-b3ff-006cd95576f7)

- 기존 DXVK 캐시가 있다면 삭제합니다.
  - **Steam 사용자**
    - `Steam > steamapps > shadercache > 2490`로 이동하여 `DXVK_STATE_CACHE`가 존재하면 삭제합니다.
  - **GOG 사용자**
    - `Nuclear Sunset > [NoDelete] Stock New Vegas > FalloutNV.dxvk-cache`로 이동하여 `DXVK_STATE_CACHE`가 존재하면 삭제합니다.

- 변경 사항이 적용되도록 컴퓨터를 다시 시작합니다.

<br></br>
<br></br>

### <p align="center"> ![Installing RivaTuner Statistics Server (RTSS)](https://github.com/user-attachments/assets/587122a3-6b03-4fe7-b342-6e844df0161e) </p>
:::tip 이 작업을 하는 이유
FPS 제한 프로그램은 프레임 속도가 급격하게 변하는 현상을 줄여 게임을 부드럽게 하고, 시간 동기화가 어긋나는 오류를 방지합니다.
:::

- [RTSS](https://www.guru3d.com/download/rtss-rivatuner-statistics-server-download)를 다운로드하여 설치합니다.
- `System Tray`(시스템 트레이)를 열고 `RTSS` 아이콘을 클릭합니다.

![RTSS Icon](https://github.com/user-attachments/assets/f6542135-e257-4053-b6c7-b7c171024a7c)

- 녹색 `Add` 버튼을 누르고 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`에 있는 `FalloutNV.exe`를 선택한 다음 `OK`를 클릭합니다.

![RTSS FNV](https://github.com/user-attachments/assets/306eecdd-482b-4011-a81b-51f0a95a8b3c)

- `FalloutNV.exe`를 선택합니다.
- `Application Detection Level`은 `Low`로 설정합니다.
- `Framerate Limit`은 `59.95`로 설정합니다.

![RTSS Frame](https://github.com/user-attachments/assets/ab24c6ef-f166-4518-b2da-802d89d91c0a)

:::warning
강력한 컴퓨터라도 이 값을 초과하면 화면 끊김이 크게 늘어날 수 있습니다. 특히 120을 초과하면 시간 동기화에 이상이 생길 수 있습니다.
:::

- `Setup` 버튼으로 설정을 엽니다.
- `Passive Waiting`을 활성화하고 `Framerate Limiter`를 `Front Edge Sync`로 설정합니다.
- `OK`를 클릭한 뒤 RTSS를 **종료하지 말고 최소화**하여 시스템 트레이로 돌려놓습니다.

![RTSS Setup](https://github.com/user-attachments/assets/eb43544d-2143-446d-a86e-777da81d27f0)

<br></br>
<br></br>

### <p align="center"> ![Nvidia Users - Applying Nvidia Profile](https://github.com/user-attachments/assets/cfc3598f-9681-4a44-a96d-2246d0168b34) </p>
:::tip 이 작업을 하는 이유
Flip Model(DXGI와 함께 사용하는 DXVK)을 활성화하면 지연 시간이 줄어들고 HDR 및 VRR을 지원할 수 있습니다.
:::

- `Nuclear Sunset > xNVIDIA Utilities`로 이동합니다.
- `nvidiaProfileInspector.exe`를 실행하고 `Import user defined profiles`를 클릭한 다음 `Import Profiles`를 선택합니다.

![Import Nvidia Profile](https://github.com/user-attachments/assets/976cfd96-b6ff-4c95-ac87-2b888c2dbaa2)

- `Nuclear Sunset > xNVIDIA Utilities`에서 `[#] [INF] - FNV-NvidiaProfile.nip` 파일을 선택하고 `Open`을 클릭합니다.

![NVIDIA Profile Select](https://github.com/user-attachments/assets/f516b1b3-d332-4b16-82d4-61360aace48e)

- `Profile Successfully Imported!` 메시지가 나타나면 `OK`를 클릭합니다.

![Nvidia Successfully Imported](https://github.com/user-attachments/assets/178cdbc0-cdf1-499c-bd7d-77aecc973e41)

- `Apply Changes`를 클릭한 뒤 프로그램을 닫습니다.

![Apply Nvidia Profile](https://github.com/user-attachments/assets/3cf964e6-fb5d-4407-a0dc-16d0f45b90b7)

:::warning 드라이버 업데이트
Nvidia 드라이버를 업데이트할 때마다 이 작업을 다시 해야 합니다.
:::

- NVIDIA 앱의 설정에서 `NVIDIA overlay`를 비활성화합니다. 오버레이는 성능을 낮출 수 있습니다.

![NVIDIA Overlay](https://github.com/user-attachments/assets/284d36b6-6f22-4346-b93f-7e1b2edce48b)

<br></br>
<br></br>

### <p align="center"> ![AMD Users - Disabling Ultra-Low Power State (ULPS)](https://github.com/user-attachments/assets/5c4bb051-58fe-465b-865d-9c3e63456f6e) </p>
:::tip 이 작업을 하는 이유
AMD GPU에서는 Ultra-Low Power State(ULPS)가 기본적으로 활성화되어 있으며, 이 설정은 성능에 상당한 영향을 미칠 수 있습니다.
:::

- [MSI Afterburner](https://download.msi.com/uti_exe/vga/MSIAfterburnerSetup.zip?__token__=exp=1749546321~acl=/*~hmac=23e15a4588ad2bbcf279cd596b33c6b1dc5a2d193ff9a50a4b2ad66d00a7ad15)를 다운로드하고 `MSIAfterburnerInstaller465.exe`를 실행합니다.
- `Norton 360 for Gamer`를 선택 해제하고 `Install`을 누른 뒤 설치 과정에서 `RivaTuner Statistics Server`의 선택을 해제합니다.

![MSIAfterBurner Install](https://github.com/user-attachments/assets/76b2246c-3cef-4a72-abf3-df000e270814)

![RTSS No](https://github.com/user-attachments/assets/06e72450-36db-4bfc-aefd-e69f071ed8fa)

- `Settings` 톱니바퀴 버튼을 열고 `Disable ULPS`를 활성화한 뒤 `Apply`, `OK` 순서로 클릭합니다.

![MSI Afterburner 1](https://github.com/user-attachments/assets/8b7fa6e8-be93-4807-8df1-c3eb400076a7)

![MSI Afterburner 2](https://github.com/user-attachments/assets/cb6278f0-94b4-4d9a-8ae6-6d43bb28b23d)

- 설정이 적용되도록 컴퓨터를 다시 시작합니다.

:::caution 한국어판 참고
원본 MSI Afterburner 주소에는 만료될 수 있는 인증 토큰이 포함되어 있습니다. 다운로드가 실패한다면 제조사 공식 배포 페이지에서 최신 설치 파일을 확인하세요. 실행 파일 이름도 버전에 따라 달라질 수 있습니다.
:::

<br></br>
<br></br>

### <p align="center"> ![Selecting a Nuclear Sunset Profile](https://github.com/user-attachments/assets/16974159-4dfb-46c5-ae36-77c33b1703a2) </p>
- MO2의 드롭다운 메뉴에서 `A - Uranium Haze NVR High`를 선택한 뒤 원하는 프로필을 고릅니다.

![NS Profile](https://github.com/user-attachments/assets/7a0f18c1-3825-491f-b045-d2cbebd5b734)

- **A - Uranium Haze NVR High**
  - 모든 모드와 설정 및 NVR을 활성화하고 Uranium Haze의 최고 품질 프리셋을 적용합니다.
- **B - Uranium Haze NVR Balanced**
  - 모든 모드와 설정 및 NVR을 활성화하고 Uranium Haze의 균형 프리셋을 적용합니다.
- **C - Uranium Haze NVR Performance**
  - 모든 모드와 설정 및 NVR을 활성화하고 Uranium Haze의 성능 프리셋을 적용합니다.
- **D - Hikikomori NVR High**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 최고 품질 프리셋을 적용합니다.
- **E - Hikikomori NVR Balanced**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 균형 프리셋을 적용합니다.
- **F - Hikikomori NVR Performance**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 성능 프리셋을 적용합니다.
- **G - Hikikomori Legacy NVR High**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 Legacy 최고 품질 프리셋을 적용합니다.
- **H - Hikikomori Legacy NVR Balanced**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 Legacy 균형 프리셋을 적용합니다.
- **I - Hikikomori Legacy NVR Performance**
  - 모든 모드와 설정 및 NVR을 활성화하고 Hikikomori의 Legacy 성능 프리셋을 적용합니다.
- **J - Nuclear Sunset - Low Quality Profile**
  - New Vegas Reloaded와 Real Time Reflections를 비활성화합니다.
- **K - Nuclear Sunset - Very Low Quality Profile**
  - New Vegas Reloaded의 추가 효과와 조명 모드를 비활성화합니다. 예: Radiation Visuals, Real Time Reflections, Lumen, Vending Machine Flicker Emits Light 비활성화.
- **L - Debugging Profile**
  - 필수 모드만 활성화한 최소한의 로드 순서입니다.

:::tip 프로필 변경
프로필을 바꿔도 같은 저장 파일을 안전하게 사용할 수 있습니다. 여러 프로필을 시험해 보고 자신에게 맞는 설정을 찾으세요!

프로필을 변경한 뒤에도 성능 문제가 남는다면 [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq)의 `FPS/Stutter - How can I increase FPS/Reduce Stutter in Nuclear Sunset?` 항목을 참고하세요.
:::

<br></br>
<br></br>

### <p align="center"> ![Optional Mods](https://github.com/user-attachments/assets/903a4ce3-c2bb-402f-b950-868a4a93206f) </p>
- 사용자 지원 자격을 잃지 않고 활성화하거나 비활성화할 수 있는 다양한 선택 모드가 설명과 함께 포함되어 있습니다.
  - 선택 모드를 켜거나 끌 때는 **이름의 앞부분이 같은 관련 모드도 전부 함께** 활성화하거나 비활성화해야 합니다.
  - 업데이트할 때마다 선택 모드 구성을 다시 설정해야 합니다.

![OptionalSeparators](https://github.com/user-attachments/assets/976d0ff7-c70e-435f-83b7-fe3939ac1cfc)

<details><summary>
펼치기 - 선택 모드 설명
</summary>

- **Optional Mods - Gameplay (게임 플레이):**
  - **Minigames - Wordle Hack** — 해킹 미니게임을 Wordle로 대체합니다.
  - **Quick Start & Associated Addons - Nuclear Sunset Merge** — 빠른 시작 관련 모드를 병합한 구성입니다. Fallout 3의 도입부를 직접 경험하고 싶다면 비활성화할 수 있습니다.
  - **Perk Level Calibrator** — 최대 레벨 60에 맞추어 특전의 요구 레벨을 재조정합니다.

- **Optional Mods - Balance (밸런스):**
  - **Fast Travel Expenses** — 빠른 이동에 이동 거리에 비례하는 비용을 부과합니다. 균형 잡힌 게임 플레이를 위해 활성화를 강력히 권장합니다.
  - **Life After Death** — 사망과 저장 파일 불러오기에 불이익을 주어 불러오기 반복을 남용하지 못하게 합니다. 행동의 결과를 감수하는 게임 플레이를 위해 활성화를 권장합니다.
  - **Permadeath** — 플레이어의 목숨이 제한된 영구 사망 모드를 활성화합니다.

- **Optional Mods - Difficulty Presets (난이도 프리셋):**
  - **Nuclear Sunset Hardercore** — 난이도를 대폭 높이는 설정입니다. 다음과 같은 변화가 적용됩니다.
    - 3레벨마다 특전 하나를 획득합니다.
    - 두 황무지 간 첫 이동인 Humbled 상태가 된 뒤 원래 레벨을 회복할 때까지 특전을 얻지 못합니다.
    - 레벨당 기술 점수가 2점 줄어듭니다.
    - 캐릭터 생성 시 분배할 SPECIAL 점수가 3점 줄어듭니다.
    - 캐릭터 생성 시 최대 5개의 특성을 선택할 수 있습니다(Wild Wasteland는 선택 횟수에 포함되지 않음).
    - 하드코어 생존 수치가 쌓이는 속도가 두 배로 증가합니다.
    - 과적 상태에서 이동 속도가 훨씬 더 크게 감소합니다.
    - 잠을 자도 체력이 훨씬 적게 회복됩니다.
    - 방사능 저항 효과가 50% 감소합니다.
    - 영구 카리스마가 5이면 동료 1명, 10이면 동료 2명을 영입할 수 있습니다.
    - 거의 모든 특전의 요구 레벨이 상승합니다.
    - 전투 중 Pip-Boy를 사용할 수 없습니다.
    - 빠른 이동 시 이동 거리와 휴대 중량에 따라 캡을 소모합니다.
    - 빠른 선택 메뉴 사용 시 시간 감속 효과가 절반으로 줄어듭니다.
    - 무기 사용 조건을 충족하지 못하면 무기 흔들림이 더 커집니다.
    - Long Haul 특전이 비활성화되어 과적 상태에서 빠른 이동을 할 수 없습니다.
    - 잠금장치와 터미널의 잠금 등급이 무작위로 한 단계 높아질 수 있습니다.
    - Cola Comrade 특전이 비활성화됩니다.
    - 레벨 상승 시 선택하는 체력, AP 또는 휴대 중량 보너스가 감소합니다.
    - 고레벨 적이 더 이른 시점에 등장합니다.
    - 기본 난이도는 Normal이며 Hard 또는 Very Hard로 변경할 수 있습니다.
    - 중독 증상은 4일 동안 지속됩니다.
  - **Nuclear Sunset Softercore** — 난이도를 크게 완화하는 설정입니다.
    - 하드코어 생존 수치가 쌓이는 속도가 기본 목록의 33%로 줄어듭니다.
    - 무기 사용 조건 미충족에 따른 불이익이 줄어듭니다.
    - 플레이어 수준보다 높은 잠금장치를 해제할 때의 자물쇠 따기 난이도가 낮아집니다.
    - 터미널 해킹 실패로 인한 감전 불이익이 줄어듭니다.
    - 방사능 오염 지역의 반경이 줄어듭니다.
    - Ammo Press에 사용되는 재료량이 늘어나고 재사용 대기시간이 줄어듭니다.
    - 기본 난이도는 Normal이며 Easy 또는 Very Easy로 변경할 수 있습니다.
    - 캡에 무게가 적용되지 않습니다.
    - 흥정 관련 설정이 완화됩니다.

- **Optional - Settings (설정):**
  - **Tutorial - Nuclear Sunset Tutorial** — Nuclear Sunset 전용 튜토리얼입니다.
  - **UI - 16-10 Aspect Ratio Monitor Support** — 16:10 화면비 모니터를 지원합니다.
  - **UI - 21-9 Aspect Ratio Monitor (Ultrawide) Support** — 21:9 울트라와이드 모니터를 지원합니다.
  - **UI - 32-9 Aspect Ratio Monitor (Super Ultrawide) Support** — 32:9 슈퍼 울트라와이드 모니터를 지원합니다.
</details>

<br></br>
<br></br>

### <p align="center"> ![Launching The Game](https://github.com/user-attachments/assets/35668840-c4e6-43ad-97f6-a8a1f0ed1797) </p>
- MO2에서 `Nuclear Sunset` 실행 항목을 선택하고 게임을 실행합니다.

![Launch](https://github.com/user-attachments/assets/8f571b67-5936-4d46-bc62-eda9f5b3c053)

- INI 파일이 읽기 전용이라는 메시지가 나타나면 `Clear the Read Only Flag`를 선택합니다.
- Nuclear Sunset 대신 게임 런처가 실행된다면 [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-) 단계를 다시 진행하세요.
- 새 게임을 시작한 후 일시 정지 메뉴에서 `K`를 누르면 `Keybinds and Legend`(단축키 및 범례)를 볼 수 있습니다. 자세한 내용은 [모드 기능 참고표](https://nuclearsunset.com/docs/main/reference)를 확인하세요.

:::danger 게임 실행 이상
- **실행 시 충돌:**
  - Overwolf는 호환되지 않으며 실행 시 충돌을 일으킵니다.
  - 다른 실행 오류가 발생했다면 지원 요청 전에 [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq)의 해결 절차를 확인하세요.
- **모드가 적용되지 않은 Fallout: New Vegas가 실행될 때:**
  - [Nuclear Sunset Wabbajack 설치 프로그램](https://nuclearsunset.com/docs/main/setup#-installing-nuclear-sunset-)을 다시 실행합니다. 잘못된 파일 경로가 수정됩니다.
  - 게임 런처에서 `Play`를 **누르지 마세요.** 해당 메뉴가 열린다면 [게임 설정 구성](https://nuclearsunset.com/docs/main/setup#-configuring-game-settings-) 단계를 반복하세요.

![NoPlay](https://github.com/user-attachments/assets/dd3d35e5-6461-444e-a8aa-dfbe8b87413d)
:::

<br></br>
<br></br>

### <p align="center"> ![Modders - Installing Geck](https://github.com/user-attachments/assets/e2c64e21-d14b-4e86-a7b6-ff4a9d2b9877) </p>
:::tip 모드 제작자 전용
이 단계는 모드 제작자에게만 필요합니다.
:::

- **Steam 사용자**
  - Steam에서 `GECK - New Vegas Edition`을 설치합니다.
  - `C:\[STEAM FILEPATH]\Fallout New Vegas`로 이동하여 `SSCE5432.dll`을 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`로 옮깁니다.
  - `C:\Modding\Nuclear Sunset`의 `GECK.exe`를 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`로 옮깁니다.

- **GOG 사용자**
  - `C:\Modding\Nuclear Sunset`의 `GECK.exe`를 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`로 옮기고, 메시지가 나오면 `Replace`(바꾸기)를 선택합니다.

<br></br>
<br></br>

### <p align="center"> ![Controller Users](https://github.com/user-attachments/assets/589b46e6-a3d4-487e-a8a0-b00a8eefc728) </p>
:::tip 컨트롤러 사용자 전용
[컨트롤러 사용 안내](https://nuclearsunset.com/docs/main/controller) 페이지에 있는 **모든 지침**을 반드시 따르세요.
:::
