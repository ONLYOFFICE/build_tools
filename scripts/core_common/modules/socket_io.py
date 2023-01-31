#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def make():
  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/socketio"
  if not base.is_dir(base_dir + "/socket.io-client-cpp"):
    base.cmd_in_dir(base_dir, "git", ["clone", "https://github.com/socketio/socket.io-client-cpp.git"])
    base.cmd_in_dir(base_dir + "/socket.io-client-cpp", "git", ["submodule", "init"])
    base.cmd_in_dir(base_dir + "/socket.io-client-cpp", "git", ["submodule", "update"])
  return
