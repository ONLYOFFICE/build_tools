#!/usr/bin/env python

import config
import base
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/..")
import sln
import qmake

# make solution
def make(solution=""):
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    print("------------------------------------------")
    print("BUILD_PLATFORM: " + platform)
    print("------------------------------------------")

    if ("" == solution):
      solution = "./sln.json"
    projects = sln.get_projects(solution, platform)

    for pro in projects:
      qmake_main_addon = ""
      if (0 == platform.find("android")) and (-1 != pro.find("X2tConverter.pro")):
        if config.check_option("config", "debug") and not config.check_option("config", "disable_x2t_debug_strip"):
          print("[WARNING:] temporary enable strip for x2t library in debug")
          qmake_main_addon += "build_strip_debug"

      qmake.make(platform, pro, qmake_main_addon)
      if config.check_option("platform", "ios") and config.check_option("config", "bundle_xcframeworks"):
        qmake.make(platform, pro, "xcframework_platform_ios_simulator")

  if config.check_option("module", "builder") and base.is_windows() and "onlyoffice" == config.branding():
    # check replace
    new_replace_path = base.correctPathForBuilder(os.getcwd() + "/../core/DesktopEditor/doctrenderer/docbuilder.com/src/docbuilder.h")
    if ("2019" == config.option("vs-version")):
      base.make_sln_project("../core/DesktopEditor/doctrenderer/docbuilder.com/src", "docbuilder.com_2019.sln")
      if (True):
        new_path_net = base.correctPathForBuilder(os.getcwd() + "/../core/DesktopEditor/doctrenderer/docbuilder.net/src/docbuilder.net.cpp")
        base.make_sln_project("../core/DesktopEditor/doctrenderer/docbuilder.net/src", "docbuilder.net.sln")
        base.restorePathForBuilder(new_path_net)
    else:
      base.make_sln_project("../core/DesktopEditor/doctrenderer/docbuilder.com/src", "docbuilder.com.sln")
    base.restorePathForBuilder(new_replace_path)

  # build Java docbuilder wrapper
  if config.check_option("module", "builder") and "onlyoffice" == config.branding():
    for platform in platforms:
      if not platform in config.platforms:
        continue

      # build JNI library
      qmake.make(platform, base.get_script_dir() + "/../../core/DesktopEditor/doctrenderer/docbuilder.java/src/jni/docbuilder_jni.pro", "", True)
      # build Java code to JAR
      base.cmd_in_dir(base.get_script_dir() + "/../../core/DesktopEditor/doctrenderer/docbuilder.java", "python", ["make.py"])

  return
