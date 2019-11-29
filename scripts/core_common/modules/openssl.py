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

  if not base.is_dir("openssl"):
    base.cmd("git", ["clone", "--depth=1", "https://github.com/openssl/openssl.git"])

  os.chdir(base_dir + "/openssl")
  if not base.is_file("Makefile"):
    base.cmd("./config", ["no-shared", "no-asm"])

  base.cmd("make", ["build_libs"])

  os.chdir(old_cur)
  return
