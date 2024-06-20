#!/usr/bin/env python

import sys
sys.path.append('../..')
sys.path.append('android')
import config
import subprocess
import os
import base
import curl_android

def make():
  path = base.get_script_dir() + "/../../core/Common/3dParty/curl"
  old_cur = os.getcwd()
  os.chdir(path)
  if (-1 != config.option("platform").find("android")):
    curl_android.make()
  elif (-1 != config.option("platform").find("ios")):
    if base.is_dir(path + "/build/ios"):
      os.chdir(old_cur)
      return
    subprocess.call(["./build-ios-curl.sh"])

  os.chdir(old_cur)
  return