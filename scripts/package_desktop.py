#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("DESKTOP")
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported host OS")
  return

def s3_upload(files, dst):
  if not files: return False
  ret = True
  for f in files:
    key = dst + utils.get_basename(f) if dst.endswith("/") else dst
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
    ret &= upload
  return ret

#
# Windows
#

def make_windows():
  global package_name, package_version, arch, xp
  utils.set_cwd("desktop-apps\\win-linux\\package\\windows")

  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  arch = {
    "windows_x64":    "x64",
    "windows_x64_xp": "x64",
    "windows_x86":    "x86",
    "windows_x86_xp": "x86"
  }[common.platform]
  xp = common.platform.endswith("_xp")

  if common.clean:
    utils.log_h2("desktop clean")
    utils.delete_dir("DesktopEditors-cache")
    utils.delete_files("*.exe")
    utils.delete_files("*.msi")
    utils.delete_files("*.aic")
    utils.delete_files("*.tmp")
    utils.delete_files("*.zip")
    utils.delete_files("data\\*.exe")

  if not xp:
    make_prepare()
    make_zip()
    make_inno()
    if branding.onlyoffice:
      make_inno("standalone")
      make_inno("update")
    make_advinst()

    make_prepare("commercial")
    make_zip("commercial")
    make_inno("commercial")
    make_advinst("commercial")
  else:
    make_prepare("xp")
    make_zip("xp")
    make_inno("xp")
  # Disable build online installer
  # if common.platform == "windows_x86_xp":
  #  make_online()

  utils.set_cwd(common.workspace_dir)
  return

def make_prepare(edition = "opensource"):
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("desktop prepare " + edition)
  ret = utils.ps1("make.ps1", args, verbose=True)
  utils.set_summary("desktop prepare " + edition, ret)
  return

def make_zip(edition = "opensource"):
  if   edition == "commercial": zip_file = "%s-Enterprise-%s-%s.zip"
  elif edition == "xp":         zip_file = "%s-XP-%s-%s.zip"
  else:                         zip_file = "%s-%s-%s.zip"
  zip_file = zip_file % (package_name, package_version, arch)
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  # if common.sign:
  #   args += ["-Sign"]

  utils.log_h2("desktop zip " + edition + " build")
  ret = utils.ps1("make_zip.ps1", args, verbose=True)
  utils.set_summary("desktop zip " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop zip " + edition + " deploy")
    ret = s3_upload([zip_file], "desktop/win/generic/")
    utils.set_summary("desktop zip " + edition + " deploy", ret)
  return

def make_inno(edition = "opensource"):
  if   edition == "commercial": inno_file = "%s-Enterprise-%s-%s.exe"
  elif edition == "standalone": inno_file = "%s-Standalone-%s-%s.exe"
  elif edition == "update":     inno_file = "%s-Update-%s-%s.exe"
  elif edition == "xp":         inno_file = "%s-XP-%s-%s.exe"
  else:                         inno_file = "%s-%s-%s.exe"
  inno_file = inno_file % (package_name, package_version, arch)
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  if common.sign:
    args += ["-Sign"]

  if xp:
    args += ["-TimestampServer", "http://timestamp.comodoca.com/authenticode"]

  utils.log_h2("desktop inno " + edition + " build")
  ret = utils.ps1("make_inno.ps1", args, verbose=True)
  utils.set_summary("desktop inno " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop inno " + edition + " deploy")
    ret = s3_upload([inno_file], "desktop/win/inno/")
    utils.set_summary("desktop inno " + edition + " deploy", ret)
  return

def make_advinst(edition = "opensource"):
  if edition == "commercial": advinst_file = "%s-Enterprise-%s-%s.msi"
  else:                       advinst_file = "%s-%s-%s.msi"
  advinst_file = advinst_file % (package_name, package_version, arch)
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("desktop advinst " + edition + " build")
  ret = utils.ps1("make_advinst.ps1", args, verbose=True)
  utils.set_summary("desktop advinst " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop advinst " + edition + " deploy")
    ret = s3_upload([advinst_file], "desktop/win/advinst/")
    utils.set_summary("desktop advinst " + edition + " deploy", ret)
  return

def make_online():
  online_file = utils.glob_file("OnlineInstaller-" + package_version + "*.exe")
  utils.log_h2("desktop online installer build")
  ret = utils.is_file(online_file)
  utils.set_summary("desktop online installer build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop online installer deploy")
    ret = s3_upload([online_file], "desktop/win/online/")
    utils.set_summary("desktop online installer deploy", ret)
  return

#
# macOS
#

def make_macos():
  global package_name, build_dir, branding_dir, updates_dir, changes_dir, \
    suffix, lane, scheme, source_dir, released_updates_dir
  package_name = branding.desktop_package_name
  build_dir = branding.desktop_build_dir
  branding_dir = branding.desktop_branding_dir
  updates_dir = branding.desktop_updates_dir
  changes_dir = branding.desktop_changes_dir
  suffix = {
    "darwin_x86_64":    "x86_64",
    "darwin_x86_64_v8": "v8",
    "darwin_arm64":     "arm"
  }[common.platform]
  lane = "release_" + suffix
  scheme = package_name + "-" + suffix
  sparkle_updates = False

  utils.set_cwd(branding_dir)

  if common.clean:
    utils.log_h2("clean")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Developer/Xcode/Archives")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Caches/Sparkle_generate_appcast")

  utils.log_h2("build")
  source_dir = "%s/build_tools/out/%s/%s" \
    % (common.workspace_dir, common.prefix, branding.company_name)
  if branding.onlyoffice:
    for path in utils.glob_path(source_dir \
        + "/desktopeditors/editors/web-apps/apps/*/main/resources/help"):
      utils.delete_dir(path)

  if utils.get_env("ARCHIVES_DIR"):
    sparkle_updates = True
    released_updates_dir = "%s/%s/_updates" % (utils.get_env("ARCHIVES_DIR"), scheme)
    plistbuddy = "/usr/libexec/PlistBuddy"
    plist_path = "%s/%s/ONLYOFFICE/Resources/%s-%s/Info.plist" \
        % (common.workspace_dir, branding_dir, package_name, suffix)

    appcast = utils.sh_output('%s -c "Print :SUFeedURL" %s' \
        % (plistbuddy, plist_path), verbose=True).rstrip()
    appcast = released_updates_dir + "/" + appcast[appcast.rfind("/")+1:]

    release_version_string = utils.sh_output(
        'xmllint --xpath "/rss/channel/item[1]/*[name()=\'sparkle:shortVersionString\']/text()" ' + appcast,
        verbose=True).rstrip()
    release_version = utils.sh_output(
        'xmllint --xpath "/rss/channel/item[1]/*[name()=\'sparkle:version\']/text()" ' + appcast,
        verbose=True).rstrip()
    bundle_version = str(int(release_version) + 1)
    help_url = "https://download.onlyoffice.com/install/desktop/editors/help/v" + common.version + "/apps"

    utils.sh('%s -c "Set :CFBundleShortVersionString %s" %s' \
        % (plistbuddy, common.version, plist_path), verbose=True)
    utils.sh('%s -c "Set :CFBundleVersion %s" %s' \
        % (plistbuddy, bundle_version, plist_path), verbose=True)
    utils.sh('%s -c "Set :ASCBundleBuildNumber %s" %s' \
        % (plistbuddy, common.build, plist_path), verbose=True)
    utils.sh('%s -c "Add :ASCWebappsHelpUrl string %s" %s' \
        % (plistbuddy, help_url, plist_path), verbose=True)

    utils.log("RELEASE=" + release_version_string + "(" + release_version + ")" \
          + "\nCURRENT=" + common.version + "(" + bundle_version + ")")

  dmg = make_dmg()
  if dmg and sparkle_updates:
    make_sparkle_updates()
  if common.platform != "darwin_x86_64_v8":
    make_dmg("commercial")

  utils.set_cwd(common.workspace_dir)
  return

def make_dmg(target = "opensource"):
  utils.log_h2("desktop dmg " + target + " build")
  utils.log_h3("build/" + package_name + ".app")
  args = ["bundler", "exec", "fastlane", lane, "skip_git_bump:true"]
  if target == "commercial":
    args += ["edition:Enterprise"]
  dmg = utils.sh(" ".join(args), verbose=True)
  utils.set_summary("desktop dmg " + target + " build", dmg)

  if common.deploy and dmg:
    utils.log_h2("desktop dmg " + target + " deploy")
    ret = s3_upload(
      utils.glob_path("build/*.dmg"),
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop dmg deploy", ret)

  if common.deploy and dmg and target != "commercial":
    utils.log_h2("desktop zip " + target + " deploy")
    ret = s3_upload(
      ["build/%s-%s.zip" % (scheme, common.version)],
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop zip " + target + " deploy", ret)
  return dmg

def make_sparkle_updates():
  utils.log_h2("desktop sparkle files build")

  zip_filename = scheme + '-' + common.version
  macos_zip = "build/" + zip_filename + ".zip"
  utils.create_dir(updates_dir)
  utils.copy_file(macos_zip, updates_dir)
  utils.sh(
    "ls -1t " + released_updates_dir + "/*.zip" \
      + " | head -n 3" \
      + " | while read f; do cp -fv \"$f\" " + updates_dir + "/; done",
    verbose=True)

  for ext in [".html", ".ru.html"]:
    changes_src = changes_dir + "/" + common.version + "/changes" + ext
    changes_dst = updates_dir + "/" + zip_filename + ext
    if not utils.copy_file(changes_src, changes_dst):
      utils.write_file(changes_dst, "<!DOCTYPE html>placeholder")

  sparkle_base_url = "%s/%s/updates/" % (branding.sparkle_base_url, suffix)
  ret = utils.sh(
      common.workspace_dir \
      + "/desktop-apps/macos/Vendor/Sparkle/bin/generate_appcast " \
      + updates_dir \
      + " --download-url-prefix " + sparkle_base_url \
      + " --release-notes-url-prefix " + sparkle_base_url,
      verbose=True
  )
  utils.set_summary("desktop sparkle files build", ret)

  if common.deploy:
    utils.log_h2("desktop sparkle files deploy")
    ret = s3_upload(
      utils.glob_path("build/update/*.delta") \
      + utils.glob_path("build/update/*.xml") \
      + utils.glob_path("build/update/*.html"),
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop sparkle files deploy", ret)
  return

#
# Linux
#

def make_linux():
  utils.set_cwd("desktop-apps/win-linux/package/linux")

  for edition in ["opensource", "commercial"]:
    utils.log_h2("desktop " + edition + " build")
    make_args = [t["make"] for t in branding.desktop_make_targets]
    if edition == "commercial":
      make_args += ["-e", "PACKAGE_EDITION=commercial"]
    if common.platform == "linux_aarch64":
      make_args += ["-e", "UNAME_M=aarch64"]
    if not branding.onlyoffice:
      make_args += ["-e", "BRANDING_DIR=../../../../" + common.branding + "/desktop-apps/win-linux/package/linux"]
    ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
    utils.set_summary("desktop " + edition + " build", ret)

    if common.deploy:
      for t in branding.desktop_make_targets:
        utils.log_h2("desktop " + edition + " " + t["make"] + " deploy")
        ret = s3_upload(utils.glob_path(t["src"]), t["dst"])
        utils.set_summary("desktop " + edition + " " + t["make"] + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
