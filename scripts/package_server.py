#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make(edition):
  utils.log_h1("SERVER (" + edition.upper() + ")")
  if utils.is_windows():
    make_windows(edition)
  elif utils.is_linux():
    make_linux(edition)
  else:
    utils.log("Unsupported host OS")
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

def make_windows(edition):
  if edition == "enterprise":
    product_name = "DocumentServer-EE"
  elif edition == "developer":
    product_name = "DocumentServer-DE"
  else:
    product_name = "DocumentServer"
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " build")
  ret = utils.cmd("make", "clean", verbose=True)
  if edition == "prerequisites":
    make_args = ["exe-pr"]
  else:
    make_args = ["exe", "-e", "PRODUCT_NAME=" + product_name]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  ret &= utils.cmd("make", *make_args, verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("server " + edition + " inno deploy")
    ret = s3_upload(utils.glob_path("exe/*.exe"), "server/win/inno/")
    utils.set_summary("server " + edition + " inno deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return

def make_linux(edition):
  if edition == "enterprise":
    product_name = "documentserver-ee"
  elif edition == "developer":
    product_name = "documentserver-de"
  else:
    product_name = "documentserver"
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " build")
  make_args = [t["make"] for t in branding.server_make_targets]
  make_args += ["-e", "PRODUCT_NAME=" + product_name]
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  if common.deploy:
    for t in branding.server_make_targets:
      utils.log_h2("server " + edition + " " + t["make"] + " deploy")
      ret = s3_upload(utils.glob_path(t["src"]), t["dst"])
      utils.set_summary("server " + edition + " " + t["make"] + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
