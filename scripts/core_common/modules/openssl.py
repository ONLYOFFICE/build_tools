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
  if ("windows" == base.host_platform() or "ios" == config.option("platform")):
    return

  print("[fetch & build]: openssl")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.common_check_version("openssl", "1", clean)

  if not base.is_dir("openssl"):
    base.cmd("git", ["clone", "--depth=1", "https://github.com/openssl/openssl.git"])

  os.chdir(base_dir + "/openssl")
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
