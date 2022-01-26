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

###############
### Windows ###
###############

def make_windows():
  global package_name, package_version, sign, machine, arch, xp, source_dir, \
    innosetup_file, innosetup_update_file, advinst_file, portable_zip_file, \
    iscc_args

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
      for year in vcredist_list:
        download_vcredist(year)

      innosetup_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

      if ("winsparkle-update" in targets):
        innosetup_update_file = "update\\editors_update_%s.exe" % suffix
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
  log("\n--- Download vcredist " + year + "\n")
  vcredist = "data\\vcredist\\vcredist_%s_%s.exe" % (year, arch)
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
  if branding:
    iscc_args.append("/DsBrandingFolder=" + desktop_branding_dir)
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
    "title": company_name + " " + product_name,
    "version": version,
    "build": build,
    "onlyoffice": onlyoffice,
    "timestamp": time.time()
  }
  update_appcast = "update\\appcast.xml"
  update_changes_dir = "update\\changes\\" + version
  log("-- " + update_appcast)
  if is_file(update_appcast):
    log("! file exist, skip")
  else:
    write_template(update_appcast + ".jinja", update_appcast, **template_vars)

  for lang, base in update_changes_list.items():
    update_changes = "update\\" + base + ".html"
    log("-- " + update_changes)
    if is_file(update_changes):
      log("! file exist, skip")
    else:
      template_vars["lang"] = lang
      write_template("update\\changes.html.jinja", update_changes, **template_vars)
  return

def make_advinst():
  log("\n--- Build advanced installer project\n")
  log("-- " + advinst_file)
  if is_file(advinst_file):
    log("! file exist, skip")
    return
  aic_content = [ ";aic" ]
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
  if machine is "32": aic_content.append("SetPackageType x86")
  aic_content += [
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "NewSync APPDIR " + source_dir + " -existingfiles delete",
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
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
  cmd("7z", ["a", "-y", portable_zip_file, source_dir + "\\*"])
  return
