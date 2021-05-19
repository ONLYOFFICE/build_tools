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
      version_zip = re.sub(r"\.0$", "", base.get_env("PRODUCT_VERSION"))
      macos_zip = macos_dir + "/build/ONLYOFFICE-" + version_zip + ".zip"
      changes_dir = macos_dir + "/ONLYOFFICE/update/updates/ONLYOFFICE/changes/" + version_zip

      base.cmd_in_dir(macos_dir, "bundler", ["exec", "fastlane", "release", "skip_git_bump:true"])

      base.delete_dir(update_dir)
      base.delete_dir(os.path.expanduser("~/Library/Caches/Sparkle_generate_appcast"))
      base.create_dir(update_dir)
      base.copy_dir_content(base.get_env("UPDATE_STORAGE"), update_dir, ".zip")
      base.copy_file(macos_zip, update_dir)
      for file in os.listdir(update_dir):
        if file.endswith(".zip"):
          base.copy_file(changes_dir + "/ReleaseNotes.html",
            update_dir + "/" + os.path.splitext(file)[0] + ".html")
          base.copy_file(changes_dir + "/ReleaseNotesRU.html",
            update_dir + "/" + os.path.splitext(file)[0] + ".ru.html")
      base.cmd(macos_dir + "/Vendor/Sparkle/bin/generate_appcast", [update_dir])
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink>.+/mac/)(?:.+-)([0-9.]+)(\.html</sparkle:releaseNotesLink>)",
        "\\1updates/onlyoffice/changes/\\2/ReleaseNotes\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink xml:lang=\"ru\">)(?:.+-[0-9.]+\.ru)(\.html</sparkle:releaseNotesLink>)",
        "\\1ReleaseNotesRU\\2")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(url=\".+/mac/)(ONLYOFFICE.+\.(zip|delta)\")", "\\1updates/onlyoffice/\\2")
      for file in os.listdir(update_dir):
        if -1 == file.find(version_zip) and (file.endswith(".zip") or file.endswith(".html")):
          base.delete_dir(update_dir + "/" + file)

  return
