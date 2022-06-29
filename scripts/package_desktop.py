#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
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

#
# Windows
#

def make_windows():
  global package_version, iscc_args, source_dir, arch_list, inno_arch_list, \
    inno_file, inno_update_file, msi_file, zip_file
  utils.set_cwd("desktop-apps\\win-linux\\package\\windows")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.desktop_product_name.replace(" ","").lower()
  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  source_dir = "..\\..\\..\\..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  arch_list = {
    "windows_x64":    "x64",
    "windows_x64_xp": "x64",
    "windows_x86":    "x86",
    "windows_x86_xp": "x86"
  }
  inno_arch_list = {
    "windows_x64":    "64",
    "windows_x86":    "32",
    "windows_x64_xp": "64",
    "windows_x86_xp": "32"
  }
  suffix = arch_list[common.platform]
  if common.platform.endswith("_xp"): suffix += "_xp"
  zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
  inno_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
  inno_update_file = "update\\editors_update_%s.exe" % suffix
  msi_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)

  if common.clean:
    utils.log_h2("desktop clean")
    utils.delete_dir("data\\vcredist")
    utils.delete_dir("DesktopEditors-cache")
    utils.delete_files("*.exe")
    utils.delete_files("*.msi")
    utils.delete_files("*.aic")
    utils.delete_files("*.tmp")
    utils.delete_files("*.zip")
    utils.delete_files("update\\*.exe")
    utils.delete_files("update\\*.xml")
    utils.delete_files("update\\*.html")

  make_zip()

  for year in branding.desktop_vcredist_list:
    download_vcredist(year)

  if vcredist_status != 0:
    common.summary["desktop inno build"] = 1
    common.summary["desktop inno update build"] = 1
    common.summary["desktop advinst build"] = 1
    return

  make_inno()
  make_inno_update()

  if common.platform == "windows_x64":
    make_winsparkle_files()

  if common.platform in ["windows_x64", "windows_x86"]:
    make_msi()
  return

def make_zip():
  utils.log_h1("desktop zip build")
  utils.log_h2(zip_file)
  rc = utils.cmd("7z", "a", "-y", zip_file, source_dir + "\\*",
                 creates=zip_file, verbose=True)
  common.summary["desktop zip build"] = rc
  return

def download_vcredist(year):
  global vcredist_status
  utils.log_h1("download vcredist " + year)

  arch = arch_list[common.platform]
  link = common.vcredist_links[year][arch]["url"]
  checksum = common.vcredist_links[year][arch]["checksum"]
  vcredist_file = "data\\vcredist\\vcredist_%s_%s.exe" % (year, arch)

  utils.log_h2(vcredist_file)
  utils.create_dir(utils.get_dirname(vcredist_file))
  rc = utils.download_file(link, vcredist_file, checksum, verbose=True)
  vcredist_status = rc
  common.summary["desktop vcredist download"] = rc
  return

def make_inno():
  global iscc_args
  utils.log_h1("innosetup project build")
  utils.log_h2(inno_file)

  iscc_args = [
    # "/Qp",
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + inno_arch_list[common.platform]
  ]
  if branding.onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=..\\..\\..\\..\\" + common.branding + \
        "\\desktop-apps\\win-linux\\package\\windows")
  if common.platform in ["windows_x64_xp", "windows_x86_xp"]:
    iscc_args.append("/D_WIN_XP=1")
  if common.sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + \
        branding.cert_name + "$q /t " + common.tsa_server + " $f")
  args = ["iscc"] + iscc_args + ["common.iss"]
  rc = utils.cmd(*args, creates=inno_file, verbose=True)
  common.summary["desktop inno build"] = rc
  return

def make_inno_update():
  utils.log_h1("build innosetup update project")
  utils.log_h2(inno_update_file)

  args = ["iscc"] + iscc_args + ["/DTARGET_NAME=" + inno_file, "update_common.iss"]
  rc = utils.cmd(*args, creates=inno_update_file, verbose=True)
  common.summary["desktop inno update build"] = rc
  return

def make_winsparkle_files():
  utils.log_h1("winsparkle files build")

  if branding.onlyoffice:
    awk_branding = "update/branding.awk"
  else:
    awk_branding = "../../../../" + common.branding + \
        "/desktop-apps/win-linux/package/windows/update/branding.awk"
  awk_args = [
    "-v", "Version=" + common.version,
    "-v", "Build=" + common.build,
    "-v", "Timestamp=" + common.timestamp,
    "-i", awk_branding
  ]

  appcast = "update/appcast.xml"
  utils.log_h2(appcast)
  args = ["env", "LANG=en_US.UTF-8", "awk"] + \
      awk_args + ["-f", "update/appcast.xml.awk"]
  appcast_result = utils.cmd_output(*args, verbose=True)
  utils.write_file(appcast, appcast_result)

  appcast_prod = "update/appcast-prod.xml"
  utils.log_h2(appcast_prod)
  args = ["env", "LANG=en_US.UTF-8", "awk", "-v", "Prod=1"] + \
      awk_args + ["-f", "update/appcast.xml.awk"]
  appcast_result = utils.cmd_output(*args, verbose=True)
  utils.write_file(appcast, appcast_result)

  if branding.onlyoffice:
    changes_dir = "update/changes/" + common.version
  else:
    changes_dir = "../../../../" + common.branding + \
        "/desktop-apps/win-linux/package/windows/update/changes/" + common.version
  for lang, base in branding.desktop_update_changes_list.items():
    changes = "update/%s.html" % base
    if   lang == "en": encoding = "en_US.UTF-8"
    elif lang == "ru": encoding = "ru_RU.UTF-8"
    utils.log_h2(changes)
    changes_file = "%s/%s.html" % (changes_dir, lang)
    args = ["env", "LANG=" + encoding, "awk"] + awk_args + \
      ["-f", "update/changes.html.awk", changes_file]

    if utils.is_exist(changes_file):
      changes_result = utils.cmd_output(*args, verbose=True)
      print(changes_result)
      utils.write_file(changes, changes_result)
    else:
      utils.log("! file not exist: " + changes_file)
  return

def make_msi():
  utils.log_h1("advanced installer project build")
  utils.log_h2(msi_file)

  arch = arch_list[common.platform]

  aic_content = [";aic"]
  if not branding.onlyoffice:
    utils.copy_dir_content("..\\..\\..\\..\\" + common.branding + \
        "\\desktop-apps\\win-linux\\package\\windows\\data", "data", ".bmp")
    utils.copy_dir_content("..\\..\\..\\..\\" + common.branding + \
        "\\desktop-apps\\win-linux\\package\\windows\\data", "data", ".png")
    aic_content += [
      "SetProperty ProductName=\"%s\"" % branding.desktop_product_name_full,
      "SetProperty Manufacturer=\"%s\"" % branding.desktop_publisher_name.replace('"', '""'),
      "SetProperty ARPURLINFOABOUT=\"%s\"" % branding.desktop_info_about_url,
      "SetProperty ARPURLUPDATEINFO=\"%s\"" % branding.desktop_update_info_url,
      "SetProperty ARPHELPLINK=\"%s\"" % branding.desktop_help_url,
      "SetProperty ARPHELPTELEPHONE=\"%s\"" % branding.desktop_help_phone,
      "SetProperty ARPCONTACT=\"%s\"" % branding.desktop_publisher_address,
      "DelLanguage 1029 -buildname DefaultBuild",
      "DelLanguage 1031 -buildname DefaultBuild",
      "DelLanguage 1041 -buildname DefaultBuild",
      "DelLanguage 1046 -buildname DefaultBuild",
      "DelLanguage 2070 -buildname DefaultBuild",
      "DelLanguage 1060 -buildname DefaultBuild",
      "DelLanguage 1036 -buildname DefaultBuild",
      "DelLanguage 3082 -buildname DefaultBuild",
      "DelLanguage 1033 -buildname DefaultBuild"
    ]
  if not common.sign: aic_content.append("ResetSig")
  if arch == "x86": aic_content.append("SetPackageType x86")
  aic_content += [
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "NewSync APPDIR " + source_dir + " -existingfiles delete",
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
    "SetVersion " + package_version,
    "SetPackageName " + msi_file + " -buildname DefaultBuild",
    "Rebuild -buildslist DefaultBuild"
  ]
  utils.write_file("DesktopEditors.aic", "\r\n".join(aic_content), "utf-8-sig")
  rc = utils.cmd("AdvancedInstaller.com", "/execute", \
    "DesktopEditors.aip", "DesktopEditors.aic", "-nofail")
  common.summary["desktop advinst build"] = rc
  return

#
# macOS
#

def make_macos():
  global suffix, lane, scheme

  set_cwd(git_dir + "/" + branding_build_dir)

  for target in targets:
    if not target.startswith('diskimage'):
      continue

    if target.startswith('diskimage'):
      if   (target == 'diskimage-x64'):    suffix = 'x86_64'
      elif (target == 'diskimage-x64-v8'): suffix = 'v8'
      elif (target == 'diskimage-arm64'):  suffix = 'arm'
      else: exit(1)
      lane = "release_" + suffix
      scheme = package_name + '-' + suffix

      make_diskimage(target)

      if ('sparkle-updates' in targets):
        make_sparkle_updates()
  return

def make_diskimage(target):
  log("\n=== Build package " + scheme + "\n")
  log("--- build/" + package_name + ".app")
  cmd("bundler", ["exec", "fastlane", lane, "skip_git_bump:true"])
  return

def make_sparkle_updates():
  log("\n=== Build sparkle updates\n")

  app_version = proc_open("/usr/libexec/PlistBuddy \
    -c 'print :CFBundleShortVersionString' \
    build/" + package_name + ".app/Contents/Info.plist")['stdout']
  zip_filename = scheme + '-' + app_version
  macos_zip = "build/" + zip_filename + ".zip"
  updates_storage_dir = "%s/%s/_updates" % (get_env('ARCHIVES_DIR'), scheme)
  create_dir(updates_dir)
  copy_dir_content(updates_storage_dir, updates_dir, ".zip")
  copy_dir_content(updates_storage_dir, updates_dir, ".html")
  copy_file(macos_zip, updates_dir)

  for lang, base in update_changes_list.items():
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, base)
    notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
    if lang == 'en':
      encoding = 'en_US.UTF-8'
      cur_date = proc_open("env LC_ALL=" + encoding + " date -u \"+%B %e, %Y\"")['stdout']
    elif lang == 'ru':
      encoding = 'ru_RU.UTF-8'
      cur_date = proc_open("env LC_ALL=" + encoding + " date -u \"+%e %B %Y\"")['stdout']
    if is_file(notes_src):
      copy_file(notes_src, notes_dst)
      replace_in_file(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    # else:
    #   write_file(notes_dst, "placeholder\n")
  cmd(git_dir + "/" + build_dir + "/Vendor/Sparkle/bin/generate_appcast", [updates_dir])

  log("\n=== Edit Sparkle appcast links\n")
  appcast_url = sparkle_base_url + "/" + suffix
  appcast = "%s/%s.xml" % (updates_dir, package_name.lower())

  for lang, base in update_changes_list.items():
    if base == "ReleaseNotes":
      replace_in_file(appcast,
        r"(<sparkle:releaseNotesLink>)(?:.+" + package_name + \
        "-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + appcast_url + "/updates/changes/\\2/" + base + ".html\\3")
    else:
      replace_in_file(appcast,
        r"(<sparkle:releaseNotesLink xml:lang=\"" + lang + "\">)(?:" + package_name + \
        "-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + appcast_url + "/updates/changes/\\2/" + base + ".html\\3")
  replace_in_file(appcast,
                  r"(url=\")(?:.+/)(" + package_name + ".+\")",
                  "\\1" + appcast_url + "/updates/\\2")

  log("\n=== Delete unnecessary files\n")
  for file in os.listdir(updates_dir):
    if (-1 == file.find(app_version)) and (file.endswith(".zip") or
          file.endswith(".html")):
      delete_file(updates_dir + '/' + file)
  return

#
# Linux
#

def make_linux():
  utils.set_cwd("desktop-apps/win-linux/package/linux")

  rc = utils.cmd("make", "clean", verbose=True)
  common.summary["desktop clean"] = rc

  args = []
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../../../../" + common.branding + "/desktop-apps/win-linux/package/linux"]
  rc = utils.cmd("make", "packages", *args, verbose=True)
  common.summary["desktop build"] = rc

  utils.set_cwd(common.workspace_dir)
  return
