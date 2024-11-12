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
    make_archive()
  return

def make_archive():
  utils.set_cwd(utils.get_path(
    "build_tools/out/" + common.prefix + "/" + branding.company_name.lower()))

  utils.log_h2("core archive build")
  utils.delete_file("core.7z")
  args = ["7z", "a", "-y", "core.7z", "./core/*"]
  if utils.is_windows():
    ret = utils.cmd(*args, verbose=True)
  else:
    ret = utils.sh(" ".join(args), verbose=True)
  utils.set_summary("core archive build", ret)

  utils.log_h2("core archive deploy")
  dest = "core-" + common.prefix.replace("_","-") + ".7z"
  dest_latest = "archive/%s/latest/%s" % (common.branch, dest)
  dest_version = "archive/%s/%s/%s" % (common.branch, common.build, dest)
  ret = utils.s3_upload(
    "core.7z", "s3://" + branding.s3_bucket + "/" + dest_version)
  utils.set_summary("core archive deploy", ret)
  if ret:
    utils.log("URL: " + branding.s3_base_url + "/" + dest_version)
    utils.s3_copy(
      "s3://" + branding.s3_bucket + "/" + dest_version,
      "s3://" + branding.s3_bucket + "/" + dest_latest)
    utils.log("URL: " + branding.s3_base_url + "/" + dest_latest)

  utils.set_cwd(common.workspace_dir)
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
  utils.set_summary("web-apps closure maps %s deploy" % license, ret)
  return
