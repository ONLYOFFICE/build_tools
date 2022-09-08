#!/usr/bin/env python
# -*- coding: utf-8 -*-

from package_utils import *
from package_branding import *

def make():
  if system == 'windows':
    make_windows()
  elif system == 'linux':
    if 'packages' in targets:
      set_cwd(build_dir)
      log("Clean")
      cmd("make", ["clean"])
      log("Build packages")
      cmd("make", ["packages"])
  else:
    exit(1)
  return

#
# Windows
#

def make_windows():
  global package_version, sign, machine, arch, source_dir, base_dir, \
    innosetup_file, portable_zip_file, isxdl_file
  base_dir = "base"
  isxdl_file = "exe/scripts/isxdl/isxdl.dll"

  set_cwd(get_abspath(git_dir, build_dir))

  if 'clean' in targets:
    log("\n=== Clean\n")
    delete_dir(base_dir)
    delete_files(isxdl_file)
    delete_files("exe/*.exe")
    delete_files("zip/*.zip")

  package_version = version + '.' + build
  sign = 'sign' in targets

  for target in targets:
    if not (target.startswith('innosetup') or target.startswith('portable')):
      continue

    machine = get_platform(target)['machine']
    arch = get_platform(target)['arch']
    suffix = arch
    source_prefix = "win_" + machine
    source_dir = get_path("%s/%s/%s/%s" % (out_dir, source_prefix, company_name_l, product_name_s))

    log("\n=== Copy arifacts\n")
    create_dir(base_dir)
    copy_dir_content(source_dir, base_dir + '\\')

    if target.startswith('innosetup'):
      download_isxdl()
      innosetup_file = "exe/%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

    if target.startswith('portable'):
      portable_zip_file = "zip/%s_%s_%s.zip" % (package_name, package_version, suffix)
      make_win_portable()
  return

def download_isxdl():
  log("\n=== Download isxdl\n")
  log("--- " + isxdl_file)
  if is_file(isxdl_file):
    log("! file exist, skip")
    return
  create_dir(get_dirname(isxdl_file))
  download_file(isxdl_link, isxdl_file)
  return

def make_innosetup():
  log("\n=== Build innosetup project\n")
  iscc_args = [
    "/Qp",
    "/DVERSION=" + package_version,
    "/DARCH=" + machine
  ]
  if not onlyoffice:
    iscc_args.append("/DBRANDING_DIR=" + get_abspath(git_dir, branding, build_dir, "exe"))
  if sign:
    iscc_args.append("/DSIGN")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " $f")
  log("--- " + innosetup_file)
  if is_file(innosetup_file):
    log("! file exist, skip")
    return
  set_cwd("exe")
  cmd("iscc", iscc_args + ["builder.iss"])
  set_cwd("..")
  return

def make_win_portable():
  log("\n=== Build portable\n")
  log("--- " + portable_zip_file)
  if is_file(portable_zip_file):
    log("! file exist, skip")
    return
  cmd("7z", ["a", "-y", portable_zip_file, get_path(base_dir, "*")])
  return
