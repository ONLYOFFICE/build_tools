#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import ixwebsocket_android
import ixwebsocket_ios

def make():
  if (-1 != config.option("platform").find("android")):
    ixwebsocket_android.make()
    return

  if (-1 != config.option("platform").find("ios")):
    ixwebsocket_ios.make()
    return

  return
