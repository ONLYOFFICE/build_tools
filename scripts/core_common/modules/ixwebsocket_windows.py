#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

current_path = base.get_env("PATH")


def build():
  print("ixwebsocket build: win_64 ----------------------------------------")

  if base.is_dir(current_dir + "/IXWebSocket/build/win_64"):
    base.delete_dir(current_dir + "/IXWebSocket/build/win_64")
  base.create_dir(current_dir + "/IXWebSocket/build/win_64")
  cache_dir = current_dir + "/IXWebSocket/build/win_64/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)
  
  base.cmd("cmake", ["../../..", 
    "-G","Visual Studio 14 2015 Win64", "-DUSE_WS=0", "-DUSE_ZLIB=0", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    #"-DPKG_CONFIG_PATH=" + cache_dir + "/../../../../../openssl/build/win_64/lib/pkgconfig",
    "-DOPENSSL_ROOT_DIR=" + cache_dir + "/../../../../../openssl/build/win_64",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../openssl/build/win_64/include",
    #"-DOPENSSL_LIBRARIES=" + cache_dir + "/../../../../../openssl/build/win_64/lib",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../openssl/build/win_64/lib/libcrypto.lib",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../openssl/build/win_64/lib/libssl.lib",
    "-DCMAKE_INSTALL_PREFIX:PATH="+cache_dir + "/../"])
  
  base.cmd("cmake", ["--build", ".", "--target", "install", "--config", "Debug"])
  #base.cmd("make", ["-j4"])
  #base.cmd("make", ["DESTDIR=" + cache_dir + "/../", "install"])

  #base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build/win_64"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: ixwebsocket_windows")
  os.chdir(current_dir)

  if not base.is_dir(current_dir + "/IXWebSocket"):
    base.cmd("git", ["clone", "https://github.com/machinezone/IXWebSocket"])


  os.chdir(current_dir + "/IXWebSocket")

  build()

  os.chdir(current_dir_old)
  return