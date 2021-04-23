#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import ixwebsocket_android
import ixwebsocket_ios
import ixwebsocket_linux
import ixwebsocket_windows

def make():
  if (-1 != config.option("platform").find("android")):
    ixwebsocket_android.make()

  elif (-1 != config.option("platform").find("ios")):
    ixwebsocket_ios.make()

  elif (-1 != config.option("platform").find("linux")):
    ixwebsocket_linux.make()

  #elif (-1 != config.option("platform").find("mac")):
    #ixwebsocket_mac.make()

  elif ("windows" == base.host_platform()):
    ixwebsocket_windows.make()

  return
