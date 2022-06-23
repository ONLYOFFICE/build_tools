#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("builder")
  if utils.is_windows():
    make_windows()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported builder on host OS")
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
  if "windows_x64" == common.platform:   suffix = "x64"
  elif "windows_x86" == common.platform: suffix = "x86"
  zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
  inno_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)

  if common.clean:
    utils.log_h1("clean")
    utils.delete_dir("build")

  utils.log_h1("copy arifacts")
  utils.create_dir("build\\data")
  utils.copy_dir_content(source_dir, "build\\data\\")

  if "builder-zip" in common.targets:
    make_zip()

  if "builder-inno" in common.targets:
    make_inno()

  utils.set_cwd(common.workspace_dir)
  return

# def make_linux():
#   utils.set_cwd("document-builder-package")
#   utils.sh("make", "clean")
#   utils.sh("make", "packages")
#   utils.set_cwd(common.workspace_dir)
#   return

def make_zip():
  dest = "s3://" + common.s3_bucket + "/onlyoffice/experimental/windows/builder/" \
      + common.version + "/" + common.build + "/"

  common.summary["zip build"] = 1
  utils.log_h1("zip build " + zip_file)
  ret = utils.cmd("7z", "a", "-y", zip_file, "data\\*",
      chdir="build", creates="build\\" + zip_file, verbose=True)
  common.summary["zip build"] = ret

  common.summary["zip deploy"] = 1
  if ret == 0:
    utils.log_h1("zip deploy " + zip_file)
    ret = utils.cmd(
        "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
        "build\\" + zip_file, dest,
        verbose=True
    )
    common.summary["zip deploy"] = ret
  return

def make_inno():
  dest = "s3://" + common.s3_bucket + "/onlyoffice/experimental/windows/builder/" \
      + common.version + "/" + common.build + "/"

  common.summary["inno build"] = 1
  # if not common.deploy:
  #   common.summary["inno deploy"] = 1
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
  ret = utils.ps1("exe\\make.ps1", args, verbose=True)
  common.summary["inno build"] = ret

  common.summary["inno deploy"] = 1
  if ret == 0:
    utils.log_h1("inno deploy " + inno_file)
    ret = utils.cmd(
        "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
        "build\\" + inno_file, dest,
        verbose=True
    )
    common.summary["inno deploy"] = ret
  return
