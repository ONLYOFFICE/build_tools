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

def aws_s3_upload(local, key, ptype = None):
  if common.os_family == "windows":
    rc = utils.cmd(
        "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
        local, "s3://" + common.s3_bucket + "/" + key,
        verbose=True
    )
  else:
    rc = utils.sh("aws s3 cp --acl public-read --no-progress " \
        + local + " s3://" + common.s3_bucket + "/" + key, verbose=True)
  if rc == 0 and ptype is not None:
    utils.add_deploy_data("builder", ptype, local, key)
  return rc

def make_windows():
  global inno_file, zip_file, key_prefix
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
  key_prefix = "%s/%s/windows/builder/%s/%s" % (branding.company_name_l, \
      common.release_branch, common.version, common.build)

  if common.clean:
    utils.log_h2("builder clean")
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
  utils.log_h2("builder zip build")
  utils.log_h2(zip_file)
  rc = utils.cmd("7z", "a", "-y", zip_file, ".\\app\\*",
      chdir="build", creates="build\\" + zip_file, verbose=True)
  utils.set_summary("builder zip build", rc == 0)

  if rc == 0:
    utils.log_h2("builder zip deploy")
    zip_key = key_prefix + "/" + zip_file
    rc = aws_s3_upload("build\\" + zip_file, zip_key, "Portable")
  utils.set_summary("builder zip deploy", rc == 0)
  return

def make_inno():
  utils.log_h2("builder inno build")
  utils.log_h2(inno_file)
  args = ["-Version " + common.version, "-Build " + common.build]
  if not branding.onlyoffice:
    args.append("-Branding '..\\..\\%s\\document-builder-package\\exe'" % common.branding)
  if common.sign:
    args.append("-Sign")
    args.append("-CertName '%s'" % branding.cert_name)
  rc = utils.ps1(".\\make_inno.ps1", args,
      creates="build\\" + inno_file, verbose=True)
  utils.set_summary("builder inno build", rc == 0)

  if rc == 0:
    utils.log_h2("builder inno deploy")
    inno_key = key_prefix + "/" + inno_file
    rc = aws_s3_upload("build\\" + inno_file, inno_key, "Installer")
  utils.set_summary("builder inno deploy", rc == 0)
  return

def make_linux():
  utils.set_cwd("document-builder-package")

  utils.log_h2("builder clean")
  rc = utils.sh("make clean", verbose=True)
  utils.set_summary("builder clean", rc == 0)

  utils.log_h2("builder build")
  args = []
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  rc = utils.sh("make packages " + " ".join(args), verbose=True)
  utils.set_summary("builder build", rc == 0)

  key_prefix = branding.company_name_l + "/" + common.release_branch
  if rc == 0:
    utils.log_h2("builder tar deploy")
    tar_file = utils.glob_file("tar/*.tar.gz")
    tar_key = key_prefix + "/linux/" + utils.get_basename(tar_file)
    rc = aws_s3_upload(tar_file, tar_key, "Portable")
    utils.set_summary("builder tar deploy", rc == 0)

    utils.log_h2("builder deb deploy")
    deb_file = utils.glob_file("deb/*.deb")
    deb_key = key_prefix + "/ubuntu/" + utils.get_basename(deb_file)
    rc = aws_s3_upload(deb_file, deb_key, "Ubuntu")
    utils.set_summary("builder deb deploy", rc == 0)

    utils.log_h2("builder rpm deploy")
    rpm_file = utils.glob_file("rpm/**/*.rpm")
    rpm_key = key_prefix + "/centos/" + utils.get_basename(rpm_file)
    rc = aws_s3_upload(rpm_file, rpm_key, "CentOS")
    utils.set_summary("builder rpm deploy", rc == 0)

  else:
    utils.set_summary("builder tar deploy", False)
    utils.set_summary("builder deb deploy", False)
    utils.set_summary("builder rpm deploy", False)

  utils.set_cwd(common.workspace_dir)
  return
