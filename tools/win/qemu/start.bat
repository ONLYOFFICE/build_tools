@echo off
REM ========================================================
REM  INSTALL Windows ARM64 VM (QEMU on Windows x64)
REM ========================================================

C:\msys64\mingw64\bin\qemu-system-aarch64 ^
 -M virt -m 8G -cpu max,pauth-impdef=on -smp 8 ^
 -bios ./QEMU_EFI.fd ^
 -accel tcg,thread=multi ^
 -device ramfb ^
 -device qemu-xhci -device usb-kbd -device usb-tablet ^
 -nic user,model=virtio-net-pci ^
 -device usb-storage,drive=install ^
 -drive if=none,id=install,format=raw,media=cdrom,file=./Win11_24H2_English_Arm64.iso ^
 -device usb-storage,drive=virtio-drivers ^
 -drive if=none,id=virtio-drivers,format=raw,media=cdrom,file=./virtio-win-0.1.271.iso ^
 -drive if=virtio,id=system,format=raw,file=./win11-arm64.img
