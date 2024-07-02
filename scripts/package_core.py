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
  ret = utils.s3_upload(
    core_7z,
    "s3://" + branding.s3_bucket + "/" + dest_version + "/core.7z")
  if ret:
    utils.log("URL: " + branding.s3_base_url + "/" + dest_version + "/core.7z")
    utils.add_deploy_data(dest_version + "/core.7z")
    ret = utils.s3_sync(
      "s3://" + branding.s3_bucket + "/" + dest_version + "/",
      "s3://" + branding.s3_bucket + "/" + dest_latest + "/",
      delete=True)
    utils.log("URL: " + branding.s3_base_url + "/" + dest_latest + "/core.7z")
  utils.set_summary("core deploy", ret)
  return

def deploy_closuremaps_sdkjs(license):
  if not common.deploy: return
  utils.log_h1("SDKJS CLOSURE MAPS")

  maps = utils.glob_path("sdkjs/build/maps/*.js.map")
  if maps:
    for m in maps: utils.log("- " + m)
  else:
    utils.log_err("files do not exist")
    utils.set_summary("sdkjs closure maps %s deploy" % license, False)
    return

  utils.log_h2("sdkjs closure maps %s deploy" % license)
  ret = True
  for f in maps:
    base = utils.get_basename(f)
    key = "closure-maps/sdkjs/%s/%s/%s/%s" % (license, common.version, common.build, base)
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    ret &= upload
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
      utils.add_deploy_data(key)
  utils.set_summary("sdkjs closure maps %s deploy" % license, ret)
  return

def deploy_closuremaps_webapps(license):
  if not common.deploy: return
  utils.log_h1("WEB-APPS CLOSURE MAPS")

  maps = utils.glob_path("web-apps/deploy/web-apps/apps/*/*/*.js.map") \
       + utils.glob_path("web-apps/deploy/web-apps/apps/*/mobile/dist/js/*.js.map")
  if maps:
    for m in maps: utils.log("- " + m)
  else:
    utils.log_err("files do not exist")
    utils.set_summary("web-apps closure maps %s deploy" % license, False)
    return

  utils.log_h2("web-apps closure maps %s deploy" % license)
  ret = True
  for f in maps:
    base = utils.get_relpath(f, "web-apps/deploy/web-apps/apps").replace("/", "_")
    key = "closure-maps/web-apps/%s/%s/%s/%s" % (license, common.version, common.build, base)
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    ret &= upload
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
      utils.add_deploy_data(key)
  utils.set_summary("web-apps closure maps %s deploy" % license, ret)
  return
