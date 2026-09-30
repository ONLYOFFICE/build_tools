#!/usr/bin/env python
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
import package_utils as utils
import package_common as common
import package_branding as branding

# The branding lists the sets of packages in branding.desktop_variants. Every key
# of a variant is optional, the empty variant builds the defaults of the
# packaging repositories:
#   name             - the name of the variant in the build summary
#   target           - -Target of desktop-apps/package/make*.ps1
#   file_suffix      - added to the package name in the file names
#   inno_extra       - more inno installers of the variant, each with its own
#                      name, target and file_suffix
#   fastlane_args    - more arguments of the fastlane lane
#   make_args        - more arguments of desktop-apps/package/Makefile
#   mac_deploy_dir   - the s3 directory of the macOS packages, desktop/mac
#   sparkle_base_url - the url of the macOS updates, no updates without it
#   deploy_help      - uploads the help packages of Linux, True
#   skip_platforms   - the platforms the variant is not built for

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

def get_variants():
  variants = getattr(branding, "desktop_variants", [{}])
  return [v for v in variants
    if common.platform not in v.get("skip_platforms", [])]

def get_title(*parts):
  return " ".join([p for p in parts if p])

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
  global package_name, package_version, arch
  utils.set_cwd("desktop-apps\\package")

  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  arch = {
    "windows_x64":    "x64",
    "windows_x86":    "x86",
    "windows_arm64":  "arm64"
  }[common.platform]

  if common.clean:
    utils.log_h2("desktop clean")
    utils.delete_dir("build")
    utils.delete_files("inno\\package*.config")
    utils.delete_files("inno\\*\\package.config")
    utils.delete_files("inno\\*.exe")
    utils.delete_dir("advinst\\DesktopEditors-cache")
    utils.delete_files("advinst\\package.config")
    utils.delete_files("advinst\\*.msi")
    utils.delete_files("advinst\\*.aic")
    utils.delete_dir("zip")

  for variant in get_variants():
    if make_prepare(variant):
      make_windows_packages(variant)
    else:
      name = variant.get("name")
      utils.set_summary(get_title("desktop zip", name, "build"), False)
      utils.set_summary(get_title("desktop inno", name, "build"), False)
      for extra in variant.get("inno_extra", []):
        utils.set_summary(get_title("desktop inno", extra.get("name"), "build"), False)
      utils.set_summary(get_title("desktop advinst", name, "build"), False)

  utils.set_cwd(common.workspace_dir)
  return

def make_windows_packages(variant):
  with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
      executor.submit(make_zip, variant),
      executor.submit(make_inno, variant),
      executor.submit(make_advinst, variant),
    ]
    for extra in variant.get("inno_extra", []):
      futures.append(executor.submit(make_inno, extra))
    for future in futures:
      future.result()

def get_windows_args(variant):
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  if variant.get("target"):
    args += ["-Target", variant["target"]]
  return args

def get_windows_file(variant, file_format):
  return file_format % (package_name + variant.get("file_suffix", ""),
    package_version, arch)

def make_prepare(variant):
  args = get_windows_args(variant)
  args += ["-Branding", utils.get_branding_name()]
  if common.sign:
    args += ["-Sign"]

  title = get_title("desktop prepare", variant.get("name"))
  utils.log_h2(title)
  ret = utils.ps1("make.ps1", args, verbose=True)
  utils.set_summary(title, ret)
  return ret

def make_zip(variant):
  zip_file = "zip\\" + get_windows_file(variant, "%s-%s-%s.zip")
  args = get_windows_args(variant)
  # if common.sign:
  #   args += ["-Sign"]

  name = variant.get("name")
  utils.log_h2(get_title("desktop zip", name, "build"))
  ret = utils.ps1("make_zip.ps1", args, verbose=True)
  utils.set_summary(get_title("desktop zip", name, "build"), ret)

  if common.deploy and ret:
    utils.log_h2(get_title("desktop zip", name, "deploy"))
    ret = s3_upload([zip_file], "desktop/win/generic/")
    utils.set_summary(get_title("desktop zip", name, "deploy"), ret)
  return

def make_inno(variant):
  inno_file = "inno\\" + get_windows_file(variant, "%s-%s-%s.exe")
  args = get_windows_args(variant)
  if common.sign:
    args += ["-Sign"]

  name = variant.get("name")
  utils.log_h2(get_title("desktop inno", name, "build"))
  ret = utils.ps1("make_inno.ps1", args, verbose=True)
  utils.set_summary(get_title("desktop inno", name, "build"), ret)

  if common.deploy and ret:
    utils.log_h2(get_title("desktop inno", name, "deploy"))
    ret = s3_upload([inno_file], "desktop/win/inno/")
    utils.set_summary(get_title("desktop inno", name, "deploy"), ret)
  return

def make_advinst(variant):
  advinst_file = "advinst\\" + get_windows_file(variant, "%s-%s-%s.msi")
  args = get_windows_args(variant)
  if common.sign:
    args += ["-Sign"]

  name = variant.get("name")
  utils.log_h2(get_title("desktop advinst", name, "build"))
  ret = utils.ps1("make_advinst.ps1", args, verbose=True)
  utils.set_summary(get_title("desktop advinst", name, "build"), ret)

  if common.deploy and ret:
    utils.log_h2(get_title("desktop advinst", name, "deploy"))
    ret = s3_upload([advinst_file], "desktop/win/advinst/")
    utils.set_summary(get_title("desktop advinst", name, "deploy"), ret)
  return

#
# macOS
#

def make_macos():
  global package_name, build_dir, branding_dir, updates_dir, changes_dir, \
    suffix, lane, scheme, released_updates_dir
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
  # the branding serves the help online instead of the one in the bundle
  if getattr(branding, "desktop_remove_help", False):
    source_dir = "%s/build_tools/out/%s/%s" \
      % (common.workspace_dir, common.prefix, utils.get_branding_name())
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

    utils.sh('%s -c "Set :CFBundleShortVersionString %s" %s' \
        % (plistbuddy, common.version, plist_path), verbose=True)
    utils.sh('%s -c "Set :CFBundleVersion %s" %s' \
        % (plistbuddy, bundle_version, plist_path), verbose=True)
    utils.sh('%s -c "Set :ASCBundleBuildNumber %s" %s' \
        % (plistbuddy, common.build, plist_path), verbose=True)
    # a format with the version, as the help of every version is kept
    help_url = getattr(branding, "desktop_help_url", None)
    if help_url:
      utils.sh('%s -c "Add :ASCWebappsHelpUrl string %s" %s' \
          % (plistbuddy, help_url % common.version, plist_path), verbose=True)

    utils.log("RELEASE=" + release_version_string + "(" + release_version + ")" \
          + "\nCURRENT=" + common.version + "(" + bundle_version + ")")

  # defaults, can be overridden via the environment
  if hasattr(branding, "desktop_appcast_main_url"):
    utils.set_env_default("DESKTOP_URL_UPDATES_MAIN_CHANNEL", branding.desktop_appcast_main_url)
  if hasattr(branding, "desktop_appcast_dev_url"):
    utils.set_env_default("DESKTOP_URL_UPDATES_DEV_CHANNEL", branding.desktop_appcast_dev_url)

  for variant in get_variants():
    dmg = make_dmg(variant)
    if dmg and sparkle_updates and variant.get("sparkle_base_url"):
      make_sparkle_updates(
        get_macos_scheme(variant),
        variant["sparkle_base_url"],
        get_macos_deploy_dir(variant))

  utils.set_cwd(common.workspace_dir)
  return

def get_macos_scheme(variant):
  return package_name + variant.get("file_suffix", "") + "-" + suffix

def get_macos_deploy_dir(variant):
  return "%s/%s/%s/%s/" % (variant.get("mac_deploy_dir", "desktop/mac"),
    suffix, common.version, common.build)

def make_dmg(variant):
  name = variant.get("name")
  utils.log_h2(get_title("desktop dmg", name, "build"))
  utils.log_h3("build/" + package_name + ".app")
  args = ["bundler", "exec", "fastlane", lane, "skip_git_bump:true"]
  args += variant.get("fastlane_args", [])
  dmg = utils.sh(" ".join(args), verbose=True)
  utils.set_summary(get_title("desktop dmg", name, "build"), dmg)

  deploy_dir = get_macos_deploy_dir(variant)

  if common.deploy and dmg:
    utils.log_h2(get_title("desktop dmg", name, "deploy"))
    ret = s3_upload(
      utils.glob_path("build/*.dmg"),
      deploy_dir)
    utils.set_summary("desktop dmg deploy", ret)

  if common.deploy and dmg:
    utils.log_h2(get_title("desktop zip", name, "deploy"))
    ret = s3_upload(
      ["build/%s-%s.zip" % (get_macos_scheme(variant), common.version)],
      deploy_dir)
    utils.set_summary(get_title("desktop zip", name, "deploy"), ret)
  return dmg

def make_sparkle_updates(archive_scheme, sparkle_base_url, deploy_dir):
  utils.log_h2("desktop sparkle files build")

  zip_filename = archive_scheme + '-' + common.version
  macos_zip = "build/" + zip_filename + ".zip"
  released_updates_dir = "%s/%s/_updates" \
    % (utils.get_env("ARCHIVES_DIR"), archive_scheme)
  utils.create_dir(updates_dir)
  utils.copy_file(macos_zip, updates_dir)
  if utils.is_dir(released_updates_dir):
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

  sparkle_base_url = "%s/%s/updates/" % (sparkle_base_url, suffix)
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
    files = utils.glob_path("build/update/*.delta") \
      + utils.glob_path("build/update/*.xml") \
      + utils.glob_path("build/update/*.html")
    ret = s3_upload(files, deploy_dir)
    utils.set_summary("desktop sparkle files deploy", ret)
  return

#
# Linux
#

def get_linux_media_player():
  # the videoplayer backend is chosen at build time (CONFIG libvlc, see config_addon_linux),
  # the deploy tells which one the packages carry, as vlc-cache-gen.exe does for make.ps1
  source_dir = "%s/build_tools/out/%s/%s/desktopeditors" \
    % (common.workspace_dir, common.prefix, utils.get_branding_name())
  if utils.is_file(source_dir + "/libvlc.so.5"):
    return "libvlc"
  return "qtmultimedia"

def make_linux():
  utils.set_cwd("desktop-apps/package")

  media_player = get_linux_media_player()
  utils.log("media player: " + media_player)
  package_dir = utils.get_branding_package_dir("desktop-apps/package")

  for variant in get_variants():
    name = variant.get("name")
    utils.log_h2(get_title("desktop", name, "build"))
    make_args = [t["make"] for t in branding.desktop_make_targets]
    make_args.append("MEDIA_PLAYER=" + media_player)
    make_args += variant.get("make_args", [])
    if common.platform == "linux_aarch64":
      make_args.append("UNAME_M=aarch64")
    if package_dir:
      make_args.append("BRANDING_DIR=../../" + package_dir)
    make_args.append("BRANDING=" + utils.get_branding_name())
    ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
    utils.set_summary(get_title("desktop", name, "build"), ret)

    if common.deploy:
      # the help packages do not depend on the architecture, one upload is enough
      deploy_help = variant.get("deploy_help", True) \
        and "x86_64" in common.platform
      for t in branding.desktop_make_targets:
        utils.log_h2(get_title("desktop", name, t["make"], "deploy"))
        uploads = []
        for f in utils.glob_path(t["src"]):
          if "help" in f and not deploy_help: continue
          uploads.append(f)
        ret = s3_upload(uploads, t["dst"])
        utils.set_summary(get_title("desktop", name, t["make"], "deploy"), ret)

  utils.set_cwd(common.workspace_dir)
  return
