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

  url = "http://d2ettrnqo7v976.cloudfront.net/cef/3770/"

  for platform in platforms:
    if not config.check_option("platform", platform):
      if (0 != platform.find("winxp")):
        continue
      if ("winxp_64" != platform) and not config.check_option("platform", "win_64_xp"):
        continue
      if ("winxp_32" != platform) and not config.check_option("platform", "win_32_xp"):
        continue

    if (0 == platform.find("mac")):
      url += "mac"
    else:
      url += platform

    url += "/cef_binary.7z"

    if not base.is_dir(platform):
      base.create_dir(platform)

    os.chdir(platform)

    data_url = base.get_file_last_modified_url(url)
    old_data_url = base.readFile("./cef_binary.7z.data")

    if (old_cur != old_data_url):
      if base.is_file("./cef_binary.7z"):
        base.delete_file("./cef_binary.7z")
      if base.is_dir("build"):
        base.delete_dir("build")

    if base.is_dir("build"):
      continue

    # download
    if not base.is_file("./cef_binary.7z"):
      base.download(url, "./cef_binary.7z")

    # extract
    base.extract("./cef_binary.7z", "./")

    base.create_dir("./build")

    # deploy
    if ("mac_64" != platform):
      base.copy_files("cef_binary/Release/*", "build/")
      base.copy_files("cef_binary/Resources/*", "build/")

    if (0 == platform.find("linux")):
      base.cmd("chmod", ["a+xr", "build/locales"])

    if ("mac_64" == platform):
      base.cmd("mv", ["cef_binary", "build/Chromium Embedded Framework.framework"])

    os.chdir(base_dir)

  os.chdir(old_cur)
  return
