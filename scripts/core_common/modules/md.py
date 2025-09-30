#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def make():
  print("[fetch]: md")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/md"
 
  base.cmd_in_dir(base_dir, "python", ["fetch.py"])
  return

if __name__ == '__main__':
  # manual compile
  make()