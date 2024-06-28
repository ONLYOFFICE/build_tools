#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def docker_build(image_name, dockerfile_dir, base_dir):
  base.cmd("docker", ["build", "-t", image_name, dockerfile_dir])
  vlc_dir = base_dir + "/vlc"
  base.cmd("docker", ["run", "--rm", "-v", vlc_dir + ":/vlc", image_name])
  base.cmd("docker", ["image", "rm", image_name])
  return

def form_build_win(src_dir, dest_dir):
  if not base.is_dir(dest_dir):
    base.create_dir(dest_dir)
  # copy include dir
  base.copy_dir(src_dir + "/sdk/include", dest_dir + "/include")
  # form lib dir
  base.create_dir(dest_dir + "/lib")
  base.copy_file(src_dir + "/sdk/lib/libvlc.lib", dest_dir + "/lib/vlc.lib")
  base.copy_file(src_dir + "/sdk/lib/libvlccore.lib", dest_dir + "/lib/vlccore.lib")
  base.copy_dir(src_dir + "/plugins", dest_dir + "/lib/plugins")
  base.copy_file(src_dir + "/libvlc.dll", dest_dir + "/lib")
  base.copy_file(src_dir + "/libvlccore.dll", dest_dir + "/lib")
  base.copy_file(src_dir + "/vlc-cache-gen.exe", dest_dir + "/lib")
  # generate cache file 'plugins.dat' for plugins loading
  base.cmd_exe(dest_dir + "/lib/vlc-cache-gen", [dest_dir + "/lib/plugins"])
  return

def form_build_linux(src_dir, dest_dir):
  if not base.is_dir(dest_dir):
    base.create_dir(dest_dir)
  # copy include dir
  base.copy_dir(src_dir + "/include", dest_dir + "/include")
  # copy and form lib dir
  base.copy_dir(src_dir + "/lib", dest_dir + "/lib")
  base.delete_dir(dest_dir + "/lib/pkgconfig")
  base.delete_file(dest_dir + "/lib/vlc/libcompat.a")

def form_build_mac(src_dir, dest_dir):
  if not base.is_dir(dest_dir):
    base.create_dir(dest_dir)
  # copy include dir
  base.copy_dir(src_dir + "/include", dest_dir + "/include")
  # copy and form lib dir
  base.copy_dir(src_dir + "/lib", dest_dir + "/lib")
  base.cmd("find", [dest_dir + "/lib", "-name", "\"*.la\"", "-type", "f", "-delete"])
  base.delete_dir(dest_dir + "/lib/pkgconfig")
  base.delete_file(dest_dir + "/lib/vlc/libcompat.a")
  # generate cache file 'plugins.dat' for plugins loading
  base.run_command("DYLD_LIBRARY_PATH=" + dest_dir + "/lib " + dest_dir + "/lib/vlc/vlc-cache-gen " + dest_dir + "/lib/vlc/plugins")
  return

def make():

  print("[fetch & build]: libvlc")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/libvlc"
  vlc_dir = base_dir + "/vlc"
  vlc_version = "3.0.18"

  tools_dir = base.get_script_dir() + "/../tools"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  if not base.is_dir(vlc_dir):
    # temporary disable auto CRLF for Windows
    if "windows" == base.host_platform():
      autocrlf_old = base.run_command("git config --global core.autocrlf")['stdout']
      base.cmd("git", ["config", "--global", "core.autocrlf", "false"])
    base.cmd("git", ["clone", "https://code.videolan.org/videolan/vlc.git", "--branch", vlc_version])
    if "windows" == base.host_platform():
      base.cmd("git", ["config", "--global", "core.autocrlf", autocrlf_old])

  base.create_dir("build")
  base.copy_file("tools/ignore-cache-time.patch", "vlc")

  # windows
  if "windows" == base.host_platform():
    if config.check_option("platform", "win_64"):
      base.copy_file("tools/win_64/build.patch", "vlc")
      docker_build("libvlc-win64", base_dir + "/tools/win_64", base_dir)
      form_build_win(vlc_dir + "/build/win64/vlc-" + vlc_version, base_dir + "/build/win_64")

    if config.check_option("platform", "win_32"):
      base.copy_file("tools/win_32/build.patch", "vlc")
      docker_build("libvlc-win32", base_dir + "/tools/win_32", base_dir)
      form_build_win(vlc_dir + "/build/win32/vlc-" + vlc_version, base_dir + "/build/win_32")

  # linux
  if config.check_option("platform", "linux_64"):
    base.copy_file(tools_dir + "/linux/elf/patchelf", "vlc")
    base.copy_file("tools/linux_64/change-rpaths.sh", "vlc")
    docker_build("libvlc-linux64", base_dir + "/tools/linux_64", base_dir)
    form_build_linux(vlc_dir + "/build/linux_64", base_dir + "/build/linux_64")

  # mac
  if "mac" == base.host_platform():
    os.chdir(vlc_dir)

    base.cmd("git", ["restore", "src/modules/bank.c"])
    base.cmd("patch", ["-p1", "src/modules/bank.c", "../tools/ignore-cache-time.patch"])

    if config.check_option("platform", "mac_64"):
      base.cmd("git", ["restore", "extras/package/macosx/build.sh"])
      base.cmd("patch", ["-p1", "extras/package/macosx/build.sh", "../tools/mac_64/build.patch"])
      base.create_dir("build/mac_64")
      os.chdir("build/mac_64")
      base.cmd("../../extras/package/macosx/build.sh", ["-c"])
      form_build_mac(vlc_dir + "/build/mac_64/vlc_install_dir", base_dir + "/build/mac_64")

    if config.check_option("platform", "mac_arm64"):
      base.cmd("git", ["restore", "extras/package/macosx/build.sh"])
      base.cmd("patch", ["-p1", "extras/package/macosx/build.sh", "../tools/mac_arm64/build.patch"])
      base.create_dir("build/mac_arm64")
      os.chdir("build/mac_arm64")
      base.cmd("../../extras/package/macosx/build.sh", ["-c"])
      form_build_mac(vlc_dir + "/build/mac_arm64/vlc_install_dir", base_dir + "/build/mac_arm64")

  os.chdir(old_cur)
  return
