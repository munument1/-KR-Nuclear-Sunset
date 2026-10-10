---
title: 문제 해결
hide_title: true
sidebar_label: 문제 해결
---

# ![Banner Troubleshooting](https://github.com/user-attachments/assets/ec9f604c-6306-4b72-9a5d-aad58a3b0234)


:::tip
이 페이지는 Nuclear Sunset의 다양한 문제 해결 절차를 모아 둔 곳입니다. [자주 묻는 질문](https://nuclearsunset.com/docs/main/faq) 또는 Nuclear Sunset 제작진이 안내한 경우에만 적용하세요.
:::

### <p align="center"> ![Intel iGPU Users and GPUs Without Vulkan Support - Downgrading DXVK](https://github.com/user-attachments/assets/3106c27e-5d75-47fb-a43c-5db7c97925c2) </p>

:::warning 동봉된 DXVK 버전
Nuclear Sunset에는 최신 DXVK가 포함되어 있습니다.

Intel 내장 GPU 또는 Vulkan을 지원하지 않는 구형 GPU는 동봉된 DXVK와 호환되지 않으므로 이전 버전으로 교체해야 합니다.
:::

- **Intel 내장 GPU 사용자:**
	- `C:\Modding\Nuclear Sunset\DXVK\DXVK 1.10.1` 폴더로 이동합니다.
	- `d3d9.dll`과 `dxvk.conf`를 `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas` 폴더로 이동하고, 메시지가 나타나면 `Replace`(바꾸기)를 선택합니다.

- **Vulkan을 지원하지 않는 GPU 사용자:**
	- `C:\Modding\Nuclear Sunset\DXVK\DXVK 1.10.3` 폴더로 이동합니다.
	- Move `d3d9.dll` and `dxvk.conf`into `C:\Modding\Nuclear Sunset\[NoDelete] Stock New Vegas`, selecting `Replace` when prompted.

<br></br>
<br></br>

### <p align="center"> ![Disabling Steam Overlay](https://github.com/user-attachments/assets/cb9d52c1-c9a8-403d-86f9-3261bddca031) </p>

:::tip 이 작업을 하는 이유
이 과정은 충돌과 성능 저하를 유발할 수 있는 Steam Overlay를 비활성화합니다.
:::

- `steam.exe`가 있는 `Steam Root Folder`(Steam 루트 폴더)로 이동합니다.
- `GameOverlayRenderer.dll`을 마우스 오른쪽 버튼으로 클릭해 `properties`(속성)를 엽니다.
- `security tab`(보안 탭)을 열어 `edit`(편집)를 클릭합니다.
- 모든 사용자에 대해 `Read & Execute`(읽기 및 실행) 아래의 `Deny`(거부)를 선택합니다.
- `Apply`(적용) 다음 `Yes`(예)를 클릭합니다.

  ![Steam Overlay 1](https://github.com/user-attachments/assets/49fdeabe-c964-4290-a28d-af6f06a9b1a9)

- 같은 폴더에서 `SteamOverlayVulkanLayer.dll`을 마우스 오른쪽 버튼으로 클릭해 `properties`(속성)를 엽니다.
- Open the `security tab` and click `edit`.
- Click the `Deny` option under `Read & Execute` for every user.
- Click `Apply`, then `Yes`.

  ![Steam Overlay 2](https://github.com/user-attachments/assets/0f84d294-f5f0-4a0d-9927-d0524785362f)

:::warning
Steam이 업데이트될 때마다 이 작업을 반복해야 하며, Steam 실행 시 업데이트가 발생할 수 있습니다.

Steam 설정에서 단순히 오버레이를 끄는 것만으로는 충분하지 않습니다. Steam에서 비활성화해도 오버레이 DLL이 게임에 직접 삽입되어 충돌을 일으킬 수 있습니다. 
:::

:::caution 한국어판 주의
Steam 프로그램 DLL의 파일 권한을 직접 변경하면 Steam의 정상적인 작동이나 업데이트에 영향을 미칠 수 있습니다. 해당 절차는 공식 제작진이 특정 오류에 대한 대응으로 지시한 경우에만 사용하세요.
:::
