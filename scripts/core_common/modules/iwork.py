#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def clear_module():
  directories = ["glm", "libetonyek", "libodfgen", "librevenge", "mdds"]

  for dir in directories:
    if base.is_dir(dir):
      base.delete_dir_with_access_error(dir)

def make(use_gperf = True):
  old_cur_dir = os.getcwd()

  print("[fetch & build]: iwork")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/apple"
  
  os.chdir(base_dir)
  base.check_module_version("3", clear_module)
  os.chdir(old_cur_dir)

  cmd_args = ["fetch.py"]

  if use_gperf:
    cmd_args.append("--gperf")

  base.cmd_in_dir(base_dir, "python", cmd_args)
  return

if __name__ == '__main__':
  # manual compile
  make(False)