#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

current_path = base.get_env("PATH")


def build():
  print("ixwebsocket build: linux_64 ----------------------------------------")

  if base.is_dir(current_dir + "/IXWebSocket/build/linux_64"):
    base.delete_dir(current_dir + "/IXWebSocket/build/linux_64")
  base.create_dir(current_dir + "/IXWebSocket/build/linux_64")
  cache_dir = current_dir + "/IXWebSocket/build/linux_64/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)

  base.cmd("cmake", ["../../..", 
    "-G","Unix Makefiles", "-DCMAKE_MAKE_PROGRAM=make", "-DUSE_WS=0", "-DUSE_ZLIB=1", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../openssl/build/linux_64/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../openssl/build/linux_64/lib/libcrypto.a",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../openssl/build/linux_64/lib/libssl.a",
    "-DCMAKE_INSTALL_PREFIX:PATH=/"])

  base.cmd("make", ["-j4"])
  base.cmd("make", ["DESTDIR=" + cache_dir + "/../", "install"])

  base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build/linux_64"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: ixwebsocket_linux")
  os.chdir(current_dir)

  if not base.is_dir(current_dir + "/IXWebSocket"):
    base.cmd("git", ["clone", "https://github.com/machinezone/IXWebSocket"])


  os.chdir(current_dir + "/IXWebSocket")

  build()

  os.chdir(current_dir_old)
  return

make()
