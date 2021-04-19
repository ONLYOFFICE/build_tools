#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os
from distutils.version import LooseVersion, StrictVersion

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

CMAKE_TOOLCHAIN_FILE = base.get_env("ANDROID_NDK_ROOT") + "/build/cmake/android.toolchain.cmake"
CMAKE_DIR = base.get_env("ANDROID_HOME") + "/cmake/"

arr = os.listdir(CMAKE_DIR)
def find_last_version(arr):
  res = arr[0]
  for version in arr:
    if(LooseVersion(version) > LooseVersion(res)):
      res = version
  return res

CMAKE = CMAKE_DIR + find_last_version(arr) + "/bin/cmake"

def build_arch(arch, api_version):
  print("ixwebsocket build: " + arch + " ----------------------------------------")

  if base.is_dir(current_dir + "/IXWebSocket/build/android/" + arch):
    base.delete_dir(current_dir + "/IXWebSocket/build/android/" + arch)
  base.create_dir(current_dir + "/IXWebSocket/build/android/" + arch)
  cache_dir = current_dir + "/IXWebSocket/build/android/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)


  base.cmd(CMAKE, ["../../..", "-DANDROID_NATIVE_API_LEVEL=" + api_version, "-DANDROID_ABI=" + arch, "-DANDROID_TOOLCHAIN=clang", "-DANDROID_NDK=" + base.get_env("ANDROID_NDK_ROOT"),
    "-G","Unix Makefiles", "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE, "-DCMAKE_MAKE_PROGRAM=make", "-DUSE_WS=0", "-DUSE_ZLIB=1", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../openssl/build/android/" + arch + "/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../openssl/build/android/" + arch + "/lib/libcrypto.a",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../openssl/build/android/" + arch + "/lib/libssl.a",
    "-DCMAKE_INSTALL_PREFIX:PATH=/"])

  base.cmd("make", ["-j4"])
  base.cmd("make", ["DESTDIR=" + cache_dir + "/../" + arch, "install"])

  #base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build/android"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: ixwebsocket_android")
  os.chdir(current_dir)

  if not base.is_dir(current_dir + "/IXWebSocket"):
    base.cmd("git", ["clone", "https://github.com/machinezone/IXWebSocket"])


  os.chdir(current_dir + "/IXWebSocket")

  build_arch("arm64-v8a", "21")
  build_arch("armeabi-v7a", "16")
  build_arch("x86_64","21")
  build_arch("x86", "16")

  os.chdir(current_dir_old)
  return