#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

# the edition is a key of branding.server_editions, its make arguments per host os
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

def get_branding_args():
  package_dir = utils.get_branding_package_dir("document-server-package")
  if not package_dir:
    return []
  return ["-e", "BRANDING_DIR=../" + package_dir,
          "-e", "BRANDING=" + common.branding]

def make_windows(edition):
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " build")
  ret = utils.cmd("make", "clean", verbose=True)
  make_args = list(branding.server_editions[edition]["windows"])
  make_args += get_branding_args()
  ret &= utils.cmd("make", *make_args, verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("server " + edition + " inno deploy")
    ret = s3_upload(utils.glob_path("exe/*.exe"), "server/win/inno/")
    utils.set_summary("server " + edition + " inno deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return

def make_linux(edition):
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " build")
  make_args = [t["make"] for t in branding.server_make_targets]
  make_args += branding.server_editions[edition]["linux"]
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  make_args += get_branding_args()
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  if common.deploy:
    for t in branding.server_make_targets:
      utils.log_h2("server " + edition + " " + t["make"] + " deploy")
      ret = s3_upload(utils.glob_path(t["src"]), t["dst"])
      utils.set_summary("server " + edition + " " + t["make"] + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
