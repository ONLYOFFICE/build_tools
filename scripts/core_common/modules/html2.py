#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def clear_module():
  directories = ["gumbo-parser", "katana-parser"]

  for dir in directories:
    if base.is_dir(dir):
      base.delete_dir_with_access_error(dir)

def make():
  old_cur_dir = os.getcwd()

  print("[fetch]: html")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/html"
  
  os.chdir(base_dir)
  base.check_module_version("2", clear_module)
  os.chdir(old_cur_dir)

  base.cmd_in_dir(base_dir, "python", ["fetch.py"])
  return

if __name__ == '__main__':
  # manual compile
  make()
