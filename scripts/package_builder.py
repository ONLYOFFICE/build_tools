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
  global package_version, machine, arch, source_dir, base_dir, \
    innosetup_file, portable_zip_file
  base_dir = "build/base"

  set_cwd(get_abspath(git_dir, build_dir))

  if clean:
    log("\n=== Clean\n")
    delete_dir("build")

  package_version = version + '.' + build

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
      innosetup_file = "build/exe/%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

    if target.startswith('portable'):
      portable_zip_file = "build/zip/%s_%s_%s.zip" % (package_name, package_version, suffix)
      make_win_portable()
  return

def make_innosetup():
  log("\n=== Build innosetup project\n")
  args = ["-Version " + version,
          "-Build " + build]
  if not onlyoffice:
    args.append("-Branding '" + get_abspath(git_dir, branding, build_dir, "exe") + "'")
  if sign:
    args.append("-Sign")
    args.append("-CertName '" + cert_name + "'")
  log("--- " + innosetup_file)
  if is_file(innosetup_file):
    log("! file exist, skip")
    return
  cmd("powershell", ["exe\\make.ps1"] + args)
  return

def make_win_portable():
  log("\n=== Build portable\n")
  log("--- " + portable_zip_file)
  if is_file(portable_zip_file):
    log("! file exist, skip")
    return
  cmd("7z", ["a", "-y", portable_zip_file, get_path(base_dir, "*")])
  return
