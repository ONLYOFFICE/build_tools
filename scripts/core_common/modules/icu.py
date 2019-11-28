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
    for platform in ["win_64", "win_32"]:
      if not config.check_option("platform", platform):
        continue
      if not base.is_dir(platform + "/build"):
        base.create_dir(platform)
        base.call_vcvarsall("x64" if ("win_64" == platform) else "x86")
        base.cmd("MSBuild.exe", ["icu/source/allinone/allinone.sln", "/p:Configuration=Release", "/p:PlatformToolset=v140", "/p:Platform=\"" + ("X64" if ("win_64" == platform) else "Win32") + "\""])
        bin_dir = "icu/bin64/" if ("win_64" == platform) else "icu/bin/"
        base.create_dir(platform + "/build")
        base.copy_file(bin_dir + "icudt" + icu_major + ".dll", platform + "/build/")
        base.copy_file(bin_dir + "icuuc" + icu_major + ".dll", platform + "/build/")
        base.copy_file(bin_dir + "icudt.lib", platform + "/build/")
        base.copy_file(bin_dir + "icuuc.lib", platform + "/build/")

  platform = ""
  if ("linux" == base.host_platform()):
    platform = "linux_64"
    if not base.is_dir(platform + "/build"):
      base.replaceInFile("./icu/source/i18n/digitlst.cpp", "xlocale", "locale")      

  if ("mac" == base.host_platform()):
    platform = "mac_64"
    if not base.is_dir(platform + "/build"):
      base.replaceInFile("./icu/source/tools/pkgdata/pkgdata.cpp", "cmd, \"%s %s -o %s%s %s %s%s %s %s\",", "cmd, \"%s %s -o %s%s %s %s %s %s %s\",")

  if ("" != platform):
    base.create_dir(platform)
    base.cmd("icu/source/runConfigureICU", [platform])
    old_dest_dir = base.get_env("DESTDIR")
    base.set_env("DESTDIR", platform)
    base.cmd("make", ["install"])
    base.set_env("DESTDIR", old_dest_dir)
    base.create_dir(platform + "/build")
    if ("linux_64" == platform):
      base.copy_file("icu/source/lib/libicudata.so." + icu_major + "." + icu_minor, platform + "/build/libicudata.so." + icu_major)
      base.copy_file("icu/source/lib/libicuuc.so." + icu_major + "." + icu_minor, platform + "/build/libicuuc.so." + icu_major)
    elif ("mac_64" == platform):
      base.copy_file("icu/source/lib/libicudata." + icu_major + "." + icu_minor + ".dylib", platform + "/build/libicudata." + icu_major + ".dylib")
      base.copy_file("icu/source/lib/libicuuc." + icu_major + "." + icu_minor + ".dylib", platform + "/build/libicuuc." + icu_major + ".dylib")
      
  os.chdir(old_cur)
  return
