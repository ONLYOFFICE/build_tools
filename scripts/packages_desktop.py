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

      isX86 = True if ("" != base.get_env("_X86")) else False

      target = "release" if not isX86 else "release_x86"
      base.cmd_in_dir(macos_dir, "bundler", ["exec", "fastlane", target, "skip_git_bump:true"])

      package = "ONLYOFFICE" if not isX86 else "ONLYOFFICE-x86"
      app_version = base.run_command("mdls -name kMDItemVersion -raw " +
        macos_dir + "/build/ONLYOFFICE.app")['stdout']
      macos_zip = macos_dir + "/build/" + package + "-" + app_version + ".zip"
      update_storage = base.get_env("ARCHIVES_DIR") + "/" + package + "/_updates"
      changes_dir = macos_dir + "/ONLYOFFICE/update/updates/ONLYOFFICE/changes/" + app_version
      base.delete_dir(update_dir)
      base.delete_dir(os.path.expanduser("~/Library/Caches/Sparkle_generate_appcast"))
      base.create_dir(update_dir)
      base.copy_dir_content(update_storage, update_dir, ".zip")
      base.copy_file(macos_zip, update_dir)
      for file in os.listdir(update_dir):
        if file.endswith(".zip"):
          base.copy_file(changes_dir + "/ReleaseNotes.html",
            update_dir + "/" + os.path.splitext(file)[0] + ".html")
          base.copy_file(changes_dir + "/ReleaseNotesRU.html",
            update_dir + "/" + os.path.splitext(file)[0] + ".ru.html")

      base.cmd(macos_dir + "/Vendor/Sparkle/bin/generate_appcast", [update_dir])

      base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"
      changes_url = base_url + "/updates/onlyoffice/changes"
      update_url = base_url + ("/updates/onlyoffice" if not isX86 else "/x86")

      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink>)(?:.+ONLYOFFICE(?:|-x86)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + changes_url + "/\\2/ReleaseNotes.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink xml:lang=\"ru\">)(?:ONLYOFFICE(?:|-x86)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + changes_url + "/\\2/ReleaseNotesRU.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(url=\")(?:.+/)(ONLYOFFICE.+\")", "\\1" + update_url + "/\\2")

      for file in os.listdir(update_dir):
        if -1 == file.find(app_version) and (file.endswith(".zip") or file.endswith(".html")):
          base.delete_dir(update_dir + "/" + file)

  return
