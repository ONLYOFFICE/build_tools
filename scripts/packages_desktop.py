#!/usr/bin/env python

import base
import os
import re

def make(packages):
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."

  for package in packages:

    if -1 != package.find("diskimage"):
      macos_dir = os.path.abspath(git_dir + "/desktop-apps/macos")
      update_dir = macos_dir + "/build/update"
      changes_dir = macos_dir + "/ONLYOFFICE/update/updates/ONLYOFFICE/changes"

      if (package == "diskimage-x86_64"):
        lane = "release_x86_64"
        scheme = "ONLYOFFICE-x86_64"
      elif (package == "diskimage-v8-x86_64"):
        lane = "release_v8"
        scheme = "ONLYOFFICE-v8"
      elif (package == "diskimage-arm64"):
        lane = "release_arm"
        scheme = "ONLYOFFICE-arm"
      else:
        exit(1)

      print("Build package " + scheme)

      print("$ bundler exec fastlane " + lane + " skip_git_bump:true")
      base.cmd_in_dir(macos_dir, "bundler", ["exec", "fastlane", lane, "skip_git_bump:true"])

      print("Build updates")

      app_version = base.run_command("/usr/libexec/PlistBuddy -c 'print :CFBundleShortVersionString' " +
        macos_dir + "/build/ONLYOFFICE.app/Contents/Info.plist")['stdout']
      macos_zip = macos_dir + "/build/" + scheme + "-" + app_version + ".zip"
      update_storage_dir = base.get_env("ARCHIVES_DIR") + "/" + scheme + "/_updates"

      base.create_dir(update_dir)
      base.copy_dir_content(update_storage_dir, update_dir, ".zip")
      base.copy_file(macos_zip, update_dir)
      for file in os.listdir(update_dir):
        if file.endswith(".zip"):
          zip_name = os.path.splitext(file)[0]
          zip_ver = os.path.splitext(file)[0].split("-")[-1]
          base.copy_file(changes_dir + "/" + zip_ver + "/ReleaseNotes.html",   update_dir + "/" + zip_name + ".html")
          base.copy_file(changes_dir + "/" + zip_ver + "/ReleaseNotesRU.html", update_dir + "/" + zip_name + ".ru.html")

      print("$ ./generate_appcast " + update_dir)
      base.cmd(macos_dir + "/Vendor/Sparkle/bin/generate_appcast", [update_dir])

      print("Edit Sparkle appcast links")

      sparkle_base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"
      if (platform == "mac_64" and isV8): sparkle_base_url += "/v8"
      elif (platform == "mac_64"):        sparkle_base_url += "/x86_64"
      elif (platform == "mac_arm64"):     sparkle_base_url += "/arm"

      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink>)(?:.+ONLYOFFICE-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotes.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink xml:lang=\"ru\">)(?:ONLYOFFICE-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotesRU.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(url=\")(?:.+/)(ONLYOFFICE.+\")", "\\1" + sparkle_base_url + "/updates/\\2")

      print("Delete unnecessary files")

      for file in os.listdir(update_dir):
        if (-1 == file.find(app_version)) and (file.endswith(".zip") or file.endswith(".html")):
          base.delete_file(update_dir + "/" + file)

  return
