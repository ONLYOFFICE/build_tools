#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def make():
  print("[fetch & build]: cef")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/cef"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  platforms = ["win_64", "win_32", "winxp_64", "winxp_32", "linux_64", "linux_32", "mac_64"]

  url = "http://d2ettrnqo7v976.cloudfront.net/cef/"

  for platform in platforms:
    if not config.check_option("platform", platform):
      if (0 != platform.find("winxp")):
        continue
      if ("winxp_64" != platform) and not config.check_option("platform", "win_64_xp"):
        continue
      if ("winxp_32" != platform) and not config.check_option("platform", "win_32_xp"):
        continue

    if base.is_dir(platform + "/build"):
      continue

    base.create_dir(platform)
    # download

    url_addon = "3163/" + platform
    if (0 == platform.find("linux")):
      url_addon = "3202/" + platform
    elif (0 == platform.find("mac")):
      url_addon = "3163/mac"

    if not base.is_file(platform + "/cef_binary.7z"):
      base.download(url + url_addon + "/cef_binary.7z", platform + "/cef_binary.7z")

    # extract
    base.extract(platform + "/cef_binary.7z", platform)

    base.create_dir(platform + "/build")

    # deploy
    if ("mac_64" != platform):
      base.copy_files(platform + "/cef_binary/Release/*", platform + "/build/")
      base.copy_files(platform + "/cef_binary/Resources/*", platform + "/build/")

    if (0 == platform.find("linux")):
      base.cmd("chmod", ["a+xr", platform + "/build/locales"])

    if ("mac_64" == platform):
      base.cmd("mv", [platform + "/cef_binary", platform + "/build/Chromium Embedded Framework.framework"])

  os.chdir(old_cur)
  return
