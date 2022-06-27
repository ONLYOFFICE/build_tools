#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("CORE")
  if not (utils.is_windows() or utils.is_macos() or utils.is_linux()):
    utils.log("Unsupported host OS")
    return
  if common.deploy:
    make_core()
  return

def make_core():
  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  repos = {
    "windows": "windows",
    "darwin": "mac",
    "linux": "linux"
  }
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
  dest = common.s3_bucket + "/" + repos[common.os_family] + "/core/" \
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
