#!/usr/bin/env python

import base
import config
import os
import subprocess

def make():
  path = base.get_script_dir() + "/../../core/Common/3dParty/curl"
  old_cur = os.getcwd()
  os.chdir(path)
  if (-1 != config.option("platform").find("android")):
  	  subprocess.call(["./build-android-curl.sh"])
      #base.cmd("sh", ["./build-android-curl.sh"])

  if (-1 != config.option("platform").find("ios")):
      subprocess.call(["./build-ios-curl.sh"])

  os.chdir(old_cur)
  return