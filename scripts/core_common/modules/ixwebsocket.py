#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import ixwebsocket_android

def make():
  if (-1 != config.option("platform").find("android")):
    ixwebsocket_android.make()
    return
  return
