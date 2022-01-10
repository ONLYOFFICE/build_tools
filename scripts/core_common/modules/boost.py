#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import glob
import boost_qt

def move_debug_libs_windows(dir):
  base.create_dir(dir + "/debug")
  for file in glob.glob(dir + "/*"):
    file_name = os.path.basename(file)
    if not base.is_file(file):
      continue
    if (0 != file_name.find("libboost_")):
      continue
    base.copy_file(file, dir + "/debug/" + file_name)
    base.delete_file(file)
  return

def clean():
  if base.is_dir("boost_1_58_0"):
    base.delete_dir_with_access_error("boost_1_58_0");
    base.delete_dir("boost_1_58_0")
  if base.is_dir("boost_1_72_0"):
    base.delete_dir_with_access_error("boost_1_72_0");
    base.delete_dir("boost_1_72_0")
  if base.is_dir("build"):
    base.delete_dir("build")
  return

def correct_install_includes_win(base_dir, platform):
  build_dir = base_dir + "/build/" + platform + "/include"
  if base.is_dir(build_dir + "/boost-1_72") and base.is_dir(build_dir + "/boost-1_72/boost"):
    base.copy_dir(build_dir + "/boost-1_72/boost", build_dir + "/boost")
    base.delete_dir(build_dir + "/boost-1_72")
  return

def clang_correct():
  base.replaceInFile("./tools/build/src/tools/darwin.jam", "flags darwin.compile.c++ OPTIONS $(condition) : -fcoalesce-templates ;", "#flags darwin.compile.c++ OPTIONS $(condition) : -fcoalesce-templates ;")
  base.replaceInFile("./tools/build/src/tools/darwin.py", "toolset.flags ('darwin.compile.c++', 'OPTIONS', None, ['-fcoalesce-templates'])", "#toolset.flags ('darwin.compile.c++', 'OPTIONS', None, ['-fcoalesce-templates'])")
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

  base.common_check_version("boost", "5", clean)

  if not base.is_dir("boost_1_72_0"):
    base.cmd("git", ["clone", "--recursive", "--depth=1", "https://github.com/boostorg/boost.git", "boost_1_72_0", "-b" "boost-1.72.0"])

  os.chdir("boost_1_72_0")

  # build
  if ("windows" == base.host_platform()):
    win_toolset = "msvc-14.0"
    win_boot_arg = "vc14"
    if (config.option("vs-version") == "2019"):
      win_toolset = "msvc-14.2"
      win_boot_arg = "vc142"
    if (-1 != config.option("platform").find("win_64")) and not base.is_dir("../build/win_64"):      
      base.cmd("bootstrap.bat", [win_boot_arg])
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("b2.exe", ["--prefix=./../build/win_64", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "address-model=64", "install"])
    if (-1 != config.option("platform").find("win_32")) and not base.is_dir("../build/win_32"):
      base.cmd("bootstrap.bat", [win_boot_arg])
      base.cmd("b2.exe", ["headers"])
      base.cmd("b2.exe", ["--clean"])
      base.cmd("b2.exe", ["--prefix=./../build/win_32", "link=static", "--with-filesystem", "--with-system", "--with-date_time", "--with-regex", "--toolset=" + win_toolset, "address-model=32", "install"])
    correct_install_includes_win(base_dir, "win_64")
    correct_install_includes_win(base_dir, "win_32")    

  if config.check_option("platform", "linux_64") and not base.is_dir("../build/linux_64"):
    base.cmd("./bootstrap.sh", ["--with-libraries=filesystem,system,date_time,regex"])
    base.cmd("./b2", ["headers"])
    base.cmd("./b2", ["--clean"])
    base.cmd("./b2", ["--prefix=./../build/linux_64", "link=static", "cxxflags=-fPIC", "install"])    
    # TODO: support x86

  if config.check_option("platform", "linux_arm64") and not base.is_dir("../build/linux_arm64"):
    boost_qt.make(os.getcwd(), ["filesystem", "system", "date_time", "regex"], "linux_arm64")
    directory_build = base_dir + "/build/linux_arm64/lib"
    base.delete_file(directory_build + "/libboost_system.a")
    base.delete_file(directory_build + "/libboost_system.so")
    base.copy_files(directory_build + "/linux_arm64/*.a", directory_build)

  if (-1 != config.option("platform").find("ios")) and not base.is_dir("../build/ios"):
    clang_correct()
    os.chdir("../")
    base.bash("./boost_ios")

  if (-1 != config.option("platform").find("android")) and not base.is_dir("../build/android"):
    boost_qt.make(os.getcwd(), ["filesystem", "system", "date_time", "regex"])

  if (-1 != config.option("platform").find("mac")) and not base.is_dir("../build/mac_64"):
    boost_qt.make(os.getcwd(), ["filesystem", "system", "date_time", "regex"], "mac_64")
    directory_build = base_dir + "/build/mac_64/lib"
    base.delete_file(directory_build + "/libboost_system.a")
    base.delete_file(directory_build + "/libboost_system.dylib")
    base.copy_files(directory_build + "/mac_64/*.a", directory_build)

  if (-1 != config.option("platform").find("mac_arm64")) and not base.is_dir("../build/mac_arm64"):
    boost_qt.make(os.getcwd(), ["filesystem", "system", "date_time", "regex"], "mac_arm64")
    directory_build = base_dir + "/build/mac_arm64/lib"
    base.delete_file(directory_build + "/libboost_system.a")
    base.delete_file(directory_build + "/libboost_system.dylib")
    base.copy_files(directory_build + "/mac_arm64/*.a", directory_build)

  os.chdir(old_cur)
  return

