#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

CMAKE_TOOLCHAIN_FILE = ""

def build_arch(platform, arch):
  print("ixwebsocket build: " + arch + " ----------------------------------------")
  print(CMAKE_TOOLCHAIN_FILE)
  if base.is_dir(current_dir + "/IXWebSocket/build/ios/" + arch):
    base.delete_dir(current_dir + "/IXWebSocket/build/ios/" + arch)
  base.create_dir(current_dir + "/IXWebSocket/build/ios/" + arch)
  cache_dir = current_dir + "/IXWebSocket/build/ios/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)

#cmake .. -G Xcode -DCMAKE_TOOLCHAIN_FILE=../../ios.toolchain.cmake -DPLATFORM=OS64
#cmake --build . --config Release
#cmake --install . --config Release

  base.cmd("cmake", ["../../..",
    "-G","Xcode", "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE, "-DDEPLOYMENT_TARGET=10", "-DENABLE_BITCODE=1", "-DPLATFORM=" + platform, "-DARCHS=" + arch, "-DUSE_WS=0", "-DUSE_ZLIB=1", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../openssl/build/ios/" + arch + "/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../openssl/build/ios/" + arch + "/lib/libcrypto.a",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../openssl/build/ios/" + arch + "/lib/libssl.a",
    "-DCMAKE_INSTALL_PREFIX:PATH=/"])

  base.cmd("cmake", ["--build", ".", "--config", "Release"])
  base.cmd("cmake", ["--install", ".", "--config", "Release", "--prefix", cache_dir + "/../" + arch])
  #base.cmd("make", ["DESTDIR=" + cache_dir + "/../" + platform, "install"])

  #base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build/ios"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: ixwebsocket_ios")
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
  build_arch("OS", "armv7")
  build_arch("OS64", "arm64")
  build_arch("SIMULATOR", "i386")
  build_arch("SIMULATOR64", "x86_64")

  os.chdir(current_dir)

  base.create_dir(current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal/include")
  base.create_dir(current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal/lib")

#copy include
  if base.is_dir(current_dir + "/IXWebSocket/build/ios/armv7/include"):
     base.cmd("cp", [ "-r", current_dir + "/IXWebSocket/build/ios/armv7/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
  elif base.is_dir(current_dir + "/IXWebSocket/build/armv64/include"):
     base.cmd("cp", [ "-r", current_dir + "/IXWebSocket/build/ios/armv64/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
  elif base.is_dir(current_dir + "/IXWebSocket/build/i386/include"):
     base.cmd("cp", [ "-r", current_dir + "/IXWebSocket/build/ios/i386/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
  elif base.is_dir(current_dir + "/IXWebSocket/build/ios/x86_64/include"):
     base.cmd("cp", [ "-r", current_dir + "/IXWebSocket/build/ios/x86_64/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])

  
  # Create fat lib
  base.cmd("lipo", ["IXWebSocket/build/ios/armv7/lib/libixwebsocket.a", "IXWebSocket/build/ios/arm64/lib/libixwebsocket.a", 
    "IXWebSocket/build/ios/i386/lib/libixwebsocket.a", "IXWebSocket/build/ios/x86_64/lib/libixwebsocket.a",
    "-create", "-output", 
     "IXWebSocket/build/ios/ixwebsocket-universal/lib/libixwebsocket.a"])

  os.chdir(current_dir_old)
  return