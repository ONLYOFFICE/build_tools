#!/usr/bin/env python

import sys
sys.path.append('../../../scripts')
import base
import os
import re

def get_android_ndk_version():
  env_val = base.get_env("ANDROID_NDK_ROOT")
  if (env_val == ""):
    env_val = "21.1.6352462" 
  return env_val.strip("/").split("/")[-1]

def get_android_ndk_version_major():
  val = get_android_ndk_version().split(".")[0]
  val = re.sub("[^0-9]", "", val)
  return int(val)

def get_sdk_api():
  if (23 > get_android_ndk_version_major()):
    return "21"
  return "23"

global archs
archs = ["arm64", "arm", "x86_64", "x86"]

global platforms
platforms = {
  "arm64" : {
    "abi"    : "arm64-v8a",
    "target" : "aarch64-linux-android",
    "dst"    : "arm64_v8a",
    "api"    : get_sdk_api(),
    "old"    : "aarch64-linux-android"
  },
  "arm" : {
    "abi"    : "armeabi-v7a",
    "target" : "armv7a-linux-androideabi",
    "dst"    : "armv7",
    "api"    : get_sdk_api(),
    "old"    : "arm-linux-android"
  },
  "x86_64" : {
    "arch"   : "x86_64",
    "target" : "x86_64-linux-android",
    "dst"    : "x86_64",
    "api"    : get_sdk_api(),
    "old"    : "x86_64-linux-android"
  },
  "x86" : {
    "arch"   : "x86",
    "target" : "i686-linux-android",
    "dst"    : "x86",
    "api"    : get_sdk_api(),
    "old"    : "i686-linux-android"
  }
}

# todo: check arm host!
global host

if ("linux" == base.host_platform()):
  host = {
    "name" : "linux",
    "arch" : "linux-x86_64"
  }
else:
  host = {
    "name" : "darwin",
    "arch" : "darwin-x86_64"
  }

def get_options_dict_as_array(opts):
  value = []
  for key in opts:
    value.append(key + "=" + opts[key])
  return value

def get_options_array_as_string(opts):
  return " ".join(opts)

def ndk_dir():
  return base.get_env("ANDROID_NDK_ROOT")

def sdk_dir():
  ndk_path = ndk_dir()
  if (-1 != ndk_path.find("/ndk/")):
    return ndk_path + "/../.."
  return ndk_path + "/.."

def toolchain_dir():
  return ndk_dir() + "/toolchains/llvm/prebuilt/" + host["arch"]

def prepare_platform(arch, cpp_standard=11):
  target = platforms[arch]["target"]
  api = platforms[arch]["api"]

  ndk_directory = ndk_dir()
  toolchain = toolchain_dir()

  base.set_env("TARGET", target)
  base.set_env("TOOLCHAIN", toolchain)
  base.set_env("NDK_STANDARD_ROOT", toolchain)
  base.set_env("ANDROIDVER", api)
  base.set_env("ANDROID_API", api)

  base.set_env("AR", toolchain + "/bin/llvm-ar")
  base.set_env("AS", toolchain + "/bin/llvm-as")
  base.set_env("LD", toolchain + "/bin/ld")
  base.set_env("RANLIB", toolchain + "/bin/llvm-ranlib")
  base.set_env("STRIP", toolchain + "/bin/llvm-strip")

  base.set_env("CC", target + api + "-clang")
  base.set_env("CXX", target + api + "-clang++")

  ld_flags = "-Wl,--gc-sections,-rpath-link=" + toolchain + "/sysroot/usr/lib/"
  if (23 > get_android_ndk_version_major()):
    ld_flags += (" -L" + toolchain + "/" + platforms[arch]["old"] + "/lib")
    ld_flags += (" -L" + toolchain + "/sysroot/usr/lib/" + platforms[arch]["old"] + "/" + api)

  base.set_env("LDFLAGS", ld_flags)
  base.set_env("PATH", toolchain + "/bin" + os.pathsep + base.get_env("PATH"))

  cflags = [
    "-Os",
    "-ffunction-sections",
    "-fdata-sections",
    "-fvisibility=hidden",

    "-Wno-unused-function",

    "-fPIC",

    "-I" + toolchain + "/sysroot/usr/include",

    "-D__ANDROID_API__=" + api,
    "-DANDROID"
  ]

  cflags_string = " ".join(cflags)
  cppflags_string = cflags_string
  
  if (cpp_standard >= 11):
    cppflags_string += " -std=c++11"

  base.set_env("CFLAGS", cflags_string)
  base.set_env("CXXFLAGS", cppflags_string)
  base.set_env("CPPPLAGS", cflags_string)
  return

def extend_cflags(params):
  base.set_env("CFLAGS", base.get_env("CFLAGS") + " " + params)
  base.set_env("CPPFLAGS", base.get_env("CFLAGS"))
  return

def extend_cxxflags(params):
  base.set_env("CXXFLAGS", base.get_env("CXXFLAGS") + " " + params)
  return

def extend_ldflags(params):
  base.set_env("LDFLAGS", base.get_env("LDFLAGS") + " " + params)
  return
