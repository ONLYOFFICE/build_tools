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

def aws_s3_upload(files, key, ptype=None):
  if not files:
    return False
  ret = True
  key = "builder/" + key
  for file in files:
    args = ["aws"]
    if hasattr(branding, "s3_endpoint_url"):
      args += ["--endpoint-url=" + branding.s3_endpoint_url]
    args += [
      "s3", "cp", "--no-progress", "--acl", "public-read",
      file, "s3://" + branding.s3_bucket + "/" + key
    ]
    if common.os_family == "windows":
      upload = utils.cmd(*args, verbose=True)
    else:
      upload = utils.sh(" ".join(args), verbose=True)
    ret &= upload
    if upload and ptype is not None:
      full_key = key
      if full_key.endswith("/"): full_key += utils.get_basename(file)
      utils.add_deploy_data(
          "builder", ptype, file, full_key,
          branding.s3_bucket, branding.s3_region
      )
  return ret

def make_windows():
  global inno_file, zip_file, suffix, key_prefix
  utils.set_cwd("document-builder-package")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.builder_product_name.replace(" ","").lower()
  source_dir = "..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  package_name = company + "_" + product
  package_version = common.version + "." + common.build
  suffix = {
    "windows_x64": "x64",
    "windows_x86": "x86",
    "windows_x64_xp": "x64_xp",
    "windows_x86_xp": "x86_xp"
  }[common.platform]
  zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
  inno_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)

  if common.clean:
    utils.log_h2("builder clean")
    utils.delete_dir("build")

  utils.log_h2("copy arifacts")
  utils.create_dir("build\\app")
  utils.copy_dir_content(source_dir, "build\\app\\")

  make_zip()
  make_inno()

  utils.set_cwd(common.workspace_dir)
  return

def make_zip():
  utils.log_h2("builder zip build")
  utils.log_h3(zip_file)

  ret = utils.cmd("7z", "a", "-y", zip_file, ".\\app\\*",
      chdir="build", creates="build\\" + zip_file, verbose=True)
  utils.set_summary("builder zip build", ret)

  if common.deploy and ret:
    utils.log_h2("builder zip deploy")
    ret = aws_s3_upload(
        ["build\\" + zip_file], "win/generic/%s/" % common.channel, "Portable"
    )
    utils.set_summary("builder zip deploy", ret)
  return

def make_inno():
  utils.log_h2("builder inno build")
  utils.log_h3(inno_file)

  args = [
    "-Arch " + suffix,
    "-Version " + common.version,
    "-Build " + common.build
  ]
  if not branding.onlyoffice:
    args.append("-Branding '..\\..\\%s\\document-builder-package\\exe'" % common.branding)
  if common.sign:
    args.append("-Sign")
    args.append("-CertName '%s'" % branding.cert_name)
  ret = utils.ps1(
      ".\\make_inno.ps1", args, creates="build\\" + inno_file, verbose=True
  )
  utils.set_summary("builder inno build", ret)

  if common.deploy and ret:
    utils.log_h2("builder inno deploy")
    ret = aws_s3_upload(
        ["build\\" + inno_file], "win/inno/%s/" % common.channel, "Installer"
    )
    utils.set_summary("builder inno deploy", ret)
  return

def make_linux():
  utils.set_cwd("document-builder-package")

  utils.log_h2("builder build")
  make_args = branding.builder_make_targets
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("builder build", ret)

  rpm_arch = "x86_64"
  if common.platform == "linux_aarch64": rpm_arch = "aarch64"

  if common.deploy:
    utils.log_h2("builder deploy")
    if ret:
      if "tar" in branding.builder_make_targets:
        utils.log_h2("builder tar deploy")
        ret = aws_s3_upload(
            utils.glob_path("tar/*.tar.gz"),
            "linux/generic/%s/" % common.channel,
            "Portable"
        )
        utils.set_summary("builder tar deploy", ret)
      if "deb" in branding.builder_make_targets:
        utils.log_h2("builder deb deploy")
        ret = aws_s3_upload(
            utils.glob_path("deb/*.deb"),
            "linux/debian/%s/" % common.channel,
            "Debian"
        )
        utils.set_summary("builder deb deploy", ret)
      if "rpm" in branding.builder_make_targets:
        utils.log_h2("builder rpm deploy")
        ret = aws_s3_upload(
            utils.glob_path("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
            "linux/rhel/%s/" % common.channel,
            "CentOS"
        )
        utils.set_summary("builder rpm deploy", ret)
    else:
      if "tar" in branding.builder_make_targets:
        utils.set_summary("builder tar deploy", False)
      if "deb" in branding.builder_make_targets:
        utils.set_summary("builder deb deploy", False)
      if "rpm" in branding.builder_make_targets:
        utils.set_summary("builder rpm deploy", False)

  utils.set_cwd(common.workspace_dir)
  return
