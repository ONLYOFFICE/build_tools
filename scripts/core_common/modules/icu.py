#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def make():
  print("[fetch & build]: icu")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  icu_major = "58"
  icu_minor = "2"

  if not base.is_dir("icu"):
    base.cmd("svn", ["export", "https://github.com/unicode-org/icu/tags/release-" + icu_major + "-" + icu_minor + "/icu4c", "./icu"])

  if ("windows" == base.host_platform()):
    need_platforms = []
    if (-1 != config.option("platform").find("win_64")):
      need_platforms.append("win_64")
    if (-1 != config.option("platform").find("win_32")):
      need_platforms.append("win_32")
    for platform in need_platforms:
      if not config.check_option("platform", platform) and not config.check_option("platform", platform + "_xp"):
        continue
      if not base.is_dir(platform + "/build"):
        base.create_dir(platform)
        base.vcvarsall_start("x64" if ("win_64" == platform) else "x86")
        base.cmd("MSBuild.exe", ["icu/source/allinone/allinone.sln", "/p:Configuration=Release", "/p:PlatformToolset=v140", "/p:Platform=" + ("X64" if ("win_64" == platform) else "Win32")])
        base.vcvarsall_end()
        bin_dir = "icu/bin64/" if ("win_64" == platform) else "icu/bin/"
        lib_dir = "icu/lib64/" if ("win_64" == platform) else "icu/lib/"
        base.create_dir(platform + "/build")
        base.copy_file(bin_dir + "icudt" + icu_major + ".dll", platform + "/build/")
        base.copy_file(bin_dir + "icuuc" + icu_major + ".dll", platform + "/build/")
        base.copy_file(lib_dir + "icudt.lib", platform + "/build/")
        base.copy_file(lib_dir + "icuuc.lib", platform + "/build/")

  platform = ""
  if ("linux" == base.host_platform()):
    platform = "linux_64"
    if not base.is_dir(platform + "/build"):
      base.replaceInFile("./icu/source/i18n/digitlst.cpp", "xlocale", "locale")      

  if ("mac" == base.host_platform()):
    platform = "mac_64"
    if not base.is_dir(platform + "/build"):
      base.replaceInFile("./icu/source/tools/pkgdata/pkgdata.cpp", "cmd, \"%s %s -o %s%s %s %s%s %s %s\",", "cmd, \"%s %s -o %s%s %s %s %s %s %s\",")

  if (-1 != config.option("platform").find("ios")):
    if not base.is_dir("build"):
      base.bash("./icu_ios")
  elif ("" != platform) and not base.is_dir(platform + "/build"):
    base.create_dir(platform)
    os.chdir("icu/source")
    base.cmd("./runConfigureICU", ["Linux" if "linux" == base.host_platform() else "MacOSX"])
    old_env = os.environ.copy()
    base.set_env("DESTDIR", base_dir + "/" + platform)
    base.cmd("make", ["install"])
    os.environ = old_env.copy()
    os.chdir("../..")
    base.create_dir(platform + "/build")
    if ("linux_64" == platform):
      base.copy_file("icu/source/lib/libicudata.so." + icu_major + "." + icu_minor, platform + "/build/libicudata.so." + icu_major)
      base.copy_file("icu/source/lib/libicuuc.so." + icu_major + "." + icu_minor, platform + "/build/libicuuc.so." + icu_major)
    elif ("mac_64" == platform):
      base.copy_file("icu/source/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", platform + "/build/libicudata." + icu_major + ".dylib")
      base.copy_file("icu/source/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", platform + "/build/libicuuc." + icu_major + ".dylib")
      
  os.chdir(old_cur)
  return
