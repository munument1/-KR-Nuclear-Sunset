---
sidebar_position: 6
title: Linux 설치 안내
hide_title: true
sidebar_label: Linux 설치 안내
---

# <p align="center"> <img width="546" height="60" alt="importantnotices" src="https://github.com/user-attachments/assets/cfc2f45d-d0c9-484a-94b3-265e538757f9" /> </p>
:::danger 중요
이 가이드는 Linux 배포판이 설치된 드라이브와 같은 드라이브에 Nuclear Sunset을 설치한다고 가정합니다.

작성 당시에는 Steam 버전 Fallout: New Vegas 설치만 설명하며 GOG 및 Epic 버전은 아직 다루지 않습니다. 해당 플랫폼 안내는 향후 추가될 예정입니다.

그래픽 환경 대신 터미널 사용을 선호하는 사용자를 위해 명령어도 함께 제공합니다. 터미널을 사용하지 않는다면 파일 탐색기에서 **숨긴 파일 표시(Show Hidden Files)**를 활성화하세요.

현재 이 구성에서는 `lsfg-vk`가 작동하지 않습니다.
:::

# <p align="center"> <img width="546" height="60" alt="prerequisites" src="https://github.com/user-attachments/assets/2b91127c-dbbd-48b2-b91b-c556a68adc13" /> </p>
Linux용 FNV 4GB Patcher  
https://www.nexusmods.com/newvegas/mods/62552?tab=files

Jackify (Linux용 Wabbajack)  
https://github.com/Omni-guides/Jackify/releases
<br></br>
**반드시 Assets 항목에서 `Source code`가 아닌 `Jackify.AppImage` 파일을 다운로드하세요!**

Tale of Two Wastelands 및 YUPTTW 업데이트  
https://mod.pub/ttw/133-tale-of-two-wastelands

### <p align="center"> <img width="546" height="60" alt="creatingnecessaryfilepaths" src="https://github.com/user-attachments/assets/6db84a3d-8707-4a17-9c8f-0db14826481c" /> </p>
- 터미널을 열고 다음 명령어를 실행합니다.
- `mkdir ~/NuclearSunset ~/NuclearSunset/downloads`
- 홈 디렉터리에 `NuclearSunset` 폴더와 그 안의 `downloads` 폴더가 생성됩니다. 다른 드라이브에 설치한다면 해당 드라이브에서 이 폴더들을 만드세요.
- `Jackify.AppImage`를 `~/NuclearSunset`로 이동합니다.

### <p align="center"> <img width="546" height="60" alt="creatingcleaninstallsandbackups" src="https://github.com/user-attachments/assets/3a620e09-ee91-4608-bfa2-595f7d414703" /> </p>
- Fallout New Vegas가 설치된 폴더로 이동해 해당 폴더의 이름을 `FNVBackup`과 같은 다른 이름으로 변경합니다.
    - 일반 Steam: `mv ~/.local/share/Steam/steamapps/common/Fallout\ New\ Vegas/ ~/.local/share/Steam/steamapps/common/FNVBackup`
    - Flatpak Steam: `mv ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/Fallout\ New\ Vegas/ ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/FNVBackup`
- `compatdata` 폴더에서 `22380`을 찾아 `22380-backup`으로 이름을 변경합니다.
    - 일반 Steam: `mv ~/.local/share/Steam/steamapps/compatdata/22380 ~/.local/share/Steam/steamapps/compatdata/22380-backup`
    - Flatpak Steam: `mv ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/22380 ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/22380-backup`
- Steam에서 Fallout New Vegas와 Fallout 3를 제거합니다.
- Steam에서 Fallout New Vegas와 Fallout 3를 다시 설치합니다.

:::caution 백업 확인
다음 단계에는 백업 폴더를 복구하는 명령어도 있으므로 기존 게임과 저장 파일이 실제로 백업되었는지 먼저 확인하세요.
:::

### <p align="center"> <img width="546" height="60" alt="generating fresh ini files" src="https://github.com/user-attachments/assets/b0ee1420-0a57-4b58-b49f-5bfad94cfa58" /> </p>
- Steam에서 Fallout: New Vegas를 실행합니다.
- `Detecting Video Hardware`(비디오 하드웨어 감지) 메시지가 나타나면 `OK`를 누릅니다.
- 런처를 닫습니다.
- Fallout 3에서도 같은 과정을 진행합니다.

### <p align="center"> <img width="546" height="60" alt="installingnuclearsunset" src="https://github.com/user-attachments/assets/b06987f9-401b-4a31-98ab-5546cceb67f8" /> </p>
- 터미널을 열고 다음 명령어를 실행합니다.

`chmod +x ~/NuclearSunset/Jackify.AppImage && ./Jackify.AppImage`

- 설정 페이지를 열고 Nexus 계정으로 로그인합니다.
- 설정 페이지를 닫은 뒤 `Modlist Tasks`를 클릭하고 `Install a Modlist (Automated)`를 선택합니다.
- `Game Type`을 `Fallout: New Vegas`로, `Modlist`를 `Nuclear Sunset`으로 설정합니다.
- `Install Directory`에 `NuclearSunset` 폴더를 지정합니다.
- `Downloads Directory`에서 `NuclearSunset` 폴더로 이동한 뒤 `downloads`를 선택합니다.
- `Start Installation`을 누릅니다.

:::warning
이 과정은 일반적으로 완료까지 최소 30분 이상 걸립니다.
:::

### <p align="center"> <img width="546" height="60" alt="creatingacleanstocknewvegasfolder" src="https://github.com/user-attachments/assets/d986fd93-5533-4717-aaeb-fca2f9433f5c" /> </p>
- 새로 설치한 New Vegas 폴더로 이동해 **모든 파일**을 `~/NuclearSunset/[NoDelete] \Stock \New \Vegas`에 복사합니다.
    - 일반 Steam: `cp -r ~/.local/share/Steam/steamapps/common/Fallout\ New\ Vegas/* ~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas/`
    - Flatpak Steam: `cp -r ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/Fallout\ New\ Vegas/* ~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas/`

:::danger 중요
- `[NoDelete] Stock New Vegas`에서 `d3d9.dll`을 반드시 제거해야 합니다. **선택 사항이 아닙니다.** 이 파일은 DXVK 모드에 포함된 것이지만 Linux는 DirectX 9 게임에 DXVK를 기본적으로 사용하므로 필요하지 않습니다. 제거하지 않으면 실내에서 실외로 나갈 때마다 게임이 종료됩니다.

`rm ~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas/d3d9.dll ~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas/dxvk.conf`
:::

:::tip 기존 게임 설치본 복구
앞에서 Fallout New Vegas를 백업했다면 기존 `FNVBackup` 폴더를 `/path/to/Steam/steamapps/common/`에 다시 둘 수 있습니다.

- **일반 Steam**
    - `cp -fr ~/.local/share/Steam/steamapps/common/FNVBackup/* ~/.local/share/Steam/steamapps/common/Fallout\ New\ Vegas/`
    - `rm -rf ~/.local/share/Steam/steamapps/compatdata/22380 && mv ~/.local/share/Steam/steamapps/compatdata/22380-backup/ ~/.local/share/Steam/steamapps/compatdata/22380`
- **Flatpak Steam**
    - `cp -fr ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/NVBackup/* ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/Fallout\ New\ Vegas/`
    - `rm -rf ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/22380 && mv ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/22380-backup/ ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/22380`
:::

:::caution 한국어판 참고
`rm -rf`는 파일을 영구 삭제할 수 있습니다. 경로와 백업 상태를 확인한 뒤 실행하세요. 원문의 Flatpak 복구 명령에서는 앞에서 생성한 `FNVBackup`과 다른 `NVBackup` 폴더명을 사용하므로 실제 백업 폴더명을 먼저 확인해야 합니다.
:::

### <p align="center"> <img width="546" height="60" alt="launching mod organizer 2 (mo2)" src="https://github.com/user-attachments/assets/971f42eb-20ec-4de7-84ba-aeba449e681e" /> </p>
- Steam을 열어 게임 목록에서 Nuclear Sunset을 찾아 실행합니다.
- Jackify가 이 항목을 자동으로 생성했어야 합니다. 없다면 왼쪽 아래 `Add a Game` → `Add a Non-Steam Game`을 선택하고 새 창의 `Browse`를 누릅니다. Nuclear Sunset 폴더에서 `ModOrganizer.exe`를 선택한 뒤 `Add Selected Programs`를 클릭하세요.
- Steam 목록의 해당 항목을 마우스 오른쪽 버튼으로 클릭하여 `Properties`를 열고 `Compatibility` 탭으로 이동합니다. `Force the use of a specific Steam Play compatibility tool`을 활성화한 뒤 `Proton 11`을 선택합니다.

:::danger 중요
ProtonGE나 Proton-CachyOS 같은 사용자 지정 Proton은 사용하지 마세요. Nuclear Sunset은 이러한 버전으로 **실행되지 않습니다.** 현재 권장 버전은 `Proton 11`입니다. 최신 DXVK를 사용하려면 `Proton Experimental`을 이용할 수 있지만 문제가 생길 가능성이 더 높습니다.
:::

### <p align="center"> <img width="546" height="60" alt="configuring game settings" src="https://github.com/user-attachments/assets/1da44a96-a0d3-438d-8600-6f2568b5d6a6" /> </p>
- MO2 오른쪽 위의 `Nuclear Sunset` 드롭다운 메뉴에서 `Configuring Game Settings`를 선택하고 `Run`을 누릅니다.
- `Options`에서 `Ultra` 프리셋을 선택합니다. 이 설정이 Nuclear Sunset의 의도된 품질입니다. 사양이 낮다면 `High` 또는 `Medium`도 고려할 수 있습니다. 이 프리셋들은 Nuclear Sunset의 모든 텍스처 해상도를 일괄적으로 낮춥니다. **`Low` 프리셋은 사용하지 마세요.** 필수 렌더링 기능이 꺼집니다.
- `Windowed`가 체크되어 있으면 해제합니다.
- `OK`를 누르고 런처를 종료합니다.

### <p align="center"> <img width="546" height="60" alt="installing tale of two wasteland ()" src="https://github.com/user-attachments/assets/a57f42cf-4879-4689-8fe0-468bee211c33" /> </p>
- Jackify에는 Tale of Two Wastelands용 설치 프로그램이 내장되어 있습니다. **ModPub에서 다운로드한 설치 프로그램은 사용하지 마세요.** 해당 프로그램은 오래되었고 Wine/Proton에서 잘 작동하지 않으며 Jackify보다 설치에 훨씬 많은 시간이 걸립니다. Jackify는 Fallout 3와 Fallout: New Vegas의 설치 경로도 자동으로 찾아 게임이 설치되어 있는지 확인합니다.
- 아직 다운로드하지 않았다면 ModPub에서 Tale of Two Wastelands와 YUPTTW 파일을 받은 뒤 TTW 압축 파일을 해제합니다.
- Jackify의 `Tools Hub`에서 `Linux Installer`를 찾습니다. 설치되어 있지 않다면 설치한 뒤 실행합니다.
- `TTW .mpi File location`에서 `Browse`를 누르고 압축 파일을 해제한 위치로 이동해 `.mpi` 파일을 선택합니다.
- `Output Directory`에서 `Browse`를 누르고 `NuclearSunset/mods/`로 이동해 `[NoDelete] [INF] [DB] - Tale of Two Wastelands (TTW)` 폴더를 선택합니다.
- 설치를 시작하고 완료될 때까지 기다립니다.
- 설치가 끝나면 YUPTTW 압축 파일의 내용을 `~/NuclearSunset/mods/[NoDelete] [INF] [DB] - YUPTTW Update`에 풉니다.

### <p align="center"> <img width="546" height="60" alt="running 4gb patcher" src="https://github.com/user-attachments/assets/fdcbb225-2f8f-4f3c-bf5c-25aef5371d86" /> </p>
- 아직 다운로드하지 않았다면 Linux용 FNV 4GB 패치 압축 파일을 받아 `~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas`에 풉니다.
- `FalloutNVPatcher`를 마우스 오른쪽 버튼으로 클릭하고 `Properties` → `Permissions` 탭을 엽니다.
- `Execute`에서 `Allow executing file as program`을 체크하고 `OK`를 누릅니다.
- `FalloutNVPatcher`를 실행합니다.

터미널 사용 시 다음 명령어를 입력합니다.

`cd ~/NuclearSunset/[NoDelete]\ Stock\ New\ Vegas/`

`chmod +x FalloutNVPatcher && ./FalloutNVPatcher`

### <p align="center"> <img width="546" height="60" alt="Installing NVR Pre-requisites" src="https://github.com/user-attachments/assets/07258ed9-6e27-41e3-8d0d-54e6a425f446" /> </p>
- `protontricks`가 설치되어 있지 않다면 일반 Steam 사용자는 배포판 패키지 관리자로, Flatpak Steam 사용자는 Flatpak으로 설치합니다.
- 터미널을 열고 `protontricks --gui`를 실행합니다.
- 게임 목록에서 Nuclear Sunset을 선택합니다. 64비트 Wine 프리픽스 또는 Wine의 wow64 모드와 관련된 오류 메시지는 무시해도 됩니다.
- `Select the default wineprefix`를 선택하고 `OK`를 누릅니다.
- `Install a Windows DLL or component`를 선택합니다.
- 아래로 스크롤하여 `d3dcompiler_43`과 `d3dcompiler_47`을 선택한 뒤 `OK`를 누릅니다.
- protontricks를 닫습니다.

