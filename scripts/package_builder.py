#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("BUILDER")
  if utils.is_windows():
    make_windows()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported host OS")
  return

def make_windows():
  global inno_file, zip_file
  utils.set_cwd("document-builder-package")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.builder_product_name.replace(" ","").lower()
  source_dir = "..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  package_name = company + "_" + product
  package_version = common.version + "." + common.build
  suffixes = {
    "windows_x64": "x64",
    "windows_x86": "x86",
    "windows_x64_xp": "x64_xp",
    "windows_x86_xp": "x86_xp"
  }
  suffix = suffixes[common.platform]
  zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
  inno_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)

  if common.clean:
    utils.log_h1("clean")
    utils.delete_dir("build")

  utils.log_h1("copy arifacts")
  utils.create_dir("build\\app")
  utils.copy_dir_content(source_dir, "build\\app\\")

  # if "builder-zip" in common.targets:
  make_zip()
  # if "builder-inno" in common.targets:
  make_inno()

  utils.set_cwd(common.workspace_dir)
  return

def make_zip():
  common.summary["builder zip build"] = 1
  utils.log_h1("zip build " + zip_file)
  rc = utils.cmd("7z", "a", "-y", zip_file, ".\\app\\*",
      chdir="build", creates="build\\" + zip_file, verbose=True)
  common.summary["builder zip build"] = rc

  # common.summary["zip deploy"] = 1
  # if rc == 0:
  #   utils.log_h1("zip deploy " + zip_file)
  #   dest = "s3://" + common.s3_bucket + "/onlyoffice/experimental/windows/builder/" \
  #       + common.version + "/" + common.build + "/"
  #   rc = utils.cmd(
  #       "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
  #       "build\\" + zip_file, dest,
  #       verbose=True
  #   )
  #   common.summary["zip deploy"] = rc
  return

def make_inno():
  common.summary["builder inno build"] = 1
  utils.log_h1("inno build " + inno_file)
  # if utils.is_file(inno_file):
  #   utils.log("! file exist, skip")
  #   return
  args = ["-Version " + common.version, "-Build " + common.build]
  if not branding.onlyoffice:
    args.append("-Branding '..\\..\\%s\\document-builder-package\\exe'" % common.branding)
  if common.sign:
    args.append("-Sign")
    args.append("-CertName '%s'" % branding.cert_name)
  rc = utils.ps1(".\\make_inno.ps1", args,
      creates="build\\" + inno_file, verbose=True)
  common.summary["builder inno build"] = rc

  # common.summary["inno deploy"] = 1
  # if rc == 0:
  #   utils.log_h1("inno deploy " + inno_file)
  #   dest = "s3://" + common.s3_bucket + "/onlyoffice/experimental/windows/builder/" \
  #       + common.version + "/" + common.build + "/"
  #   rc = utils.cmd(
  #       "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
  #       "build\\" + inno_file, dest,
  #       verbose=True
  #   )
  #   common.summary["inno deploy"] = rc
  return

def make_linux():
  utils.set_cwd("document-builder-package")

  rc = utils.sh("make clean", verbose=True)
  common.summary["builder clean"] = rc

  args = []
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  rc = utils.sh("make packages " + " ".join(args), verbose=True)
  common.summary["builder build"] = rc

  utils.set_cwd(common.workspace_dir)
  return
