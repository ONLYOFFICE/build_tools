#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def clean():
  if base.is_dir("boost_1_58_0"):
    base.delete_dir_with_access_error("boost_1_58_0");
    base.delete_dir("boost_1_58_0")
  if base.is_dir("build"):
    base.delete_dir("build")
  return

def correct_install_includes_win(base_dir, platform):
  build_dir = base_dir + "/build/" + platform + "/include"
  if base.is_dir(build_dir + "/boost-1_58") and base.is_dir(build_dir + "/boost-1_58/boost"):
    base.copy_dir(build_dir + "/boost-1_58/boost", build_dir + "/boost")
    base.delete_dir(build_dir + "/boost-1_58")
  return

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

  base.common_check_version("boost", "2", clean)

  if not base.is_dir("boost_1_58_0"):
    base.cmd("git", ["clone", "--recursive", "--depth=1", "https://github.com/boostorg/boost.git", "boost_1_58_0", "-b" "boost-1.58.0"])

  os.chdir("boost_1_58_0")

  # build
  if ("windows" == base.host_platform()):
    win_toolset = "msvc-14.0"
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("../build/win_64"):      
      base.cmd("bootstrap.bat")
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["--prefix=./../build/win_64", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "address-model=64", "install"])      
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("../build/win_32"):
      base.cmd("bootstrap.bat")
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("bjam.exe", ["--prefix=./../build/win_32", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "install"])
    correct_install_includes_win(base_dir, "win_64")
    correct_install_includes_win(base_dir, "win_32")    

  if (-1 != config.option("platform").find("linux")) and not base.is_dir("../build/linux_64"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.cmd("./b2", ["headers"])
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["--prefix=./../build/linux_64", "link=static", "cxxflags=-fPIC", "install"])    
    # TODO: support x86

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("../build/mac_64"):
    base.replaceInFile("./tools/build/src/tools/darwin.jam", "flags darwin.compile.c++ OPTIONS $(condition) : -fcoalesce-templates ;", "#flags darwin.compile.c++ OPTIONS $(condition) : -fcoalesce-templates ;")
    base.replaceInFile("./tools/build/src/tools/darwin.py", "toolset.flags ('darwin.compile.c++', 'OPTIONS', None, ['-fcoalesce-templates'])", "#toolset.flags ('darwin.compile.c++', 'OPTIONS', None, ['-fcoalesce-templates'])")
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.cmd("./b2", ["headers"])
    base.cmd("./b2", ["--clean"])
    base.cmd("./bjam", ["--prefix=./../build/mac_64", "link=static", "install"])

  if (-1 != config.option("platform").find("ios")) and not base.is_dir("../build/ios"):
    os.chdir("../")
    base.bash("./boost_ios")

  os.chdir(old_cur)
  return

