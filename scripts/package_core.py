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
  prefix = common.platformPrefixes[common.platform]
  company = branding.company_name.lower()
  repos = {
    "windows_x64":   { "repo": "windows", "arch": "x64", "version": common.version + "." + common.build },
    "windows_x86":   { "repo": "windows", "arch": "x86", "version": common.version + "." + common.build },
    "darwin_x86_64": { "repo": "mac",     "arch": "x64", "version": common.version + "-" + common.build },
    "darwin_arm64":  { "repo": "mac",     "arch": "arm", "version": common.version + "-" + common.build },
    "linux_x86_64":  { "repo": "linux",   "arch": "x64", "version": common.version + "-" + common.build },
  }
  repo = repos[common.platform]
  branch = utils.get_env("BRANCH_NAME")
  core_7z = utils.get_path("build_tools/out/%s/%s/core.7z" % (prefix, company))
  dest_version = "%s/core/%s/%s/%s" % (repo["repo"], branch, repo["version"], repo["arch"])
  dest_latest = "%s/core/%s/%s/%s" % (repo["repo"], branch, "latest", repo["arch"])

  if branch is None:
    utils.log_err("BRANCH_NAME variable is undefined")
    utils.set_summary("core deploy", False)
    return
  if not utils.is_file(core_7z):
    utils.log_err("file not exist: " + core_7z)
    utils.set_summary("core deploy", False)
    return

  utils.log_h2("core deploy")
  aws_kwargs = { "acl": "public-read" }
  if hasattr(branding, "s3_endpoint_url"):
    aws_kwargs["endpoint_url"]=branding.s3_endpoint_url
  ret = utils.s3_upload(
    core_7z,
    "s3://" + branding.s3_bucket + "/" + dest_version + "/core.7z",
    **aws_kwargs)
  if ret:
    utils.log("URL: " + branding.s3_base_url + "/" + dest_version + "/core.7z")
    utils.add_deploy_data(dest_version + "/core.7z")
    ret = utils.s3_sync(
      "s3://" + branding.s3_bucket + "/" + dest_version + "/",
      "s3://" + branding.s3_bucket + "/" + dest_latest + "/",
      delete=True, **aws_kwargs)
    utils.log("URL: " + branding.s3_base_url + "/" + dest_latest + "/core.7z")
  utils.set_summary("core deploy", ret)
  return

def deploy_closuremaps(license):
  if not common.deploy: return
  utils.log_h1("CLOSURE MAPS")
  utils.set_cwd(utils.get_path("sdkjs/build/maps"))

  maps = utils.glob_path("*.js.map")
  if not maps:
    utils.log_err("files do not exist")
    utils.set_summary("closure maps " + license + " deploy", False)
    return

  utils.log_h2("closure maps " + license + " deploy")
  aws_kwargs = {}
  if hasattr(branding, "s3_endpoint_url"):
    aws_kwargs["endpoint_url"]=branding.s3_endpoint_url
  ret = True
  for f in maps:
    key = "closure-maps/%s/%s/%s/%s" % (license, common.version, common.build, f)
    upload = utils.s3_upload(
      f, "s3://" + branding.s3_bucket + "/" + key, **aws_kwargs)
    ret &= upload
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
      utils.add_deploy_data(key)
  utils.set_summary("closure maps " + license + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
