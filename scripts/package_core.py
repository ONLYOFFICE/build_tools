#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  if len([t for t in common.targets if t.startswith("core")]):
    utils.log_h1("CORE")
  else:
    return

  if not (utils.is_windows() or utils.is_macos() or utils.is_linux()):
    utils.log("Unsupported host OS")
    return

  deploy_core()
  return

def deploy_core():
  if not common.deploy:
    return

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  if common.platform.startswith("windows"):  platform = "windows"
  elif common.platform.startswith("darwin"): platform = "macos"
  elif common.platform.startswith("linux"):  platform = "linux"
  branch = utils.get_env("BRANCH_NAME")
  if branch is None:
    utils.log("BRANCH_NAME variable is undefined")
    return
  arch = common.platforms[common.platform]["arch"]
  if utils.is_windows():
    version = common.version + "." + common.build
  else:
    version = common.version + "-" + common.build
  src = "build_tools/out/%s/%s/core/core.7z" % (prefix, company)
  dest = common.s3_bucket + "/" + platform + "/core/" \
      + branch + "/%s/" + arch + "/"

  utils.log_h1("core deploy")
  common.summary["core deploy"] = 1
  ret = utils.cmd(
      "aws", "s3", "cp",
      "--acl", "public-read", "--no-progress",
      utils.get_path(src), "s3://" + dest % version,
      verbose=True
  )
  if ret == 0:
    common.deploy_list.append({
      "product": "core",
      "platform": common.platform,
      "section": "Archive",
      "path": dest % version + "core.7z",
      "size": utils.get_file_size(utils.get_path(src))
    })
    ret = utils.cmd(
        "aws", "s3", "sync",
        "--delete", "--acl", "public-read", "--no-progress",
        "s3://" + dest % version, "s3://" + dest % "latest",
        verbose=True
    )
  common.summary["core deploy"] = ret
  return
