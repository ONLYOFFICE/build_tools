#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os
import config
from distutils.version import LooseVersion, StrictVersion

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/ixwebsocket"

CMAKE = "cmake"

def find_last_version(arr_input, base_directory):
    arr = []
    for arr_rec in arr_input:
      if base.is_file(base_directory + "/" + arr_rec + "/bin/cmake"):
        arr.append(arr_rec)
    res = arr[0]
    for version in arr:
      if(LooseVersion(version) > LooseVersion(res)):
        res = version
    return res

def build_arch(platform, arch, params, is_debug=False):
  print("ixwebsocket build: " + platform + "....." + arch + " ----------------------------------------")

  if base.is_dir(current_dir + "/IXWebSocket/build/"+ platform + "/" + arch):
    base.delete_dir(current_dir + "/IXWebSocket/build/" + platform + "/" + arch)
  base.create_dir(current_dir + "/IXWebSocket/build/" + platform + "/" + arch)
  cache_dir = current_dir + "/IXWebSocket/build/" + platform + "/cache"
  base.create_dir(cache_dir)
  os.chdir(cache_dir)

  libext = "a" 
  prefix = "/"
  zlib = "1"
  if (0 == platform.find("windows")):
    zlib = "0"
    libext = "lib"
    prefix = cache_dir + "/../" + arch

  path = platform
  if(platform == "ios" or platform == "android"):
    path += "/"
  else:
    path = ""

  base.cmd(CMAKE, ["../../..",
    "-DUSE_WS=0", "-DUSE_ZLIB=" + zlib, "-DUSE_TLS=1", "-DUSE_OPEN_SSL=1", 
    "-DOPENSSL_ROOT_DIR=" + cache_dir + "/../../../../../openssl/build/" + path + arch,
    "-DOPENSSL_INCLUDE_DIR=" + cache_dir + "/../../../../../openssl/build/"  + path + arch + "/include",
    "-DOPENSSL_CRYPTO_LIBRARY=" + cache_dir + "/../../../../../openssl/build/" + path + arch + "/lib/libcrypto." + libext,
    "-DOPENSSL_SSL_LIBRARY=" + cache_dir + "/../../../../../openssl/build/" + path + arch + "/lib/libssl." + libext,
    "-DCMAKE_INSTALL_PREFIX:PATH=" + prefix] + params)

  if(-1 != platform.find("ios") or -1 != platform.find("mac")):
    base.cmd(CMAKE, ["--build", ".", "--config", "Release"])
    base.cmd(CMAKE, ["--install", ".", "--config", "Release", "--prefix", cache_dir + "/../" + arch])
  elif(-1 != platform.find("android") or -1 != platform.find("linux")):
    base.cmd("make", ["-j4"])
    base.cmd("make", ["DESTDIR=" + cache_dir + "/../" + arch, "install"])
  elif(-1 != platform.find("windows")):
    conf = "Debug" if is_debug else "Release"
    base.cmd(CMAKE, ["--build", ".", "--target", "install", "--config", conf])

  base.delete_dir(cache_dir)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  print("[fetch & build]: ixwebsocket")

  current_dir_old = os.getcwd()
  
  os.chdir(current_dir)

  if not base.is_dir(current_dir + "/IXWebSocket"):
    base.cmd("git", ["clone", "https://github.com/machinezone/IXWebSocket"])


  # build for platform
  if (-1 != config.option("platform").find("android")):
   if base.is_dir(current_dir + "/IXWebSocket/build/android"):
    os.chdir(current_dir_old)
    return

   os.chdir(current_dir + "/IXWebSocket")

   global CMAKE

   CMAKE_TOOLCHAIN_FILE = base.get_env("ANDROID_NDK_ROOT") + "/build/cmake/android.toolchain.cmake"
   CMAKE_DIR = base.get_android_sdk_home() + "/cmake/"
   CMAKE = CMAKE_DIR + find_last_version(os.listdir(CMAKE_DIR), CMAKE_DIR) + "/bin/cmake"

   def param_android(arch, api):
    return ["-G","Unix Makefiles", "-DANDROID_NATIVE_API_LEVEL=" + api, "-DANDROID_ABI=" + arch, "-DANDROID_TOOLCHAIN=clang", "-DANDROID_NDK=" + base.get_env("ANDROID_NDK_ROOT"), "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE, "-DCMAKE_MAKE_PROGRAM=make"]

   build_arch("android", "arm64-v8a", param_android("arm64-v8a", "21"))
   build_arch("android", "armeabi-v7a", param_android("armeabi-v7a", "16"))
   build_arch("android", "x86_64", param_android("x86_64", "21"))
   build_arch("android", "x86", param_android("x86", "16"))


  elif (-1 != config.option("platform").find("ios") or -1 != config.option("platform").find("mac")):
    platform = "ios" if -1 != config.option("platform").find("ios") else "mac"
    if base.is_dir(current_dir + "/IXWebSocket/build/" + platform):
      os.chdir(current_dir_old)
      return

    if not base.is_dir(current_dir + "/ios-cmake"):
     base.cmd("git", ["clone", "https://github.com/leetal/ios-cmake"])

    CMAKE_TOOLCHAIN_FILE = current_dir + "/ios-cmake/ios.toolchain.cmake"

    os_cmd = 'cmake'
    if os.system(os_cmd) != 0:
      base.cmd("brew install", ["cmake"])

    os.chdir(current_dir + "/IXWebSocket")

    def param_apple(platform, arch):
      return ["-G","Xcode", "-DDEPLOYMENT_TARGET=10", "-DENABLE_BITCODE=1", "-DPLATFORM=" + platform, "-DARCHS=" + arch, "-DCMAKE_TOOLCHAIN_FILE=" + CMAKE_TOOLCHAIN_FILE]

    if(platform == "ios"):
      build_arch("ios", "armv7", param_apple("OS", "armv7"))
      build_arch("ios", "arm64", param_apple("OS64", "arm64"))
      build_arch("ios", "i386", param_apple("SIMULATOR", "i386"))
      build_arch("ios", "x86_64", param_apple("SIMULATOR64", "x86_64"))
    else:
      build_arch("mac", "mac_arm64", param_apple("MAC_ARM64", "arm64"))
      build_arch("mac", "mac_64", param_apple("MAC", "x86_64"))

    os.chdir(current_dir)

    if(platform == "ios"):
      base.create_dir(current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal/include")
      base.create_dir(current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal/lib")

      #copy include
      prefix_dir = current_dir + "/IXWebSocket/build/ios/"
      postfix_dir = ""
      if base.is_dir(prefix_dir + "armv7/usr"):
        postfix_dir = "/usr"

      if base.is_dir(prefix_dir + "armv7" + postfix_dir + "/include"):
         base.cmd("cp", [ "-r", prefix_dir + "armv7" + postfix_dir + "/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
      elif base.is_dir(prefix_dir + "armv64" + postfix_dir + "/include"):
         base.cmd("cp", [ "-r", prefix_dir + "armv64" + postfix_dir + "/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
      elif base.is_dir(prefix_dir + "i386" + postfix_dir + "/include"):
         base.cmd("cp", [ "-r", prefix_dir + "i386" + postfix_dir + "/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])
      elif base.is_dir(prefix_dir + "x86_64" + postfix_dir + "/include"):
         base.cmd("cp", [ "-r", prefix_dir + "x86_64" + postfix_dir + "/include", current_dir + "/IXWebSocket/build/ios/ixwebsocket-universal"])

      # Create fat lib
      base.cmd("lipo", ["IXWebSocket/build/ios/armv7" + postfix_dir + "/lib/libixwebsocket.a", "IXWebSocket/build/ios/arm64" + postfix_dir + "/lib/libixwebsocket.a", 
        "IXWebSocket/build/ios/i386" + postfix_dir + "/lib/libixwebsocket.a", "IXWebSocket/build/ios/x86_64" + postfix_dir + "/lib/libixwebsocket.a",
        "-create", "-output", 
         "IXWebSocket/build/ios/ixwebsocket-universal/lib/libixwebsocket.a"])


  elif (-1 != config.option("platform").find("linux")):
    if base.is_dir(current_dir + "/IXWebSocket/build/linux"):
      os.chdir(current_dir_old)
      return
     
    #will support when openssl x86 will support
    #if (-1 != config.option("platform").find("linux_32")):
      #build_arch("linux", "linux_32", ["-G","Unix Makefiles", "-DCMAKE_MAKE_PROGRAM=make", "-DCMAKE_C_FLAGS=-m32", "-DCMAKE_CXX_FLAGS=-m32"])
    if (-1 != config.option("platform").find("linux_64")):
      build_arch("linux", "linux_64", ["-G","Unix Makefiles", "-DCMAKE_MAKE_PROGRAM=make"])


  elif ("windows" == base.host_platform()):
    if base.is_dir(current_dir + "/IXWebSocket/build/windows"):
      os.chdir(current_dir_old)
      return

    vsVersion = "14 2015"
    if (config.option("vs-version") == "2019"):
      vsVersion = "16 2019"

    if (-1 != config.option("platform").find("win_32")):
      build_arch("windows", "win_32", ["-G","Visual Studio " + vsVersion, "-A", "Win32"])
      build_arch("windows_debug", "win_32", ["-G","Visual Studio" + vsVersion, "-A", "Win32"], True)      
    if (-1 != config.option("platform").find("win_64")):
      build_arch("windows", "win_64", ["-G","Visual Studio " + vsVersion + " Win64"])
      build_arch("windows_debug", "win_64", ["-G","Visual Studio " + vsVersion + " Win64"], True)

  os.chdir(current_dir_old)
  return