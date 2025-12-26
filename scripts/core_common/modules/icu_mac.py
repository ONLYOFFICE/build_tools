#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

def change_icu_defs(arch):
  old_env = dict(os.environ)

  param = "-arch x86_64"
  if arch == "arm64":
    param = "-arch arm64"

  param += " -isysroot " + base.find_mac_sdk()
  param += " -mmacosx-version-min=10.12"

  os.environ["CFLAGS"] = param
  os.environ["CXXFLAGS"] = param + " --std=c++11"
  os.environ["LDFLAGS"] = param

  return old_env

def restore_icu_defs(old_env):
  os.environ.clear()
  os.environ.update(old_env)
  return

icu_major = "74"
icu_minor = "2"

current_dir_old = os.getcwd()
current_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu"

os.chdir(current_dir)

if not base.is_dir(current_dir + "/mac_cross_64"):
  base.create_dir(current_dir + "/mac_cross_64")
  os.chdir(current_dir + "/mac_cross_64")

  old_env = change_icu_defs("x86_64")

  base.cmd("../icu/source/runConfigureICU", ["MacOSX",
    "--prefix=" + current_dir + "/mac_64_install", "--enable-static"])

  base.cmd("make", ["-j4"])
  base.cmd("make", ["install"], True)

  restore_icu_defs(old_env)

  os.chdir(current_dir)

os.chdir(current_dir + "/icu/source")

old_env = change_icu_defs("arm64")

addon = []
if not base.is_os_arm():
  addon = ["--host=aarch64-apple-darwin"]

base.cmd("./configure", ["--prefix=" + current_dir + "/mac_arm64_install",
  "--with-cross-build=" + current_dir + "/mac_cross_64", "--enable-static", "VERBOSE=1"] + addon)

base.cmd("make", ["-j4"])
base.cmd("make", ["install"])

restore_icu_defs(old_env)

os.chdir(current_dir)

if base.is_dir(current_dir + "/mac_64"):
  base.delete_dir(current_dir + "/mac_64")

if base.is_dir(current_dir + "/mac_arm64"):
  base.delete_dir(current_dir + "/mac_arm64")

base.create_dir(current_dir + "/mac_64")
base.create_dir(current_dir + "/mac_64/build")

base.create_dir(current_dir + "/mac_arm64")
base.create_dir(current_dir + "/mac_arm64/build")

base.copy_dir(current_dir + "/mac_64_install/include", current_dir + "/mac_64/build/include")
# copy shared libs
base.copy_file(current_dir + "/mac_64_install/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_64_install/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/libicuuc." + icu_major + ".dylib")
# copy static libs
base.copy_file(current_dir + "/mac_64_install/lib/libicudata.a", current_dir + "/mac_64/build")
base.copy_file(current_dir + "/mac_64_install/lib/libicui18n.a", current_dir + "/mac_64/build")
base.copy_file(current_dir + "/mac_64_install/lib/libicuuc.a", current_dir + "/mac_64/build")

base.copy_dir(current_dir + "/mac_arm64_install/include", current_dir + "/mac_arm64/build/include")
# copy shared libs
base.copy_file(current_dir + "/mac_arm64_install/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_arm64_install/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/libicuuc." + icu_major + ".dylib")
# copy static libs
base.copy_file(current_dir + "/mac_arm64_install/lib/libicudata.a", current_dir + "/mac_arm64/build")
base.copy_file(current_dir + "/mac_arm64_install/lib/libicui18n.a", current_dir + "/mac_arm64/build")
base.copy_file(current_dir + "/mac_arm64_install/lib/libicuuc.a", current_dir + "/mac_arm64/build")

base.delete_dir(current_dir + "/mac_cross_64")
base.delete_dir(current_dir + "/mac_64_install")
base.delete_dir(current_dir + "/mac_arm64_install")

os.chdir(current_dir_old)
