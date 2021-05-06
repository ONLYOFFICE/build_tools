#!/usr/bin/env python

import config
import base
import os
import re

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  branding = config.branding()

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    isWindowsXP = False if (-1 == native_platform.find("_xp")) else True
    platform = native_platform[0:-3] if isWindowsXP else native_platform

    if (0 == platform.find("mac")):
      macos_dir = git_dir + "/desktop-apps/macos"
      update_dir = macos_dir + "/build/update"
      version_zip = re.sub(r"\.(\d+)$", "", base.get_env("PRODUCT_VERSION"))
      macos_zip = macos_dir + "/build/ONLYOFFICE-" + version_zip + ".zip"

      base.cmd_in_dir(macos_dir, "bundler", ["exec", "fastlane", "release", "skip_git_bump:true"])

      base.delete_dir(update_dir)
      base.delete_dir(os.path.expanduser("~/Library/Caches/Sparkle_generate_appcast"))
      base.create_dir(update_dir)
      base.copy_dir_content(base.get_env("UPDATE_STORAGE"), update_dir, ".zip")
      base.copy_file(macos_zip, update_dir)
      base.cmd(macos_dir + "/Vendor/Sparkle/bin/generate_appcast", [update_dir])
      base.cmd_in_dir(update_dir, "find", [".", "-type", "f", "-name", "*.zip",
        "-not", "-name", "*-" + version_zip + ".zip", "-delete"])

  return
