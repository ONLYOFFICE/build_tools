#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import ixwebsocket_all
import socketrocket

config_file = base.get_script_dir() + "/../../core/Common/WebSocket/websocket.pri"

def make():
  
  ixwebsocket_all.make()
  socketrocket.make()

  if (-1 != config.option("websocketlib").find("ixwebsocket")):
    base.writeFile(config_file, "CONFIG += ixwebsocket")
  elif (-1 != config.option("websocketlib").find("socketrocket")):
    base.writeFile(config_file, "CONFIG += socketrocket")

  return
