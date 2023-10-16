#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess

def make():
  if base.is_dir("./system_qt"):
    return

  # TODO: check all places...
  
  base.create_dir("./system_qt")
  base.create_dir("./system_qt/gcc_64")
  base.cmd("ln", ["-s", "/usr/lib/x86_64-linux-gnu/qt5/bin", "./system_qt/gcc_64/bin"])
  base.cmd("ln", ["-s", "/usr/lib/x86_64-linux-gnu", "./system_qt/gcc_64/lib"])
  base.cmd("ln", ["-s", "/usr/lib/x86_64-linux-gnu/qt5/plugins", "./system_qt/gcc_64/plugins"])
  return
  
if __name__ == "__main__":
  make()

