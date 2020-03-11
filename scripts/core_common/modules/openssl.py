#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def make():
  if ("windows" == base.host_platform()):
    return

  print("[fetch & build]: openssl")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  openssl_version_good = "openssl_version_1"
  openssl_version = base.readFile("./openssl.data")
  if (openssl_version != openssl_version_good):
    base.delete_file("./openssl.data")
    base.writeFile("./openssl.data", openssl_version_good)
    if base.is_dir("openssl"):
      base.delete_dir("openssl")

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
