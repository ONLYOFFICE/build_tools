#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import ixwebsocket
import socketrocket
import socket_io

config_file = base.get_script_dir() + "/../../core/Common/WebSocket/websocket.pri"

def make():
  #ixwebsocket.make()
  #socketrocket.make()
  socket_io.make()

  return
