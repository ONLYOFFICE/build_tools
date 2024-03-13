#!/usr/bin/env python

import config
import base
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/..")
import sources
import qmake

# make solution
def make():
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    print("------------------------------------------")
    print("BUILD_PLATFORM: " + platform)
    print("------------------------------------------")

    projects = sources.get_projects(platform)

    for pro in projects:
      pro_file = os.path.abspath("../" + pro)
      qmake.make(platform, pro_file)
      if config.check_option("platform", "ios") and config.check_option("config", "bundle_xcframeworks"):
        qmake.make(platform, pro_file, "xcframework_platform_ios_simulator")

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
  return
