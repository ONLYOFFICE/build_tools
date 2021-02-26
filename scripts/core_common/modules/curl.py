#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import curl_mobile

def make():
  if (-1 != config.option("platform").find("android") or -1 != config.option("platform").find("ios")):
    #curl_mobile.make()
    return
