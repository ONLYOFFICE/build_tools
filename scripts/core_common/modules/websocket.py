#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import ixwebsocket
import socketrocket

config_file = base.get_script_dir() + "/../../core/Common/WebSocket/websocket.pri"

def make():
  ixwebsocket.make()
  socketrocket.make()

  return
