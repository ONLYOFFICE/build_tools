#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("BUILDER")
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported host OS")
  return

def s3_upload(files, dst):
  if not files: return False
  ret = True
  for f in files:
    key = dst + utils.get_basename(f) if dst.endswith("/") else dst
    aws_kwargs = { "acl": "public-read" }
    if hasattr(branding, "s3_endpoint_url"):
      aws_kwargs["endpoint_url"] = branding.s3_endpoint_url
    upload = utils.s3_upload(
      f, "s3://" + branding.s3_bucket + "/" + key, **aws_kwargs)
    if upload:
      utils.add_deploy_data(key)
      utils.log("URL: " + branding.s3_base_url + "/" + key)
    ret &= upload
  return ret

def make_windows():
  global inno_file, zip_file, suffix, key_prefix
  utils.set_cwd("document-builder-package")

  prefix = common.platformPrefixes[common.platform]
  company = branding.company_name
  product = branding.builder_product_name.replace(" ","")
  source_dir = "..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  package_name = company + "-" + product
  package_version = common.version + "." + common.build
  suffix = {
    "windows_x64": "x64",
    "windows_x86": "x86"
  }[common.platform]
  zip_file = "%s-%s-%s-%s.zip" % (company, product, package_version, suffix)
  inno_file = "%s-%s-%s-%s.exe" % (company, product, package_version, suffix)

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
    ret = s3_upload(["build\\" + zip_file], "builder/win/generic/")
    utils.set_summary("builder zip deploy", ret)
  return

def make_inno():
  utils.log_h2("builder inno build")
  utils.log_h3(inno_file)

  args = [
    "-Arch", suffix,
    "-Version", common.version,
    "-Build", common.build
  ]
  if not branding.onlyoffice:
    args += [
      "-Branding", "%s\\%s\\document-builder-package\\exe" % (common.workspace_dir, common.branding)
    ]
  if common.sign:
    args += [
      "-Sign",
      "-CertName", branding.cert_name
    ]
  ret = utils.ps1(
      "make_inno.ps1", args, creates="build\\" + inno_file, verbose=True
  )
  utils.set_summary("builder inno build", ret)

  if common.deploy and ret:
    utils.log_h2("builder inno deploy")
    ret = s3_upload(["build\\" + inno_file], "builder/win/inno/")
    utils.set_summary("builder inno deploy", ret)
  return

def make_macos():
  company = branding.company_name.lower()
  product = branding.builder_product_name.replace(" ","").lower()
  source_dir = "build_tools/out/%s/%s/%s" % (common.prefix, company, product)
  arch_list = {
    "darwin_x86_64": "x86_64",
    "darwin_arm64": "arm64"
  }
  suffix = arch_list[common.platform]
  builder_tar = "../%s-%s-%s-%s-%s.tar.xz" % \
    (company, product, common.version, common.build, suffix)

  utils.set_cwd(source_dir)

  if common.clean:
    utils.log_h2("builder clean")
    utils.delete_files("../*.tar*")

  utils.log_h2("builder build")
  ret = utils.sh("tar --xz -cvf %s *" % builder_tar, creates=builder_tar, verbose=True)
  utils.set_summary("builder build", ret)

  if common.deploy and ret:
    utils.log_h2("builder deploy")
    ret = s3_upload([builder_tar], "builder/mac/")
    utils.set_summary("builder deploy", ret)

  utils.set_cwd(common.workspace_dir)
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

  if common.deploy:
    if ret:
      if "tar" in branding.builder_make_targets:
        utils.log_h2("builder tar deploy")
        ret = s3_upload(
          utils.glob_path("tar/*.tar.gz"),
          "builder/linux/generic/")
        utils.set_summary("builder tar deploy", ret)
      if "deb" in branding.builder_make_targets:
        utils.log_h2("builder deb deploy")
        ret = s3_upload(
          utils.glob_path("deb/*.deb"),
          "builder/linux/debian/")
        utils.set_summary("builder deb deploy", ret)
      if "rpm" in branding.builder_make_targets:
        utils.log_h2("builder rpm deploy")
        ret = s3_upload(
          utils.glob_path("rpm/builddir/RPMS/*/*.rpm"),
          "builder/linux/rhel/")
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
