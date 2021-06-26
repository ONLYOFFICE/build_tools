#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def clean():
  if base.is_dir("glew-2.1.0"):
    base.delete_dir("glew-2.1.0");
  return

def make():
  if ("windows" != base.host_platform()):
    return

  if not config.check_option("module", "mobile"):
    return;

  print("[fetch & build]: glew")
  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/glew"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.common_check_version("glew", "1", clean)

  if not base.is_dir("glew-2.1.0"):
    base.download("https://deac-ams.dl.sourceforge.net/project/glew/glew/2.1.0/glew-2.1.0-win32.zip", "./archive.zip")
    base.extract("./archive.zip", "./")
    base.delete_file("./archive.zip")

  os.chdir(old_cur)
  return
