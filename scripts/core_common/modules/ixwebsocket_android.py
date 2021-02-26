#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

current_path = base.get_env("PATH")

CMAKE_TOOLCHAIN_FILE = base.get_env("ANDROID_NDK_ROOT") + "/build/cmake/android.toolchain.cmake"
CMAKE_DIR = base.get_env("ANDROID_HOME") + "/cmake/3.10.2.4988404/bin"
CMAKE = CMAKE_DIR + "/cmake"
NINJA = CMAKE_DIR  + "/ninja"

def build_arch(arch, api_version):
  print("ixwebsocket build: " + arch + " ----------------------------------------")

  if base.is_dir(current_dir + "/IXWebSocket/build/" + arch):
    base.delete_dir(current_dir + "/IXWebSocket/build/" + arch)
  base.create_dir(current_dir + "/IXWebSocket/build/" + arch)
  cache_dir = current_dir + "/IXWebSocket/build/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)


# ${CMAKE} \
#     .. \
#     -DANDROID_NATIVE_API_LEVEL=23 \
#     -DANDROID_ABI=arm64-v8a, armeabi-v7a\
#     -DANDROID_TOOLCHAIN=clang \
#     -DANDROID_NDK=${ANDROID_NDK_ROOT} \
#     -G'Unix Makefiles' \
#     -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE} \
#     -DCMAKE_MAKE_PROGRAM=make \
#     -DUSE_WS=0 \
#     -DUSE_ZLIB=1 \
#     -DUSE_TLS=1 \
#     -DUSE_OPEN_SSL=1 \
#     -DOPENSSL_ROOT_DIR=/mnt/sdc/Development/StudioProjects/core/Common/3dParty/openssl/android/build/arm64-v8a \
#     -DOPENSSL_INCLUDE_DIR=/mnt/sdc/Development/StudioProjects/core/Common/3dParty/openssl/android/build/arm64-v8a/include \
#     -DOPENSSL_CRYPTO_LIBRARY=/mnt/sdc/Development/StudioProjects/core/Common/3dParty/openssl/android/build/arm64-v8a/lib/libcrypto.a \
#     -DOPENSSL_SSL_LIBRARY=/mnt/sdc/Development/StudioProjects/core/Common/3dParty/openssl/android/build/arm64-v8a/lib/libssl.a \
#     -DCMAKE_INSTALL_PREFIX:PATH=/ \

  base.cmd(CMAKE, ["../..", "-DANDROID_NATIVE_API_LEVEL=" + api_version, "-DANDROID_ABI=" + arch, "-DANDROID_TOOLCHAIN=clang", "-DANDROID_NDK=" + base.get_env("ANDROID_NDK_ROOT"),
    "-G","Unix Makefiles", "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE, "-DCMAKE_MAKE_PROGRAM=make", "-DUSE_WS=0", "-DUSE_ZLIB=1", "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1",
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../openssl/android/build/" + arch + "/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../openssl/android/build/" + arch + "/lib/libcrypto.a",
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../openssl/android/build/" + arch + "/lib/libssl.a",
    "-DCMAKE_INSTALL_PREFIX:PATH=/"])

  base.cmd("make", ["-j4"])
  base.cmd("make", ["DESTDIR=" + cache_dir + "/../" + arch, "install"])

  base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/IXWebSocket/build"):
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
