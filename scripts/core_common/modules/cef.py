#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import glob

def clear_module():
  for child in glob.glob("./*"):
    if base.is_dir(child):
      base.delete_dir(child)
  return

def make():
  print("[fetch & build]: cef")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/cef"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  base.check_module_version("2", clear_module)
  platforms = ["win_64", "win_32", "win_64_xp", "win_32_xp", "linux_64", "linux_32", "mac_64", "mac_arm64", "win_arm64"]

  for platform in platforms:
    if not config.check_option("platform", platform):
      continue

    url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/cef/"
    archive_name = "./cef_binary.7z"

    if (-1 != platform.find("_xp")):
      url += "4280/"
      archive_name = "./cef_binary_xp.7z"
    elif (config.check_option("config", "cef_version_107")):
      url += "5304/"
      archive_name = "./cef_binary_107.7z"
    elif ("mac_64" == platform) and (config.check_option("config", "use_v8")):
      url += "5060/"
      archive_name = "./cef_binary_103.7z"
    else:
      url += "5414/"

    url_platform = (url + platform + "/cef_binary.7z")
    archive_name_data = archive_name + ".data"

    if not base.is_dir(platform):
      base.create_dir(platform)

    os.chdir(platform)
    
    data_url = base.get_file_last_modified_url(url_platform)
    old_data_url = base.readFile(archive_name_data)

    build_dir_name = "build"
    if (0 == platform.find("linux")) and (config.check_option("config", "cef_version_107")):
      build_dir_name = "build_107"
    if ("mac_64" == platform) and (config.check_option("config", "use_v8")):
      build_dir_name = "build_103"

    if (data_url != old_data_url):
      if base.is_file(archive_name):
        base.delete_file(archive_name)
      if base.is_dir(build_dir_name):
        base.delete_dir(build_dir_name)

    if base.is_dir(build_dir_name):
      os.chdir(base_dir)
      continue

    # download
    if not base.is_file(archive_name):
      base.download(url_platform, archive_name)

    # extract
    base.extract(archive_name, "./")

    base.delete_file(archive_name_data)
    base.writeFile(archive_name_data, data_url)

    base.create_dir("./" + build_dir_name)

    # deploy
    if (0 == platform.find("mac")):
      base.cmd("mv", ["Chromium Embedded Framework.framework", build_dir_name + "/Chromium Embedded Framework.framework"])
      base.delete_dir("./Chromium Embedded Framework.framework")
    else:
      base.copy_files("cef_binary/Release/*", build_dir_name + "/")
      base.copy_files("cef_binary/Resources/*", build_dir_name + "/")
      if (0 == platform.find("linux")):
        base.cmd("chmod", ["a+xr", build_dir_name + "/locales"])
      base.delete_dir("./cef_binary")

    os.chdir(base_dir)

  os.chdir(old_cur)
  return
