#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  if not (utils.is_windows() or utils.is_macos() or utils.is_linux()):
    utils.log("Unsupported host OS")
    return
  if "core" in common.targets:
    deploy_core()
  return

def deploy_core():
  if not common.deploy:
    return
  utils.log_h1("core deploy")
  common.summary["core deploy"] = 1

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  if common.platform.startswith("windows"):  platform = "windows"
  elif common.platform.startswith("darwin"): platform = "macos"
  elif common.platform.startswith("linux"):  platform = "linux"
  branch = utils.get_env("BRANCH_NAME")
  arch = common.platforms[common.platform]["arch"]
  if utils.is_windows():
    version = common.version + "." + common.build
  else:
    version = common.version + "-" + common.build
  src = "build_tools/out/%s/%s/core/core.7z" % (prefix, company)
  dest = "s3://" + common.s3_bucket + "/" + platform + "/core/" \
      + branch + "/%s/" + arch + "/"

  if branch is None:
    utils.log("BRANCH_NAME variable is empty")
    return

  ret = utils.win_command(
      "aws", "s3", "cp",
      "--acl", "public-read", "--no-progress",
      utils.get_path(src), dest % version,
      verbose=True
  )
  if ret == 0:
    ret = utils.win_command(
        "aws", "s3", "sync",
        "--delete", "--acl", "public-read", "--no-progress",
        dest % version, dest % "latest",
        verbose=True
    )
  common.summary["core deploy"] = ret
  return
