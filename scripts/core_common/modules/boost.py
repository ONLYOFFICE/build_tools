#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def make():
  print("[fetch & build]: boost")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/boost"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  # download
  url = "https://downloads.sourceforge.net/project/boost/boost/1.58.0/boost_1_58_0.7z"

  if not base.is_file("boost_1_58_0.7z"):
    base.download("https://downloads.sourceforge.net/project/boost/boost/1.58.0/boost_1_58_0.7z", "boost_1_58_0.7z")

  if not base.is_dir("boost_1_58_0"):
    base.extract("boost_1_58_0.7z", "./")

  os.chdir("boost_1_58_0")

  # build
  if ("windows" == base.host_platform()):
    win_toolset = "msvc-14.0"
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("build/win_64/static"):      
      base.cmd("bootstrap.bat")
      base.create_dir("build/win_64")
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "address-model=64"])
      base.create_dir("build/win_64/static")
      base.copy_files("stage/lib/*", "build/win_64/static/")
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("build/win_32/static"):
      base.cmd("bootstrap.bat")
      base.create_dir("build/win_32")
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset])
      base.create_dir("build/win_32/static")
      base.copy_files("stage/lib/*", "build/win_32/static/")

  if (-1 != config.option("platform").find("linux")) and not base.is_dir("build/linux_64/static"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.create_dir("build/linux_64")
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["link=static", "cxxflags=-fPIC"])
    base.create_dir("build/linux_64/static")
    base.copy_files("stage/lib/*", "build/linux_64/static/")
    # TODO: support x86

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("build/mac_64/static"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.create_dir("build/mac_64")
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["link=static"])
    base.create_dir("build/mac_64/static")
    base.copy_files("stage/lib/*", "build/mac_64/static/")

  if (-1 != config.option("platform").find("ios")) and not base.is_dir("build/ios/static"):
    os.chdir("../")
    base.bash("./boost_ios")

  os.chdir(old_cur)
  return

