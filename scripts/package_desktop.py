#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import zipfile
from concurrent.futures import ThreadPoolExecutor
import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("DESKTOP")
  if get_desktop_package_editions() == ["commercial"]:
    make_desktop_addon()
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported host OS")
  return

def get_desktop_package_editions():
  edition = getattr(common, "package_edition", "all")
  if edition in ["opensource", "commercial"]:
    return [edition]
  return ["opensource", "commercial"]

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

def make_desktop_addon():
  if common.platform == "darwin_x86_64_v8":
    return

  company_name_l = branding.company_name_l \
    if hasattr(branding, "company_name_l") else branding.company_name.lower()
  source_dir = utils.get_path("%s/build_tools/out/%s/%s/desktop-addon" \
    % (common.workspace_dir, common.prefix, company_name_l))
  zip_file = utils.get_path("%s/build_tools/out/%s/%s/%s" \
    % (common.workspace_dir, common.prefix, company_name_l,
       get_desktop_addon_filename()))

  utils.log_h2("desktop addon build")
  utils.log("source: " + source_dir)
  utils.log("output: " + zip_file)

  if not utils.is_dir(source_dir):
    utils.log_err("dir not exist: " + source_dir)
    utils.set_summary("desktop addon build", False)
    return False

  if utils.is_file(zip_file):
    utils.delete_file(zip_file)

  files = []
  for root, dirs, names in os.walk(source_dir):
    dirs.sort()
    for name in sorted(names):
      files.append(os.path.join(root, name))

  if not files:
    utils.log_err("dir is empty: " + source_dir)
    utils.set_summary("desktop addon build", False)
    return False

  if not sign_desktop_addon(files):
    utils.set_summary("desktop addon build", False)
    return False

  if utils.is_macos():
    try:
      subprocess.run([
        "ditto", "-c", "-k", "--sequesterRsrc", source_dir, zip_file
      ], check=True)
    except (OSError, subprocess.CalledProcessError) as err:
      utils.log_err("failed to create desktop addon zip: %s" % err)
      utils.set_summary("desktop addon build", False)
      return False
  else:
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as archive:
      for f in files:
        archive.write(f, os.path.relpath(f, source_dir).replace(os.sep, "/"))

  ret = utils.is_file(zip_file)
  utils.set_summary("desktop addon build", ret)

  # notarization of the addon is disabled for now: it needs the notarize_addon
  # lane in desktop-apps/macos/fastlane/Fastfile and will move to the branding
  if False and ret and common.sign and utils.is_macos():
    ret = notarize_macos_desktop_addon(zip_file)
    utils.set_summary("desktop addon notarize", ret)

  if common.deploy and ret:
    utils.log_h2("desktop addon deploy")
    ret = s3_upload([zip_file], get_desktop_addon_dst())
    utils.set_summary("desktop addon deploy", ret)

  return ret

def sign_desktop_addon(files):
  if not common.sign:
    return True

  if utils.is_macos():
    return sign_macos_desktop_addon(files)
  if utils.is_windows():
    return sign_windows_desktop_addon(files)

  return True

def sign_windows_desktop_addon(files):
  sign_script = utils.get_path(
    "%s/documents-pipeline/scripts/Sign.ps1" % common.workspace_dir)
  binaries = [f for f in files
    if os.path.splitext(f)[1].lower() in (".dll", ".exe")]

  utils.log_h2("desktop addon sign")
  for f in binaries:
    if not utils.ps1(sign_script, ["-File", f], verbose=True):
      utils.log_err("failed to sign: " + f)
      return False

  return True

def sign_macos_desktop_addon(files):
  identity = utils.get_env("CODESIGNING_IDENTITY")
  if not identity:
    utils.log_err("CODESIGNING_IDENTITY is not set")
    return False

  # executables get the entitlements of the app, as the "Rename symbols" phase of
  # ONLYOFFICE.xcodeproj does: under the hardened runtime docbuilder-tools needs
  # allow-dyld-environment-variables to find the engine through DYLD_* from aitools-bridge
  entitlements = get_macos_entitlements()
  if not utils.is_file(entitlements):
    utils.log_err("entitlements not found: " + entitlements)
    return False

  utils.log_h2("desktop addon sign")
  frameworks = set()
  for f in files:
    for match in re.finditer(r"\.framework(?=[\\/])", f, re.IGNORECASE):
      frameworks.add(f[:match.end()])

  for f in files + sorted(frameworks, key=lambda f: f.count(os.sep), reverse=True):
    try:
      framework = f.lower().endswith(".framework")
      executable = False
      if not framework:
        result = subprocess.run(
          ["file", "-b", f], stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT, check=True)
        if b"Mach-O" not in result.stdout:
          continue
        executable = b"executable" in result.stdout

      utils.log("codesign: " + f)
      sign_args = ["codesign", "--force", "--options", "runtime", "--timestamp"]
      if executable:
        sign_args += ["--entitlements", entitlements]
      subprocess.run(sign_args + ["--sign", identity, f], check=True)

      verify_args = ["codesign", "--verify", "--strict", "--verbose=2"]
      if framework:
        verify_args.append("--deep")
      subprocess.run(verify_args + [f], check=True)
    except (OSError, subprocess.CalledProcessError) as err:
      utils.log_err("failed to process %s: %s" % (f, err))
      return False

  return True

def get_macos_entitlements():
  _, suffix = get_desktop_addon_platform_info()
  return utils.get_path("%s/%s/ONLYOFFICE/Resources/%s-%s/ONLYOFFICE.entitlements" \
    % (common.workspace_dir, branding.desktop_branding_dir,
       branding.desktop_package_name, suffix))

def notarize_macos_desktop_addon(zip_file):
  # through fastlane: it already has the notarization credentials of the app
  # (Appfile, .env.secret). A zip is not stapled, Gatekeeper checks it online.
  utils.log_h2("desktop addon notarize")
  ret = utils.sh(
    "bundler exec fastlane notarize_addon package:\"%s\"" % zip_file,
    chdir=utils.get_path("%s/%s" \
      % (common.workspace_dir, branding.desktop_branding_dir)),
    verbose=True)
  if not ret:
    utils.log_err("failed to notarize: " + zip_file)
  return ret

def get_desktop_addon_dst():
  os_name, _ = get_desktop_addon_platform_info()
  return "desktop/%s/" % os_name

def get_desktop_addon_filename():
  _, arch = get_desktop_addon_platform_info()
  return "addon-%s.%s-%s.zip" % (common.version, common.build, arch)

def get_desktop_addon_platform_info():
  platform_map = {
    "windows_x64":      ["win",   "x64"],
    "windows_x86":      ["win",   "x86"],
    "windows_arm64":    ["win",   "arm64"],
    "windows_x64_xp":   ["win",   "x64_xp"],
    "windows_x86_xp":   ["win",   "x86_xp"],
    "darwin_arm64":     ["mac",   "arm"],
    "darwin_x86_64":    ["mac",   "x86_64"],
    "linux_x86_64":     ["linux", "x86_64"],
    "linux_aarch64":    ["linux", "aarch64"],
  }
  return platform_map[common.platform]

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

  editions = get_desktop_package_editions()

  if "opensource" in editions:
    if make_prepare():
      make_windows_packages("opensource")
    else:
      utils.set_summary("desktop zip opensource build", False)
      utils.set_summary("desktop inno opensource build", False)
      utils.set_summary("desktop advinst opensource build", False)

  if "commercial" in editions:
    if make_prepare("commercial"):
      make_windows_packages("commercial")
    else:
      utils.set_summary("desktop zip commercial build", False)
      utils.set_summary("desktop inno commercial build", False)
      utils.set_summary("desktop inno standalone build", False)
      utils.set_summary("desktop advinst commercial build", False)

  utils.set_cwd(common.workspace_dir)
  return

def make_windows_packages(edition):
  with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
      executor.submit(make_zip, edition),
      executor.submit(make_inno, edition),
      executor.submit(make_advinst, edition),
    ]
    if edition == "commercial":
      futures.append(executor.submit(make_inno, "standalone"))
    for future in futures:
      future.result()

def make_prepare(edition = "opensource"):
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  if common.branding:
    args += ["-Branding", common.branding]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("desktop prepare " + edition)
  ret = utils.ps1("make.ps1", args, verbose=True)
  utils.set_summary("desktop prepare " + edition, ret)
  return ret

def make_zip(edition = "opensource"):
  if edition == "commercial": zip_file = "%s-Enterprise-%s-%s.zip"
  else:                       zip_file = "%s-%s-%s.zip"
  zip_file = "zip\\" + zip_file % (package_name, package_version, arch)
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
  else:                         inno_file = "%s-%s-%s.exe"
  inno_file = "inno\\" + inno_file % (package_name, package_version, arch)
  args = [
    "-Version", package_version,
    "-Arch", arch,
    "-Target", edition
  ]
  if common.sign:
    args += ["-Sign"]

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
  advinst_file = "advinst\\" + advinst_file % (package_name, package_version, arch)
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
    % (common.workspace_dir, common.prefix, utils.get_branding_name())
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

  # defaults, can be overridden via the environment
  utils.set_env_default("DESKTOP_URL_UPDATES_MAIN_CHANNEL", branding.desktop_appcast_main_url)
  utils.set_env_default("DESKTOP_URL_UPDATES_DEV_CHANNEL", branding.desktop_appcast_dev_url)

  editions = get_desktop_package_editions()

  if "opensource" in editions:
    dmg = make_dmg()
    if dmg and sparkle_updates:
      make_sparkle_updates(
        scheme,
        branding.sparkle_base_url,
        "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
  if "commercial" in editions and common.platform != "darwin_x86_64_v8":
    dmg = make_dmg("commercial")
    if dmg and sparkle_updates and branding.onlyoffice:
      make_sparkle_updates(
        package_name + "-Enterprise-" + suffix,
        branding.sparkle_enterprise_base_url,
        "desktop/mac/enterprise/%s/%s/%s/" \
          % (suffix, common.version, common.build))

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

  deploy_dir = "desktop/mac/%s/%s/%s/" \
    % (suffix, common.version, common.build)
  if target == "commercial":
    deploy_dir = "desktop/mac/enterprise/%s/%s/%s/" \
      % (suffix, common.version, common.build)

  if common.deploy and dmg:
    utils.log_h2("desktop dmg " + target + " deploy")
    ret = s3_upload(
      utils.glob_path("build/*.dmg"),
      deploy_dir)
    utils.set_summary("desktop dmg deploy", ret)

  if common.deploy and dmg:
    zip_scheme = scheme
    if target == "commercial":
      zip_scheme = package_name + "-Enterprise-" + suffix
    utils.log_h2("desktop zip " + target + " deploy")
    ret = s3_upload(
      ["build/%s-%s.zip" % (zip_scheme, common.version)],
      deploy_dir)
    utils.set_summary("desktop zip " + target + " deploy", ret)
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
    % (common.workspace_dir, common.prefix, branding.company_name_l)
  if utils.is_file(source_dir + "/libvlc.so.5"):
    return "libvlc"
  return "qtmultimedia"

def make_linux():
  utils.set_cwd("desktop-apps/package")

  media_player = get_linux_media_player()
  utils.log("media player: " + media_player)

  for edition in get_desktop_package_editions():
    utils.log_h2("desktop " + edition + " build")
    make_args = [t["make"] for t in branding.desktop_make_targets]
    make_args.append("MEDIA_PLAYER=" + media_player)
    if edition == "commercial":
      make_args.append("PACKAGE_EDITION=commercial")
    if common.platform == "linux_aarch64":
      make_args.append("UNAME_M=aarch64")
    if not branding.onlyoffice:
      make_args.append("BRANDING_DIR=../../" + common.branding + "/desktop-apps/package")
    make_args.append("BRANDING=" + common.branding)
    ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
    utils.set_summary("desktop " + edition + " build", ret)

    if common.deploy:
      for t in branding.desktop_make_targets:
        utils.log_h2("desktop " + edition + " " + t["make"] + " deploy")
        uploads = []
        for f in utils.glob_path(t["src"]):
          if "help" in f and not \
            ("x86_64" in common.platform and edition == "opensource"): continue
          uploads.append(f)
        ret = s3_upload(uploads, t["dst"])
        utils.set_summary("desktop " + edition + " " + t["make"] + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
