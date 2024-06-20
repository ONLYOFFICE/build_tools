#!/usr/bin/env python
import sys
sys.path.append('../..')
sys.path.append('android')
import base
import config
import os
import subprocess
import openssl_android

def make():
  path = base.get_script_dir() + "/../../core/Common/3dParty/openssl"
  old_cur = os.getcwd()
  os.chdir(path)
  if (-1 != config.option("platform").find("android")):
      openssl_android.make()
      
  if (-1 != config.option("platform").find("ios") and not base.is_dir("./build/ios")):
      subprocess.call(["./build-ios-openssl.sh"])

  os.chdir(old_cur)
  return