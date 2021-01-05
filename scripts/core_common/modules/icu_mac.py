#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

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
  base.cmd("make", ["-j4"])
  base.cmd("make", ["install"], True)
  os.chdir(current_dir)

os.chdir(current_dir + "/icu/source")
clang_params = "-target arm64-apple-macos10.15 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX11.1.sdk"
base.cmd("./configure", ["--prefix=" + current_dir + "/mac_arm_64", 
  "--with-cross-build=" + current_dir + "/mac_cross_64", "VERBOSE=1"])

icudef_file = current_dir + "/icu/source/icudefs.mk"
base.replaceInFile(icudef_file, "CFLAGS = ", "CFLAGS = " + clang_params + " ")
base.replaceInFile(icudef_file, "CXXFLAGS = ", "CXXFLAGS = " + clang_params + " ")
base.replaceInFile(icudef_file, "RPATHLDFLAGS =", "RPATHLDFLAGS2 =")
base.replaceInFile(icudef_file, "LDFLAGS = ", "LDFLAGS = " + clang_params + " ")
base.replaceInFile(icudef_file, "RPATHLDFLAGS2 =", "RPATHLDFLAGS =")

base.cmd("make", ["-j4"])
base.cmd("make", ["install"])

os.chdir(current_dir)

if base.is_dir(current_dir + "/mac_64"):
  base.delete_dir(current_dir + "/mac_64")

if base.is_dir(current_dir + "/mac_arm64"):
  base.delete_dir(current_dir + "/mac_arm64")

base.create_dir(current_dir + "/mac_64")
base.create_dir(current_dir + "/mac_64/build")
base.create_dir(current_dir + "/mac_64/build/lib")

base.create_dir(current_dir + "/mac_arm64")
base.create_dir(current_dir + "/mac_arm64/build")
base.create_dir(current_dir + "/mac_arm64/build/lib")

base.copy_dir(current_dir + "/mac_cross_64/include", current_dir + "/mac_64/build/include")
base.copy_file(current_dir + "/mac_cross_64/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/lib/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_cross_64/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_64/build/lib/libicuuc." + icu_major + ".dylib")

base.copy_dir(current_dir + "/mac_arm_64/include", current_dir + "/mac_arm64/build/include")
base.copy_file(current_dir + "/mac_arm_64/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/lib/libicudata." + icu_major + ".dylib")
base.copy_file(current_dir + "/mac_arm_64/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", current_dir + "/mac_arm64/build/lib/libicuuc." + icu_major + ".dylib")

base.delete_dir(current_dir + "/mac_cross_64")
base.delete_dir(current_dir + "/mac_arm_64")

os.chdir(current_dir_old)
