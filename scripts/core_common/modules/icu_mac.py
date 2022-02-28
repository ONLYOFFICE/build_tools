#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

def change_icu_defs(current_dir, arch):
  icudef_file = current_dir + "/icudefs.mk"
  icudef_file_old = current_dir + "/icudefs.mk.back"

  param = "-arch x86_64"
  if arch == "arm64":
    param = "-arch arm64 -isysroot " + base.find_mac_sdk()

  param += " -mmacosx-version-min=10.12"

  base.copy_file(icudef_file, icudef_file_old)

  base.replaceInFile(icudef_file, "CFLAGS = ", "CFLAGS = " + param + " ")
  base.replaceInFile(icudef_file, "CXXFLAGS = ", "CXXFLAGS = " + param + " ")
  base.replaceInFile(icudef_file, "RPATHLDFLAGS =", "RPATHLDFLAGS2 =")
  base.replaceInFile(icudef_file, "LDFLAGS = ", "LDFLAGS = " + param + " ")
  base.replaceInFile(icudef_file, "RPATHLDFLAGS2 =", "RPATHLDFLAGS =")

  return

def restore_icu_defs(current_dir):
  icudef_file = current_dir + "/icudefs.mk"
  icudef_file_old = current_dir + "/icudefs.mk.back"

  base.delete_file(icudef_file)
  base.copy_file(icudef_file_old, icudef_file)
  base.delete_file(icudef_file_old)
  return

icu_major = "58"
icu_minor = "2"

current_dir_old = os.getcwd()
current_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu"

os.chdir(current_dir)

if not base.is_dir(current_dir + "/mac_cross_64"):
  base.create_dir(current_dir + "/mac_cross_64")
  os.chdir(current_dir + "/mac_cross_64")

  base.cmd("../icu/source/runConfigureICU", ["MacOSX",
    "--prefix=" + current_dir + "/mac_cross_64", "CFLAGS=-Os CXXFLAGS=--std=c++11"])

  change_icu_defs(current_dir + "/mac_cross_64", "x86_64")

  base.cmd("make", ["-j4"])
  base.cmd("make", ["install"], True)

  restore_icu_defs(current_dir + "/mac_cross_64")

  os.chdir(current_dir)

os.chdir(current_dir + "/icu/source")

base.cmd("./configure", ["--prefix=" + current_dir + "/mac_arm_64", 
  "--with-cross-build=" + current_dir + "/mac_cross_64", "VERBOSE=1"])

change_icu_defs(current_dir + "/icu/source", "arm64")

base.cmd("make", ["-j4"])
base.cmd("make", ["install"])

restore_icu_defs(current_dir + "/icu/source")

os.chdir(current_dir)

if base.is_dir(current_dir + "/mac_64"):
  base.delete_dir(current_dir + "/mac_64")

if base.is_dir(current_dir + "/mac_arm64"):
  base.delete_dir(current_dir + "/mac_arm64")

base.create_dir(current_dir + "/mac_64")
base.create_dir(current_dir + "/mac_64/build")

base.create_dir(current_dir + "/mac_arm64")
base.create_dir(current_dir + "/mac_arm64/build")

base.copy_dir(current_dir + "/mac_cross_64/include", current_dir + "/mac_64/build/include")
base.copy_file(current_dir + "/mac_cross_64/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_cross_64/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/libicuuc." + icu_major + ".dylib")

base.copy_dir(current_dir + "/mac_arm_64/include", current_dir + "/mac_arm64/build/include")
base.copy_file(current_dir + "/mac_arm_64/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_arm_64/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/libicuuc." + icu_major + ".dylib")

base.delete_dir(current_dir + "/mac_cross_64")
base.delete_dir(current_dir + "/mac_arm_64")

os.chdir(current_dir_old)
