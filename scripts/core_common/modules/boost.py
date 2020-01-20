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
  #url = "https://downloads.sourceforge.net/project/boost/boost/1.58.0/boost_1_58_0.7z"  
  #if not base.is_file("boost_1_58_0.7z"):
  #  base.download("https://downloads.sourceforge.net/project/boost/boost/1.58.0/boost_1_58_0.7z", "boost_1_58_0.7z")
  #if not base.is_dir("boost_1_58_0"):
  #  base.extract("boost_1_58_0.7z", "./")

  if not base.is_dir("boost_1_58_0"):
    base.cmd("git", ["clone", "--recursive", "--depth=1", "https://github.com/boostorg/boost.git", "boost_1_58_0", "-b" "boost-1.58.0"])

  os.chdir("boost_1_58_0")

  # build
  if ("windows" == base.host_platform()):
    win_toolset = "msvc-14.0"
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("build/win_64/static"):      
      base.cmd("bootstrap.bat")
      base.create_dir("build/win_64")
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["--prefix=./../build/win_64", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "address-model=64", "install"])
      base.create_dir("build/win_64/static")
      base.copy_files("stage/lib/*", "build/win_64/static/")
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("build/win_32/static"):
      base.cmd("bootstrap.bat")
      base.create_dir("build/win_32")
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["--prefix=./../build/win_32", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "install"])
      base.create_dir("build/win_32/static")
      base.copy_files("stage/lib/*", "build/win_32/static/")

  if (-1 != config.option("platform").find("linux")) and not base.is_dir("build/linux_64/static"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.create_dir("build/linux_64")
    base.cmd("./b2", ["headers"])
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["--prefix=./../build/linux_64", "link=static", "cxxflags=-fPIC", "install"])
    base.create_dir("build/linux_64/static")
    base.copy_files("stage/lib/*", "build/linux_64/static/")
    # TODO: support x86

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("build/mac_64/static"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.create_dir("build/mac_64")
    base.cmd("./b2", ["headers"])
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["--prefix=./../build/mac_64", "link=static", "install"])
    base.create_dir("build/mac_64/static")
    base.copy_files("stage/lib/*", "build/mac_64/static/")

  if (-1 != config.option("platform").find("ios")) and not base.is_dir("build/ios/static"):
    os.chdir("../")
    base.bash("./boost_ios")

  # copy header-only
  os.chdir(base_dir)
  src_dir = "boost_1_58_0/libs"
  dst_dir = "boost_1_58_0/boost"
  for library in glob.glob(src_dir + "/*"):
    library_name = os.path.basename(library)
    if base.is_dir(library) and base.is_dir(library + "/include/boost") and not base.is_dir(dst_dir + "/" + library_name) and not base.is_dir(library + "/src"):
      base.copy_files(library + "/include/boost/*", dst_dir, False)

  os.chdir(old_cur)
  return

