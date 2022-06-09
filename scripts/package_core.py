#!/usr/bin/env python

# import os
import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  else:
    exit("Unknown host os")
  return

def make_windows():
  for target in common.targets:
    if target in ["core-x64", "core-x86"]:
      deploy_core(target, "windows")
  return

def make_macos():
  for target in common.targets:
    if target in ["core-x86_64"]:
      deploy_core(target, "macos")
  return

def make_linux():
  for target in common.targets:
    if target in ["core-x86_64"]:
      deploy_core(target, "linux")
  return

def deploy_core(target, platform):
  task = target + " deploy"
  common.summary[task] = 1
  utils.log_h1(task)

  prefix = branding.packages[platform][target]["prefix"]
  company = branding.company_name.lower()
  branch = utils.get_env("BRANCH_NAME")
  version = common.version + "." + common.build
  arch = branding.packages[platform][target]["arch"]
  src = "build_tools/out/%s/%s/core/core.7z"
  dest = "s3://" + common.s3_bucket + "/%s/core/%s/%s/%s/"

  if branch is None:
    utils.log("BRANCH_NAME variable is empty")
    return

  ret = utils.win_command(
      "aws", "s3", "cp",
      "--acl", "public-read",
      "--no-progress",
      utils.get_path(src % (prefix, company)),
      dest % (platform, branch, version, arch),
      verbose=True
  )
  if ret == 0:
    ret = utils.win_command(
        "aws", "s3", "sync",
        "--delete",
        "--acl", "public-read",
        "--no-progress",
        dest % (platform, branch, version, arch),
        dest % (platform, branch, "latest", arch),
        verbose=True
    )
  common.summary[task] = ret
  return
