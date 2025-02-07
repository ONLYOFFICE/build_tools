#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("BUILDER")
  if not (utils.is_windows() or utils.is_macos() or utils.is_linux()):
    utils.log("Unsupported host OS")
    return
  if common.deploy:
    make_archive()
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  return

def s3_upload(files, dst):
  if not files: return False
  ret = True
  for f in files:
    key = dst + utils.get_basename(f) if dst.endswith("/") else dst
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
    ret &= upload
  return ret

def make_archive():
  utils.set_cwd(utils.get_path(
    "build_tools/out/" + common.prefix + "/" + branding.company_name.lower()))

  utils.log_h2("builder archive build")
  utils.delete_file("builder.7z")
  args = ["7z", "a", "-y", "builder.7z", "./documentbuilder/*"]
  if utils.is_windows():
    ret = utils.cmd(*args, verbose=True)
  else:
    ret = utils.sh(" ".join(args), verbose=True)
  utils.set_summary("builder archive build", ret)

  utils.log_h2("builder archive deploy")
  dest = "builder-" + common.prefix.replace("_","-") + ".7z"
  dest_latest = "archive/%s/latest/%s" % (common.branch, dest)
  dest_version = "archive/%s/%s/%s" % (common.branch, common.build, dest)
  ret = utils.s3_upload(
    "builder.7z", "s3://" + branding.s3_bucket + "/" + dest_version)
  utils.set_summary("builder archive deploy", ret)
  if ret:
    utils.log("URL: " + branding.s3_base_url + "/" + dest_version)
    utils.s3_copy(
      "s3://" + branding.s3_bucket + "/" + dest_version,
      "s3://" + branding.s3_bucket + "/" + dest_latest)
    utils.log("URL: " + branding.s3_base_url + "/" + dest_latest)

  utils.set_cwd(common.workspace_dir)
  return

def make_windows():
  global package_version, arch
  utils.set_cwd("document-builder-package")

  package_version = common.version + "." + common.build
  arch = {
    "windows_x64": "x64",
    "windows_x86": "x86"
  }[common.platform]

  if common.clean:
    utils.log_h2("builder clean")
    utils.delete_dir("build")
    utils.delete_files("exe\\*.exe")
    utils.delete_files("zip\\*.msi")

  if make_prepare():
    make_zip()
    make_inno()
  else:
    utils.set_summary("builder zip build", False)
    utils.set_summary("builder inno build", False)

  utils.set_cwd(common.workspace_dir)
  return

def make_prepare():
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("builder prepare")
  ret = utils.ps1("make.ps1", args, verbose=True)
  utils.set_summary("builder prepare", ret)
  return ret

def make_zip():
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  # if common.sign:
  #   args += ["-Sign"]

  utils.log_h2("builder zip build")
  ret = utils.ps1("make_zip.ps1", args, verbose=True)
  utils.set_summary("builder zip build", ret)

  if common.deploy and ret:
    utils.log_h2("builder zip deploy")
    ret = s3_upload(utils.glob_path("zip/*.zip"), "builder/win/generic/")
    utils.set_summary("builder zip deploy", ret)
  return

def make_inno():
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  if not branding.onlyoffice:
    args += ["-Branding", common.branding]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("builder inno build")
  ret = utils.ps1("make_inno.ps1", args, verbose=True)
  utils.set_summary("builder inno build", ret)

  if common.deploy and ret:
    utils.log_h2("builder inno deploy")
    ret = s3_upload(utils.glob_path("exe/*.exe"), "builder/win/inno/")
    utils.set_summary("builder inno deploy", ret)
  return

def make_macos():
  utils.set_cwd("document-builder-package")

  utils.log_h2("builder tar build")
  make_args = ["tar"]
  if common.platform == "darwin_arm64":
    make_args += ["-e", "UNAME_M=arm64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("builder tar build", ret)

  if common.deploy:
    utils.log_h2("builder tar deploy")
    ret = s3_upload(utils.glob_path("tar/*.tar.xz"), "builder/mac/generic/")
    utils.set_summary("builder tar deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return

def make_linux():
  utils.set_cwd("document-builder-package")

  utils.log_h2("builder build")
  make_args = [t["make"] for t in branding.builder_make_targets]
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("builder build", ret)

  if common.deploy:
    for t in branding.builder_make_targets:
      utils.log_h2("builder " + t["make"] + " deploy")
      ret = s3_upload(utils.glob_path(t["src"]), t["dst"])
      utils.set_summary("builder " + t["make"] + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
