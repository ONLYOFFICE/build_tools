#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

CMAKE_TOOLCHAIN_FILE = ""

def build_arch(platform, arch, folder):
  print("ixwebsocket build: " + arch + " ----------------------------------------")
  print(CMAKE_TOOLCHAIN_FILE)
  if base.is_dir(current_dir + "/IXWebSocket/build/mac/" + folder):
    base.delete_dir(current_dir + "/IXWebSocket/build/mac/" + folder)
  base.create_dir(current_dir + "/IXWebSocket/build/mac/" + folder)
  cache_dir = current_dir + "/IXWebSocket/build/mac/" + folder +"/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)

  base.cmd("cmake", ["../../../..",
    "-G","Xcode", "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE, "-DDEPLOYMENT_TARGET=10", "-DENABLE_BITCODE=1", "-DPLATFORM=" + platform, "-DARCHS=" + arch, "-DUSE_WS=0", "-DUSE_ZLIB=1", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../../openssl/build/" + folder + "/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../../openssl/build/" + folder + "/lib/libcrypto.a",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../../openssl/build/" + folder + "/lib/libssl.a",
    "-DCMAKE_INSTALL_PREFIX:PATH=/"])

  base.cmd("cmake", ["--build", ".", "--config", "Release"])
  base.cmd("cmake", ["--install", ".", "--config", "Release", "--prefix", cache_dir + "/.."])

  #base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build/mac"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: ixwebsocket_mac")
  os.chdir(current_dir)

  if not base.is_dir(current_dir + "/IXWebSocket"):
    base.cmd("git", ["clone", "https://github.com/machinezone/IXWebSocket"])

  if not base.is_dir(current_dir + "/ios-cmake"):
    base.cmd("git", ["clone", "https://github.com/leetal/ios-cmake"])

  global CMAKE_TOOLCHAIN_FILE
  CMAKE_TOOLCHAIN_FILE = current_dir + "/ios-cmake/ios.toolchain.cmake"

  os_cmd = 'cmake'
  if os.system(os_cmd) != 0:
    base.cmd("brew install", ["cmake"])

  os.chdir(current_dir + "/IXWebSocket")

#build all arch
  build_arch("MAC_ARM64", "arm64", "mac_arm64")
  build_arch("MAC", "x86_64", "mac_64")

  os.chdir(current_dir)

  os.chdir(current_dir_old)
  return