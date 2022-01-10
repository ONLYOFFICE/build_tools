#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import platform
import openssl_mobile

def clean():
  if base.is_dir("openssl"):
    base.delete_dir_with_access_error("openssl")
  if base.is_dir("build"):
    base.delete_dir("build")
  return

def make():

  print("[fetch & build]: openssl")

  if (-1 != config.option("platform").find("android") or -1 != config.option("platform").find("ios")):
    openssl_mobile.make()
    return

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.common_check_version("openssl", "3", clean)

  if not base.is_dir("openssl"):
    base.cmd("git", ["clone", "--depth=1", "--branch", "OpenSSL_1_1_1f", "https://github.com/openssl/openssl.git"])

  os.chdir(base_dir + "/openssl")

  old_cur_dir = base_dir.replace(" ", "\\ ")
  if ("windows" == base.host_platform()):
    old_cur_dir = base_dir.replace(" ", "\\ ")
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("../build/win_64"):
      base.create_dir("./../build/win_64")
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x64")      
      qmake_bat.append("perl Configure VC-WIN64A --prefix=" + old_cur_dir + "\\build\\win_64 --openssldir=" + old_cur_dir + "\\build\\win_64 no-shared no-asm")
      qmake_bat.append("call nmake clean")
      qmake_bat.append("call nmake build_libs install")
      base.run_as_bat(qmake_bat, True)
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("../build/win_32"):
      base.create_dir("./../build/win_32")
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x86")
      qmake_bat.append("perl Configure VC-WIN32 --prefix=" + old_cur_dir + "\\build\\win_32 --openssldir=" + old_cur_dir + "\\build\\win_32 no-shared no-asm")
      qmake_bat.append("call nmake clean")
      qmake_bat.append("call nmake build_libs install")
      base.run_as_bat(qmake_bat, True)
    os.chdir(old_cur)
    # xp ----------------------------------------------------------------------------------------------------
    os.chdir(base_dir + "/openssl")
    base.replaceInFile(base_dir + "/openssl/crypto/rand/rand_win.c", "define USE_BCRYPTGENRANDOM", "define USE_BCRYPTGENRANDOM_FIX")
    old_cur_dir = base_dir.replace(" ", "\\ ")
    if (-1 != config.option("platform").find("win_64_xp")) and not base.is_dir("../build/win_64_xp"):
      base.create_dir("./../build/win_64_xp")
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x64")      
      qmake_bat.append("perl Configure VC-WIN64A --prefix=" + old_cur_dir + "\\build\\win_64_xp --openssldir=" + old_cur_dir + "\\build\\win_64_xp no-shared no-asm no-async")
      qmake_bat.append("call nmake clean")
      qmake_bat.append("call nmake build_libs install")
      base.run_as_bat(qmake_bat, True)
    if (-1 != config.option("platform").find("win_32_xp")) and not base.is_dir("../build/win_32_xp"):
      base.create_dir("./../build/win_32_xp")
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x86")
      qmake_bat.append("perl Configure VC-WIN32 --prefix=" + old_cur_dir + "\\build\\win_32_xp --openssldir=" + old_cur_dir + "\\build\\win_32_xp no-shared no-asm no-async")
      qmake_bat.append("call nmake clean")
      qmake_bat.append("call nmake build_libs install")
      base.run_as_bat(qmake_bat, True)
    os.chdir(old_cur)
    # -------------------------------------------------------------------------------------------------------
    return

  if (-1 != config.option("platform").find("linux")) and not base.is_dir("../build/linux_64"):
    base.cmd("./config", ["no-shared", "no-asm", "--prefix=" + old_cur_dir + "/build/linux_64", "--openssldir=" + old_cur_dir + "/build/linux_64"])
    base.replaceInFile("./Makefile", "CFLAGS=-Wall -O3", "CFLAGS=-Wall -O3 -fvisibility=hidden")
    base.replaceInFile("./Makefile", "CXXFLAGS=-Wall -O3", "CXXFLAGS=-Wall -O3 -fvisibility=hidden")
    base.cmd("make")
    base.cmd("make", ["install"])
    # TODO: support x86

  if (-1 != config.option("platform").find("linux_arm64")) and not base.is_dir("../build/linux_arm64"):
    if ("x86_64" != platform.machine()):
      base.copy_dir("../build/linux_64", "../build/linux_arm64")
    else:
      cross_compiler_arm64 = config.option("arm64-toolchain-bin")
      if ("" == cross_compiler_arm64):
        cross_compiler_arm64 = "/usr/bin"
      cross_compiler_arm64_prefix = cross_compiler_arm64 + "/" + base.get_prefix_cross_compiler_arm64()
      base.cmd("./Configure", ["linux-aarch64", "--cross-compile-prefix=" + cross_compiler_arm64_prefix, "no-shared", "no-asm", "no-tests", "--prefix=" + old_cur_dir + "/build/linux_arm64", "--openssldir=" + old_cur_dir + "/build/linux_arm64"])
      base.replaceInFile("./Makefile", "CFLAGS=-Wall -O3", "CFLAGS=-Wall -O3 -fvisibility=hidden")
      base.replaceInFile("./Makefile", "CXXFLAGS=-Wall -O3", "CXXFLAGS=-Wall -O3 -fvisibility=hidden")
      base.cmd("make", [], True)
      base.cmd("make", ["install"], True)

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("../build/mac_64"):
    base.cmd("./Configure", ["no-shared", "no-asm", "darwin64-x86_64-cc", "--prefix=" + old_cur_dir + "/build/mac_64", "--openssldir=" + old_cur_dir + "/build/mac_64", "-mmacosx-version-min=10.11"])
    base.cmd("make", ["build_libs", "install"])

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("../build/mac_arm64"):
    os.chdir(base_dir)
    base.cmd("git", ["clone", "--depth=1", "--branch", "OpenSSL_1_1_1f", "https://github.com/openssl/openssl.git", "openssl2"])
    os.chdir(base_dir + "/openssl2")
    replace1 = "\"darwin64-x86_64-cc\" => {"
    replace2 = "\"darwin64-arm64-cc\" => {\n\
        inherit_from     => [ \"darwin-common\", asm(\"aarch64_asm\") ],\n\
        CFLAGS           => add(\"-Wall\"),\n\
        cflags           => add(\"-arch arm64 -isysroot " + base.find_mac_sdk() + "\"),\n\
        lib_cppflags     => add(\"-DL_ENDIAN\"),\n\
        bn_ops           => \"SIXTY_FOUR_BIT_LONG\",\n\
        perlasm_scheme   => \"macosx\",\n\
    },\n\
    \"darwin64-x86_64-cc\" => {"
    base.replaceInFile(base_dir + "/openssl2/Configurations/10-main.conf", replace1, replace2)
    base.cmd("./Configure", ["no-shared", "no-asm", "darwin64-arm64-cc", "--prefix=" + old_cur_dir + "/build/mac_arm64", "--openssldir=" + old_cur_dir + "/build/mac_arm64"])
    base.cmd("make", ["build_libs", "install"])

  os.chdir(old_cur)
  return
