#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess
import glob

def correct_namespace(dir):
  folder = dir
  if ("/" != folder[-1:]):
    folder += "/"
  folder += "*"
  for file in glob.glob(folder):
    if base.is_file(file):
      base.replaceInFile(file, "namespace sio", "namespace sio_no_tls")
      base.replaceInFile(file, "asio::", "asio_no_tls::")
      base.replaceInFile(file, "sio::", "sio_no_tls::")
      base.replaceInFile(file, "asio_no_tls::", "asio::")
    elif base.is_dir(file):
      correct_namespace(file)
  return

def make():
  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/socketio"
  if not base.is_dir(base_dir + "/socket.io-client-cpp"):
    base.cmd_in_dir(base_dir, "git", ["clone", "https://github.com/socketio/socket.io-client-cpp.git"])
    base.cmd_in_dir(base_dir + "/socket.io-client-cpp", "git", ["submodule", "init"])
    base.cmd_in_dir(base_dir + "/socket.io-client-cpp", "git", ["submodule", "update"])

    # no tls realization (remove if socket.io fix this)
    dst_dir = base_dir + "/socket.io-client-cpp/src_no_tls"
    base.copy_dir(base_dir + "/socket.io-client-cpp/src", dst_dir)
    correct_namespace(dst_dir)
    base.replaceInFile(dst_dir + "/internal/sio_client_impl.h", "SIO_TLS", "SIO_TLS_NO")
    base.replaceInFile(dst_dir + "/internal/sio_client_impl.cpp", "SIO_TLS", "SIO_TLS_NO")

    base.replaceInFile(dst_dir + "/sio_socket.h", "SIO_SOCKET_H", "SIO_SOCKET_NO_TLS_H")
    base.replaceInFile(dst_dir + "/sio_client.h", "SIO_CLIENT_H", "SIO_CLIENT_NO_TLS_H")
    base.replaceInFile(dst_dir + "/sio_message.h", "__SIO_MESSAGE_H__", "__SIO_MESSAGE_NO_TLS_H__")
    base.replaceInFile(dst_dir + "/internal/sio_packet.h", "SIO_PACKET_H", "SIO_PACKET_NO_TLS_H")

    old_ping = "        m_ping_timeout_timer->expires_from_now(milliseconds(m_ping_interval + m_ping_timeout), ec);"
    new_ping = "#if defined(PING_TIMEOUT_INTERVAL)\n"
    new_ping += "        m_ping_timeout_timer->expires_from_now(milliseconds(PING_TIMEOUT_INTERVAL), ec);\n"
    new_ping += "#else\n"
    new_ping += old_ping
    new_ping += "\n#endif"

    base.replaceInFile(base_dir + "/socket.io-client-cpp/src/internal/sio_client_impl.cpp", old_ping, new_ping)
    base.replaceInFile(base_dir + "/socket.io-client-cpp/src_no_tls/internal/sio_client_impl.cpp", old_ping, new_ping)
  return
