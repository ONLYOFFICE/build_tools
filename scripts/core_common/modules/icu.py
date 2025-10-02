#!/usr/bin/env python

import sys
sys.path.append('../..')
sys.path.append('android')
import config
import base
import os
import glob
import icu_android

def fetch_icu(major, minor, target_dir="icu"):
  if (base.is_dir("./icu2")):
    base.delete_dir_with_access_error("icu2")
  base.cmd("git", ["clone", "--depth", "1", "--branch", "release-" + major + "-" + minor, "https://github.com/unicode-org/icu.git", "./icu2"])
  base.copy_dir("./icu2/icu4c", target_dir)
  base.delete_dir_with_access_error("icu2")
  return

def clear_module():
  if base.is_dir("icu"):
    base.delete_dir_with_access_error("icu")

  # remove build
  for child in glob.glob("./*"):
    if base.is_dir(child):
      base.delete_dir(child)

  return

def make():
  print("[fetch & build]: icu")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.check_module_version("7", clear_module)

  if (-1 != config.option("platform").find("android")):
    icu_android.make()

  os.chdir(base_dir)

  icu_major = "74"
  icu_minor = "2"

  if not base.is_dir("icu"):
    fetch_icu(icu_major, icu_minor)

  # old version for win_xp
  icu_major_old = "58"
  icu_minor_old = "3"

  if config.check_option("platform", "win_64_xp") or config.check_option("platform", "win_32_xp"):
    if not base.is_dir("icu58"):
      fetch_icu(icu_major_old, icu_minor_old, "icu58")

  if ("windows" == base.host_platform()):
    platformToolset = "v140"
    if (config.option("vs-version") == "2019"):
      platformToolset = "v142"
    need_platforms = []
    if (-1 != config.option("platform").find("win_64")):
      need_platforms.append("win_64")
    if (-1 != config.option("platform").find("win_32")):
      need_platforms.append("win_32")
    if (-1 != config.option("platform").find("win_arm64")):
      need_platforms.append("win_64") # for exe files
      need_platforms.append("win_arm64")

    def build_icu_win(source_dir, out_dir, icu_major):
      if base.is_dir(out_dir):
        return

      compile_bat = []
      compile_bat.append("setlocal")

      args = {
        "win_32" : {
          "msbuild_platfrom" : "Win32",
          "vcvarsall_arch" : "x86",
          "out_bin_dir" : source_dir + "/bin/",
          "out_lib_dir" : source_dir + "/lib/"
        },
        "win_64" : {
          "msbuild_platfrom" : "X64",
          "vcvarsall_arch" : "x64",
          "out_bin_dir" : source_dir + "/bin64/",
          "out_lib_dir" : source_dir + "/lib64/"
        },
        "win_arm64" : {
          "msbuild_platfrom" : "ARM64",
          "vcvarsall_arch" : "x64_arm64",
          "out_bin_dir" : source_dir + "/binARM64/",
          "out_lib_dir" : source_dir + "/libARM64/"
        }
      }

      platform_args = args[platform]

      compile_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + platform_args['vcvarsall_arch'])
      compile_bat.append("call MSBuild.exe " + source_dir + "/source/allinone/allinone.sln /p:Configuration=Release /p:PlatformToolset=" + platformToolset + " /p:Platform=" + platform_args['msbuild_platfrom'])
      compile_bat.append("endlocal")
      base.run_as_bat(compile_bat)

      base.create_dir(out_dir)
      base.copy_file(platform_args['out_bin_dir'] + "icudt" + icu_major + ".dll", out_dir)
      base.copy_file(platform_args['out_bin_dir'] + "icuuc" + icu_major + ".dll", out_dir)
      base.copy_file(platform_args['out_lib_dir'] + "icudt.lib", out_dir)
      base.copy_file(platform_args['out_lib_dir'] + "icuuc.lib", out_dir)

    for platform in need_platforms:
      if not config.check_option("platform", platform) and not config.check_option("platform", platform + "_xp"):
        continue

      if not (config.check_option("platform", "win_64_xp") or config.check_option("platform", "win_32_xp")):
        build_icu_win("icu", platform + "/build", icu_major)
      else:
        # xp
        build_icu_win("icu58", platform + "/build/xp", icu_major_old)

    os.chdir(old_cur)
    return

  if ("linux" == base.host_platform()):
    if not base.is_dir(base_dir + "/linux_64"):
      base.create_dir(base_dir + "/icu/cross_build")
      os.chdir("icu/cross_build")
      command_configure = "./../source/runConfigureICU"
      command_compile_addon = "-static-libstdc++ -static-libgcc"
      if "1" == config.option("use-clang"):
        command_configure = "CXXFLAGS=-stdlib=libc++ " + command_configure
        command_compile_addon = "-stdlib=libc++"
      if "" == config.option("sysroot"):
        base.cmd(command_configure, ["Linux", "--prefix=" + base_dir + "/icu/cross_build_install"])
        base.replaceInFile("./../source/icudefs.mk.in", "LDFLAGS = @LDFLAGS@ $(RPATHLDFLAGS)", "LDFLAGS = @LDFLAGS@ $(RPATHLDFLAGS) " + command_compile_addon)
      else:
        base.set_sysroot_env()     
        base.cmd_exe("./../source/configure", ["--prefix=" + base_dir + "/icu/cross_build_install",
                                           "CC=" + config.get_custom_sysroot_bin() + "/gcc", "CXX=" + config.get_custom_sysroot_bin() + "/g++",
                                           "AR=" + config.get_custom_sysroot_bin() + "/ar", "RANLIB=" + config.get_custom_sysroot_bin() + "/ranlib",
                                           "CFLAGS=--sysroot=" + config.option("sysroot"),
                                           "CXXFLAGS=--sysroot=" + config.option("sysroot") + " " + command_compile_addon,
                                           "LDFLAGS=--sysroot=" + config.option("sysroot")])

      if "" == config.option("sysroot"):
        base.cmd("make", ["-j4"])
        base.cmd("make", ["install"], True)
      else:
        base.cmd_exe("make", ["-j4"])
        base.cmd_exe("make", ["install"], True)
        base.restore_sysroot_env()

      base.create_dir(base_dir + "/linux_64")
      base.create_dir(base_dir + "/linux_64/build")
      base.copy_file(base_dir + "/icu/cross_build_install/lib/libicudata.so." + icu_major + "." + icu_minor, base_dir + "/linux_64/build/libicudata.so." + icu_major)
      base.copy_file(base_dir + "/icu/cross_build_install/lib/libicuuc.so." + icu_major + "." + icu_minor, base_dir + "/linux_64/build/libicuuc.so." + icu_major)
      base.copy_dir(base_dir + "/icu/cross_build_install/include", base_dir + "/linux_64/build/include")

    if config.check_option("platform", "linux_arm64") and not base.is_dir(base_dir + "/linux_arm64") and not base.is_os_arm():
      base.create_dir(base_dir + "/icu/linux_arm64")
      os.chdir(base_dir + "/icu/linux_arm64")
      base_arm_tool_dir = config.option('arm64-toolchain-bin') + '/' + base.get_prefix_cross_compiler_arm64()
      base.cmd("./../source/configure", ["--host=arm-linux", "--prefix=" + base_dir + "/icu/linux_arm64_install", "--with-cross-build=" + base_dir + "/icu/cross_build",
        "CC=" + base_arm_tool_dir + "gcc", "CXX=" + base_arm_tool_dir + "g++", "AR=" + base_arm_tool_dir + "ar", "RANLIB=" + base_arm_tool_dir + "ranlib"])
      base.cmd("make", ["-j4"])
      base.cmd("make", ["install"], True)
      base.create_dir(base_dir + "/linux_arm64")
      base.create_dir(base_dir + "/linux_arm64/build")
      base.copy_file(base_dir + "/icu/linux_arm64_install/lib/libicudata.so." + icu_major + "." + icu_minor, base_dir + "/linux_arm64/build/libicudata.so." + icu_major)
      base.copy_file(base_dir + "/icu/linux_arm64_install/lib/libicuuc.so." + icu_major + "." + icu_minor, base_dir + "/linux_arm64/build/libicuuc.so." + icu_major)
      base.copy_dir(base_dir + "/icu/linux_arm64_install/include", base_dir + "/linux_arm64/build/include")

      os.chdir("../..")

  if ("mac" == base.host_platform()):
    if not base.is_file("./icu/source/tools/pkgdata/pkgdata.cpp.bak"):
      base.copy_file("./icu/source/tools/pkgdata/pkgdata.cpp", "./icu/source/tools/pkgdata/pkgdata.cpp.bak")
      base.replaceInFile("./icu/source/tools/pkgdata/pkgdata.cpp", "cmd, \"%s %s -o %s%s %s %s%s %s %s\",", "cmd, \"%s %s -o %s%s %s %s %s %s %s\",")

    # mac
    if (-1 != config.option("platform").find("mac_")) and not base.is_dir("mac_64/build"):
      base.cmd_in_dir(base_dir + "/../../../../build_tools/scripts/core_common/modules", "python", ["icu_mac.py"])

    # ios
    if (-1 != config.option("platform").find("ios")):
      if not base.is_dir("build"):
        base.bash("./icu_ios")

  os.chdir(old_cur)
  return
