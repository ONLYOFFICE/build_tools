#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import platform

def clean():
  if base.is_dir("build"):
    base.delete_dir("build")
  return

def make():

  print("[fetch & build]: googletest")

  if (-1 != config.option("platform").find("android") or -1 != config.option("platform").find("ios")):
    # TODO
    return

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/googletest"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  if not base.is_dir("googletest"):
    base.cmd("git", ["clone", "https://github.com/google/googletest.git", "-b", "v1.13.0"])

  os.chdir(base_dir + "/googletest")

  if ("windows" == base.host_platform()):
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("./build/win_64"):
      # TODO: check
      base.create_dir("./build/win_64")
      os.chdir("./build/win_64")
      base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF"])
      base.cmd("make")
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("./build/win_32"):
      # TODO: check
      base.create_dir("./build/win_32")
      os.chdir("./build/win_32")
      base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF"])
      base.cmd("make")
    # xp ----------------------------------------------------------------------------------------------------
    os.chdir(base_dir + "/googletest")
    if (-1 != config.option("platform").find("win_64_xp")) and not base.is_dir("./build/win_64_xp"):
      # TODO: check
      base.create_dir("./build/win_64_xp")
      os.chdir("./build/win_64_xp")
      base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF"])
      base.cmd("make")
    if (-1 != config.option("platform").find("win_32_xp")) and not base.is_dir("./build/win_32_xp"):
      # TODO: check
      base.create_dir("./build/win_32_xp")
      os.chdir("./build/win_32_xp")
      base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF"])
      base.cmd("make")
    os.chdir(old_cur)
    # -------------------------------------------------------------------------------------------------------
    return

  if (-1 != config.option("platform").find("linux")) and not base.is_dir("./build/linux_64"):
    base.create_dir("./build/linux_64")
    os.chdir("./build/linux_64")
    base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF"])
    base.cmd("make")
    # TODO: support x86

  if (-1 != config.option("platform").find("linux_arm64")) and not base.is_dir("../build/linux_arm64"):
    # TODO
    pass

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("./build/mac_64"):
    base.create_dir("./build/mac_64")
    os.chdir("./build/mac_64")
    base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF", "-DCMAKE_OSX_ARCHITECTURES=x86_64"])
    base.cmd("make")
  os.chdir(base_dir + "/googletest")
  if (-1 != config.option("platform").find("mac")) and not base.is_dir("./build/mac_arm64"):
    base.create_dir("./build/mac_arm64")
    os.chdir("./build/mac_arm64")
    base.cmd("cmake ../../", ["-DBUILD_GMOCK=OFF", "-DCMAKE_OSX_ARCHITECTURES=arm64"])
    base.cmd("make")

  os.chdir(old_cur)
  return
