#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base
import os
import re
import time
from package_utils import *
from package_branding import *

def make():
  if system == 'windows':
    make_windows()
  elif system == 'darwin':
    make_macos()
  elif system == 'linux':
    if 'packages' in targets:
      set_cwd(desktop_dir)
      log("Clean")
      base.cmd("make", ["clean"])
      log("Build packages")
      base.cmd("make", ["packages"])
  else:
    exit(1)
  return

#
# Windows
#

def make_windows():
  global package_name, package_version, sign, machine, arch, xp, source_dir, \
    innosetup_file, innosetup_update_file, advinst_file, portable_zip_file, \
    iscc_args

  set_cwd(get_abspath(git_dir, build_dir))

  if 'clean' in targets:
    log("\n--- Clean\n")
    delete_dir(get_path("data/vcredist"))
    delete_dir("DesktopEditors-cache")
    delete_files("*.exe")
    delete_files("*.msi")
    delete_files("*.aic")
    delete_files("*.tmp")
    delete_files("*.zip")
    delete_files(get_path("update/*.exe"))
    delete_files(get_path("update/*.xml"))
    delete_files(get_path("update/*.html"))

  package_name = company_name + '_' + product_name_s
  package_version = version + '.' + build
  sign = 'sign' in targets

  for target in targets:
    if not (target.startswith('innosetup') or target.startswith('advinst') or 
            target.startswith('portable')):
      continue

    machine = get_platform(target)['machine']
    arch = get_platform(target)['arch']
    xp = get_platform(target)['xp']
    suffix = arch + ("_xp" if xp else "")
    source_prefix = "win_" + machine + ("_xp" if xp else "")
    source_dir = get_path("%s/%s/%s/%s" % (out_dir, source_prefix, company_name_l, product_name_s))

    if target.startswith('innosetup'):
      for year in vcredist_list:
        download_vcredist(year)

      innosetup_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

      if 'winsparkle-update' in targets:
        innosetup_update_file = get_path("update/editors_update_%s.exe" % suffix)
        make_innosetup_update()

      if 'winsparkle-files' in targets:
        make_winsparkle_files()

    if target.startswith('advinst'):
      advinst_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)
      make_advinst()

    if target.startswith('portable'):
      portable_zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
      make_win_portable()

  return

def download_vcredist(year):
  log("\n--- Download vcredist " + year + "\n")
  vcredist = get_path("data/vcredist/vcredist_%s_%s.exe" % (year, arch))
  log("-- " + vcredist)
  if is_file(vcredist):
    log("! file exist, skip")
    return
  create_dir(get_dirname(vcredist))
  download_file(vcredist_links[year][machine], vcredist)
  return

def make_innosetup():
  log("\n--- Build innosetup project\n")
  global iscc_args
  iscc_args = [
    "/Qp",
    "/DsAppVersion=" + package_version,
    "/DsAppVerShort=" + version,
    "/DsAppBuildNumber=" + build,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + machine
  ]
  if onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=" + get_abspath(git_dir, branding_dir, "desktop-apps"))
  if xp:
    iscc_args.append("/D_WIN_XP=1")
  if sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " $f")
  log("-- " + innosetup_file)
  if is_file(innosetup_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["common.iss"])
  return

def make_innosetup_update():
  log("\n--- Build innosetup update project\n")
  log("-- " + innosetup_update_file)
  if is_file(innosetup_update_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["/DTARGET_NAME=" + innosetup_file, "update_common.iss"])
  return

def make_winsparkle_files():
  log("\n--- Build winsparkle files\n")
  template_vars = {
    "title": company_name + ' ' + product_name,
    "version": version,
    "build": build,
    "onlyoffice": onlyoffice,
    "timestamp": time.time()
  }
  update_appcast = get_path("update/appcast.xml")
  update_changes_dir = get_path("update/changes", version)
  log("-- " + update_appcast)
  if is_file(update_appcast):
    log("! file exist, skip")
  else:
    write_template(get_path("update/appcast.xml.jinja"), update_appcast, **template_vars)

  for lang, base in update_changes_list.items():
    update_changes = get_path("update/" + base + ".html")
    log("-- " + update_changes)
    if is_file(update_changes):
      log("! file exist, skip")
    else:
      template_vars["lang"] = lang
      write_template(get_path("update/changes.html.jinja"), update_changes, **template_vars)
  return

def make_advinst():
  log("\n--- Build advanced installer project\n")
  log("-- " + advinst_file)
  if is_file(advinst_file):
    log("! file exist, skip")
    return
  aic_content = [";aic"]
  if not onlyoffice:
    aic_content += [
      "SetProperty ProductName=\"%s\"" % ProductName,
      "SetProperty Manufacturer=\"%s\"" % Manufacturer,
      "SetProperty ARPURLINFOABOUT=\"%s\"" % ARPURLINFOABOUT,
      "SetProperty ARPURLUPDATEINFO=\"%s\"" % ARPURLUPDATEINFO,
      "SetProperty ARPHELPLINK=\"%s\"" % ARPHELPLINK,
      "SetProperty ARPHELPTELEPHONE=\"%s\"" % ARPHELPTELEPHONE,
      "SetProperty ARPCONTACT=\"%s\"" % ARPCONTACT,
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
  if not sign:        aic_content.append("ResetSig")
  if machine == '32': aic_content.append("SetPackageType x86")
  aic_content += [
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "NewSync APPDIR " + source_dir + " -existingfiles delete",
    "UpdateFile APPDIR\\DesktopEditors.exe " + get_path(source_dir, "DesktopEditors.exe"),
    "SetVersion " + package_version,
    "SetPackageName " + advinst_file + " -buildname DefaultBuild",
    "Rebuild -buildslist DefaultBuild"
  ]
  write_file("DesktopEditors.aic", "\n".join(aic_content))
  cmd("AdvancedInstaller.com", ["/execute", "DesktopEditors.aip", "DesktopEditors.aic", "-nofail"])
  return

def make_win_portable():
  log("\n--- Build portable\n")
  log("-- " + portable_zip_file)
  if is_file(portable_zip_file):
    log("! file exist, skip")
    return
  cmd("7z", ["a", "-y", portable_zip_file, get_path(source_dir, "*")])
  return

#
# macOS
#

def make_macos():
  for target in targets:
    if not target.startswith('diskimage'):
      continue

    if target.startswith('diskimage'):
      make_diskimage(target)

      if ('sparkle-updates' in targets):
        make_sparkle_updates()
  return

def make_diskimage(target):
  global suffix
  if   (target == 'diskimage-x64'):    suffix = 'x86_64'
  elif (target == 'diskimage-x64-v8'): suffix = 'v8'
  elif (target == 'diskimage-arm64'):  suffix = 'arm'
  else: exit(1)
  lane = "release_" + suffix
  scheme = package_name + '-' + suffix
  log("\n--- Build package " + scheme + "\n")
  log("$ bundler exec fastlane " + lane + " skip_git_bump:true")
  cmd("bundler", ["exec", "fastlane", lane, "skip_git_bump:true"])
  return

def make_sparkle_updates():
  log("\n--- Build sparkle updates\n")

  app_version = cmd("/usr/libexec/PlistBuddy \
    -c 'print :CFBundleShortVersionString' \
    build/" + package_name + ".app/Contents/Info.plist")['stdout']
  zip_filename = scheme + '-' + app_version
  macos_zip = "build/" + zip_filename + ".zip"
  updates_storage_dir = get_env('ARCHIVES_DIR') + '/' + scheme + "/_updates"
  create_dir(updates_dir)
  copy_dir_content(update_storage_dir, updates_dir, ".zip")
  copy_dir_content(update_storage_dir, updates_dir, ".html")
  copy_file(macos_zip, updates_dir)
  for lang, base in update_changes_list.items():
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, base)
    notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
    if   lang == 'en': encoding = 'en_US.UTF-8'
    elif lang == 'ru': encoding = 'ru_RU.UTF-8'
    cur_date = cmd("LC_ALL=%s date -u \"%s\"" % (lang, encoding))['stdout']
    if is_file(notes_src):
      copy_file(notes_src, notes_dst)
      replaceInFileRE(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    #else:
    #  write_file(notes_dst, "placeholder\n")
  log("$ ./generate_appcast " + updates_dir)
  cmd(desktop_dir + "/Vendor/Sparkle/bin/generate_appcast", [updates_dir])

  log("Edit Sparkle appcast links")
  sparkle_base_url += '/' + suffix
  update_appcast = "%s/%s.xml" % (updates_dir, company_name.lower())
  if (list(update_changes_list.values())[0] is not None):
    replaceInFileRE(update_appcast,
                    r("(<sparkle:releaseNotesLink>)(?:.+" + company_name + "-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)"),
                    "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotes.html\\3")
  if (list(update_changes_list.values())[1] is not None):
    replaceInFileRE(update_appcast,
                    r"(<sparkle:releaseNotesLink xml:lang=\"ru\">)(?:" + company_name + "-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
                    "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotesRU.html\\3")
  replaceInFileRE(update_appcast,
                  r"(url=\")(?:.+/)(" + company_name + ".+\")",
                  "\\1" + sparkle_base_url + "/updates/\\2")

  log("Delete unnecessary files")
  for file in os.listdir(updates_dir):
    if (-1 == file.find(app_version)) and (file.endswith(".zip") or
          file.endswith(".html")):
      base.delete_file(updates_dir + '/' + file)
  return
