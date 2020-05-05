#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def clean():
  if base.is_dir("openssl"):
    base.delete_dir("openssl")
  return

def make():
  if ("ios" == config.option("platform")):
    return

  print("[fetch & build]: openssl")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.common_check_version("openssl", "1", clean)

  if not base.is_dir("openssl"):
    base.cmd("git", ["clone", "--depth=1", "--branch", "OpenSSL_1_1_1f", "https://github.com/openssl/openssl.git"])

  os.chdir(base_dir + "/openssl")

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
    return

  if not base.is_file("Makefile"):
    base.cmd("./config", ["no-shared", "no-asm"])

  if base.is_file("./libssl.a") and base.is_file("./libcrypto.a"):
    os.chdir(old_cur)
    return    

  if ("linux" == base.host_platform()):
    base.replaceInFile("./Makefile", "CFLAGS=-Wall -O3", "CFLAGS=-Wall -O3 -fvisibility=hidden")
    base.replaceInFile("./Makefile", "CXXFLAGS=-Wall -O3", "CXXFLAGS=-Wall -O3 -fvisibility=hidden")

  base.cmd("make", ["build_libs"])

  os.chdir(old_cur)
  return
