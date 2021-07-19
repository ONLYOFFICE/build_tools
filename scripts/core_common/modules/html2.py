#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def make():
  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/html"
  base.cmd_in_dir(base_dir, "python", ["fetch.py"])
  return
