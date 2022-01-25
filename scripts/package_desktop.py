#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base
import os
import re
import time
from package_utils import *
from package_branding import *

def make():
  set_cwd(desktop_dir)

  if (system == "windows"):
    make_windows()
  elif (system == "darwin"):
    make_macos()
  elif (system == "linux"):
    if ("packages" in targets):
      set_cwd(desktop_dir)
      log("Clean")
      base.cmd("make", ["clean"])
      log("Build packages")
      base.cmd("make", ["packages"])
  else:
    exit(1)
  return

def make_windows():
  global package_name, package_version, sign, machine, arch, xp, source_dir, \
    innosetup_file, advinst_file, portable_zip_file, update_innosetup_file, \
    vcredist_dir, iscc_args

  set_cwd(build_dir)

  if ("clean" in targets):
    log("\n--- Clean\n")
    delete_dir("data\\vcredist")
    delete_dir("DesktopEditors-cache")
    delete_files("*.exe")
    delete_files("*.msi")
    delete_files("*.aic")
    delete_files("*.tmp")
    delete_files("*.zip")
    delete_files("update\\*.exe")
    delete_files("update\\*.xml")
    delete_files("update\\*.html")

  package_name = company_name + "_" + product_name_s
  package_version = version + "." + build
  sign = "sign" in targets

  for target in targets:
    if not (target.startswith("innosetup") or target.startswith("advinst") or target.startswith("portable")):
      continue

    machine = get_platform(target)["machine"]
    arch = get_platform(target)["arch"]
    xp = get_platform(target)["xp"]
    suffix = arch + ("_xp" if xp else "")
    source_prefix = "win_" + machine + ("_xp" if xp else "")
    source_dir = "%s\\%s\\%s\\%s" % (out_dir, source_prefix, company_name_l, product_name_s)

    if target.startswith("innosetup"):
      vcredist_dir = "data\\vcredist"
      for year in vcredist_list:
        download_vcredist(year)

      innosetup_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

      update_innosetup_file = "editors_update_%s.exe" % suffix
      update_appcast_file = "appcast.xml"
      update_changes_dir = "update\\changes\\" + version

      if ("winsparkle-update" in targets):
        make_innosetup_update()

      if ("winsparkle-files" in targets):
        make_winsparkle_files()

    if target.startswith("advinst"):
      advinst_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)
      make_advinst()

    if target.startswith("portable"):
      portable_zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
      make_win_portable()

  return

def download_vcredist(year):
  path = "%s\\vcredist_%s_%s.exe" % (vcredist_dir, year, arch)
  log("\n--- Download vcredist " + year + "\n--- " + path + "\n")
  if is_file(path):
    log("! file exist, skip")
    return
  create_dir(vcredist_dir)
  download(vcredist_links[year][machine], path)
  return

def make_innosetup():
  log("\n--- Build innosetup project\n--- " + innosetup_file + "\n")
  global iscc_args
  iscc_args = [
    "/Qp",
    # "/DsAppVersion=" + package_version,
    "/DsAppVerShort=" + version,
    "/DsAppBuildNumber=" + build,
    # "/DsBrandingFolder=" + branding_dir,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + machine
  ]
  if onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  if xp:
    iscc_args.append("/D_WIN_XP=1")
  if sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " $f")
  if is_file(innosetup_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["common.iss"])
  return

def make_innosetup_update():
  log("\n--- Build innosetup update project\n--- update\\" + update_innosetup_file + "\n")
  if is_file("update\\" + update_innosetup_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["/DTARGET_NAME=" + innosetup_file, "update_common.iss"])
  return

def make_winsparkle_files():
  log("Build winsparkle files")
  return

def make_advinst():
  log("\n--- Build advanced installer project\n--- " + advinst_file + "\n")
  if is_file(advinst_file):
    log("! file exist, skip")
    return
  aic_content = [
    ";aic",
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "NewSync APPDIR " + source_dir + " -existingfiles delete",
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
    "SetVersion " + package_version,
    "SetPackageName " + advinst_file + " -buildname DefaultBuild",
    "Rebuild"
  ]
  if not sign:        aic_content.insert(1, "ResetSig")
  if machine is "32": aic_content.insert(1, "SetPackageType x86")
  write_file("DesktopEditors.aic", "\n".join(aic_content))
  cmd("AdvancedInstaller.com", ["/execute", "DesktopEditors.aip", "DesktopEditors.aic", "-nofail"])
  return

def make_win_portable():
  log("\n--- Build portable\n--- " + portable_zip_file + "\n")
  if is_file(portable_zip_file):
    log("! file exist, skip")
    return
  cmd("7z", ["a", "-y", portable_zip_file, source_dir + "\\*"])
  return
