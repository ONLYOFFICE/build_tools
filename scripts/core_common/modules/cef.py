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

  platforms = ["win_64", "win_32", "win_64_xp", "win_32_xp", "linux_64", "linux_32", "mac_64", "mac_arm64"]

  url = "http://d2ettrnqo7v976.cloudfront.net/cef/4280/"

  for platform in platforms:
    if not config.check_option("platform", platform):
      continue

    url_platform = (url + platform + "/cef_binary.7z")

    if not base.is_dir(platform):
      base.create_dir(platform)

    os.chdir(platform)

    data_url = base.get_file_last_modified_url(url_platform)
    old_data_url = base.readFile("./cef_binary.7z.data")

    if (data_url != old_data_url):
      if base.is_file("./cef_binary.7z"):
        base.delete_file("./cef_binary.7z")
      if base.is_dir("build"):
        base.delete_dir("build")

    if base.is_dir("build"):
      os.chdir(base_dir)
      continue

    # download
    if not base.is_file("./cef_binary.7z"):
      base.download(url_platform, "./cef_binary.7z")

    # extract
    base.extract("./cef_binary.7z", "./")

    base.delete_file("./cef_binary.7z.data")
    base.writeFile("./cef_binary.7z.data", data_url)

    base.create_dir("./build")

    # deploy
    if (0 != platform.find("mac")):
      base.copy_files("cef_binary/Release/*", "build/")
      base.copy_files("cef_binary/Resources/*", "build/")

    if (0 == platform.find("linux")):
      base.cmd("chmod", ["a+xr", "build/locales"])

    if (0 == platform.find("mac")):
      base.cmd("mv", ["Chromium Embedded Framework.framework", "build/Chromium Embedded Framework.framework"])

    os.chdir(base_dir)

  os.chdir(old_cur)
  return
