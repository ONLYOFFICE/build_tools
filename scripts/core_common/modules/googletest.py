#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import platform

def make():
  print("[fetch & build]: googletest")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/googletest"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  if not base.is_dir("googletest"):
    base.cmd("git", ["clone", "https://github.com/google/googletest.git", "-b", "v1.13.0"])

  os.chdir(old_cur)
  return
