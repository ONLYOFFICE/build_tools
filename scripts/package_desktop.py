#!/usr/bin/env python

import base
import os
import re
import time
from jinja2 import Template
from package_utils import *
from package_branding import *

def make():
  set_cwd(desktop_dir)

  if ("windows" == system):
    make_windows()
  elif ("macos" == system):
    make_macos()
  elif ("linux" == system):
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
  global source_dir, package_name, package_version, arch, xp, sign, iscc_args, \
    vcredist_dir, \
    innosetup_file, advinst_file, portable_zip_file, update_innosetup_file

  set_cwd(build_dir)

  if ("clean" in targets):
    log("\nClean\n")
    delete_dir("data\\vcredist")
    delete_dir("DesktopEditors-cache")
    delete_files("*.exe")
    delete_files("*.msi")
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

    arch = get_arch(target)
    xp = get_xp(target)
    suffix = get_win_suffix(target)
    source_dir = "%s\\%s\\%s\\%s" % (out_dir, get_platform(target), company_name, product_name_s)

    if target.startswith("innosetup"):
      innosetup_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
      update_innosetup_file = "editors_update_%s.exe" % suffix
      update_appcast_file = "appcast.xml"
      update_changes_dir = "update\\changes\\" + version
      vcredist_dir = "data\\vcredist"

      for year in vcredist_list:
        download_vcredist(year)

      make_innosetup()

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
  xarch = ""
  xarch = "x86" if (arch == "32") else xarch
  xarch = "x64" if (arch == "64") else xarch
  path = "%s\\vcredist_%s_%s.exe" % (vcredist_dir, year, xarch)
  log("\nDownload vcredist " + year + "\n" + path + "\n")
  if base.is_file(path):
    log("! file exist, skip")
    return
  create_dir(vcredist_dir)
  download(vcredist_links[year][arch], path)
  return

def make_innosetup():
  log("\nBuild innosetup project\n" + innosetup_file + "\n")
  iscc_args = [
    "/Qp",
    # "/DsAppVersion=" + package_version,
    "/DsAppVerShort=" + version,
    "/DsAppBuildNumber=" + build,
    # "/DsBrandingFolder=" + branding_dir,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + arch
  ]
  if onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  if xp:
    iscc_args.append("/D_WIN_XP=1")
  if sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/S\"byparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " \\$f\"")

  if base.is_file(innosetup_file):
    log("! file exist")
    return
  cmd("iscc", iscc_args + ["common.iss"])
  return

def make_innosetup_update():
  log("\nBuild innosetup update project\n" + update_innosetup_file + "\n")
  if base.is_file(update_innosetup_file):
    log("! file exist")
    return
  cmd("iscc", iscc_args + ["/DTARGET_NAME=" + innosetup_file, "update_common.iss"])
  return

def make_winsparkle_files():
  log("Build winsparkle files")
  return

def make_advinst():
  log("\nBuild advanced installer project\n" + advinst_file + "\n")
  if base.is_file(advinst_file):
    log("! file exist")
    return
  xarch = ""
  xarch = "x86" if (arch == "32") else xarch
  xarch = "x64" if (arch == "64") else xarch
  advinst_exe = "AdvancedInstaller.com"
  advinst_args = ["/edit", "DesktopEditors.aip"]
  if arch is "32":
    cmd(advinst_exe, advinst_args + ["/SetPackageType", "x86"])
  if not sign:
    cmd(advinst_exe, advinst_args + ["/ResetSig"])
  cmd(advinst_exe, advinst_args + ["/AddOsLc", "-buildname", "DefaultBuild", "-arch", xarch])
  cmd(advinst_exe, advinst_args + ["/NewSync", "APPDIR", source_dir, "-existingfiles", "delete"])
  cmd(advinst_exe, advinst_args + ["/UpdateFile", "APPDIR\\DesktopEditors.exe", source_dir + "\\DesktopEditors.exe"])
  cmd(advinst_exe, advinst_args + ["/SetVersion", package_version])
  # cmd(advinst_exe, advinst_args + ["/SetOutputLocation", "-buildname", "DefaultBuild", "-path", ""])
  cmd(advinst_exe, advinst_args + ["/SetPackageName", advinst_file, "-buildname", "DefaultBuild"])
  cmd(advinst_exe, ["/rebuild", "DesktopEditors.aip", "-buildslist", "DefaultBuild"])
  return

def make_win_portable():
  log("\nBuild portable\n" + portable_zip_file + "\n")
  cmd("7z", ["a", "-y", portable_zip_file, source_dir + "\\*"])
  return
