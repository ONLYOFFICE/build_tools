# **Setting up QEMU Windows 11**

## **0. Preparing for Installation**

1) Install [**MSYS2**](https://www.msys2.org/). The following commands assume that the installation directory remains the default.
2) ```pacman -S mingw-w64-x86_64-qemu```
3) Verify installation: ```C:\msys64\mingw64\bin\qemu-system-aarch64.exe --version```
4) Create an image: ```C:\msys64\mingw64\bin\qemu-img create win11-arm64.img 40G```
5) Download the Windows 11 ARM64 ISO (a VPN may be required): https://www.microsoft.com/en-us/software-download/windows11arm64
6) Download the drivers: https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md
7) Download the bootloader: https://packages.debian.org/sid/qemu-efi-aarch64  

```ar x qemu-efi-aarch64*.deb```

```tar xvf data.tar.xz```

```mv ./usr/share/qemu-efi-aarch64/QEMU_EFI.fd .```

8) Run _start.bat_  

**Note:** If you plan to install the VM elsewhere, copy _start.bat_ to that same location.

---

## **1. Installing and Configuring QEMU**

1. To install QEMU and run a Windows ARM64 virtual machine, follow this tutorial:  
   [Windows ARM64 VM using qemu-system](https://linaro.atlassian.net/wiki/spaces/WOAR/pages/28914909194/windows-arm64+VM+using+qemu-system).  
   During installation, there may be no “Back” button (as was my case); if so, you need to set the required registry variables beforehand.  
   It is strongly recommended to select the **Pro** version — functionality is not guaranteed on the Home edition.
2. Installing connection drivers is essential; details are provided at the end of the tutorial. Other drivers are optional.

---

## **2. Creating a Shared Folder**

To share files between the host Windows and the guest OS, create a folder, for example **D:\shared**.  
The _shared_ folder can also be a working repository folder; in that case, replace _shared_ with your folder name later on.

1. Right-click the folder → **Properties**.  
2. Go to **Sharing** → **Share**.  
3. In the list, select **Everyone** (or a specific user), click **Add**, grant **Read/Write** permissions, and then click **Share**.

You may also need to allow guest connections both on the host and in the guest OS. Instructions are available [here](https://learn.microsoft.com/en-us/windows-server/storage/file-server/enable-insecure-guest-logons-smb2-and-smb3?tabs=powershell).  
Now the folder is accessible from the guest machine.

---

## **3. Verification**

After starting the virtual machine, open **Command Prompt** or **PowerShell** **without** administrator rights and run:

```
net use Z: \\10.0.2.2\shared /user:guest ""
dir Z:
```

These commands should complete without errors and display a list of directories and files in the shared folder.

---

## **4. Installing VC_redist**

Additional packages are required for running software. You can download them inside the guest machine, but that may take a long time, so it’s recommended to download them on the host, place them in the shared folder, and install them from there.  

Download from:  
https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170 (choose ARM64 version).  

To install from the command line after connecting the shared folder:

```
.\Z:\VC_redist.arm64.exe
```

---

## **5. Setting Up Automatic Script Execution via Task Scheduler**

Before creating a task, remove the password from your user account so that the system logs in automatically when the VM starts.

### **Creating the Task**

1. Open **Task Scheduler** → **Create Task...**
2. **General** tab:
   - Name: Automate  
   - Run only when user is logged on  
   - Run with highest privileges  
3. **Triggers** tab:
   - New → **At log on**
4. **Actions** tab:
   - Action: **Start a program**  
   - Program/script:  
     `\\10.0.2.2\shared\build_tools\tools\win\qemu\automate.bat`

---

## **6. Config Setup**

Finally, specify the path to the folder containing the VM and the _start.bat_ script in the configuration under  
```qemu-win-arm64-dir```.  

You can do this either through `configure.py` or by editing the configuration file directly.
