#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os
import subprocess

def clear_module():
  if base.is_dir("libxml2"):
    base.delete_dir_with_access_error(dir)

def make():
  old_cur_dir = os.getcwd()

  print("[fetch]: libxml2")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/libxml/"
  
  os.chdir(base_dir)
  base.check_module_version("1", clear_module)
  os.chdir(old_cur_dir)

  base.cmd_in_dir(base_dir, "python", ["fetch.py"])
  return

if __name__ == '__main__':
  # manual compile
  make()