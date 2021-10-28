#!/usr/bin/env python

import base
import config
import os
import subprocess

def make():
  path = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(path)
  base.set_env("ANDROID_HOME", base.get_android_sdk_home())

  if (-1 != config.option("platform").find("android") and not base.is_dir("./build/android")):
      subprocess.call(["./build-android-openssl.sh"])
      
  if (-1 != config.option("platform").find("ios") and not base.is_dir("./build/ios")):
      subprocess.call(["./build-ios-openssl.sh"])

  os.chdir(old_cur)
  return