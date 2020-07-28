#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

platforms = {
  "arm64_v8a" : {
    "name" : "arm64-v8a",
    "toolset" : "arm64v8a", 
    "clang_triple" : "aarch64-linux-android21", 
    "tool_triple" : "aarch64-linux-android", 
    "abi" : "aapcs",
    "arch" : "arm",
    "address_model" : "64",
    "compiler_flags" : "",
    "linker_flags" : ""
  },
  "armv7" : {
    "name" : "armeabi-v7a",
    "toolset" : "armeabiv7a", 
    "clang_triple" : "armv7a-linux-androideabi16", 
    "tool_triple" : "arm-linux-androideabi", 
    "abi" : "aapcs",
    "arch" : "arm",
    "address_model" : "32",
    "compiler_flags" : "-march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp",
    "linker_flags" : "-Wl,--fix-cortex-a8"
  },
  "x86" : {
    "name" : "x86",
    "toolset" : "x86", 
    "clang_triple" : "i686-linux-android16", 
    "tool_triple" : "i686-linux-android", 
    "abi" : "sysv",
    "arch" : "x86",
    "address_model" : "32",
    "compiler_flags" : "",
    "linker_flags" : ""
  },
  "x86_64" : {
    "name" : "x86_64",
    "toolset" : "x8664", 
    "clang_triple" : "x86_64-linux-android21", 
    "tool_triple" : "x86_64-linux-android", 
    "abi" : "sysv",
    "arch" : "x86",
    "address_model" : "64",
    "compiler_flags" : "",
    "linker_flags" : ""
  }
}

base_dir = base.get_script_dir()

def make(platform):
  tmp_build_dir = base_dir + "/core_common/modules/boost"
  if (base.is_dir(tmp_build_dir)):
    base.delete_dir(tmp_build_dir)
  base.copy_dir(base_dir + "/../tools/android/boost", tmp_build_dir)

  current_platform = platforms[platform]

  if (base.host_platform() == "mac"):
    source = "prebuilt/linux-x86_64"
    dest = "prebuilt/darwin-x86_64"
    base.replaceInFile(tmp_build_dir + "/user-config.jam", source, dest)
    base.replaceInFile(tmp_build_dir + "/bin/hide/as", source, dest)
    base.replaceInFile(tmp_build_dir + "/bin/hide/strip", source, dest)
    base.replaceInFile(tmp_build_dir + "/bin/ar", source, dest)
    base.replaceInFile(tmp_build_dir + "/bin/clang++", source, dest)
    base.replaceInFile(tmp_build_dir + "/bin/ranlib", source, dest)

  build_dir_tmp = tmp_build_dir + "/tmp"

  base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex", "--prefix=../build/android_" + platform])
  base.cmd("./b2", ["headers"])
  base.cmd("./b2", ["--clean"])

  old_path = base.get_env("PATH")
  base.set_env("PATH", tmp_build_dir + "/bin:" + old_path)
  base.set_env("NDK_DIR", base.get_env("ANDROID_NDK_ROOT"))

  base.set_env("BFA_CLANG_TRIPLE_FOR_ABI", current_platform["clang_triple"])
  base.set_env("BFA_TOOL_TRIPLE_FOR_ABI", current_platform["tool_triple"])
  base.set_env("BFA_COMPILER_FLAGS_FOR_ABI", current_platform["compiler_flags"])
  base.set_env("BFA_LINKER_FLAGS_FOR_ABI", current_platform["linker_flags"])

  print(current_platform)
  base.cmd("./b2", ["-q", "-j4",
    "toolset=clang-" + current_platform["toolset"],
    "binary-format=elf",
    "address-model=" + current_platform["address_model"],
    "architecture=" + current_platform["arch"],
    "abi=" + current_platform["abi"],
    "link=static",
    "threading=multi",
    "target-os=android",
    "--user-config=" + tmp_build_dir + "/user-config.jam",
    "--ignore-site-config",
    "--layout=system",
    "install"], True)

  base.set_env("PATH", old_path)
  base.delete_dir(tmp_build_dir)
  return
