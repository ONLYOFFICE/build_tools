#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

def make():
  print("[fetch & build]: brotli")
  base.cmd_in_dir(base.get_script_dir() + "/../../core/Common/3dParty/brotli", "./make.py")
  return

if __name__ == '__main__':
  # manual compile
  make()
