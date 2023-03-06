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
    "windows_x64":   { "repo": "windows", "arch": "x64", "version": common.version + "." + common.build },
    "windows_x86":   { "repo": "windows", "arch": "x86", "version": common.version + "." + common.build },
    "darwin_x86_64": { "repo": "mac",     "arch": "x64", "version": common.version + "-" + common.build },
    "darwin_arm64":  { "repo": "mac",     "arch": "arm", "version": common.version + "-" + common.build },
    "linux_x86_64":  { "repo": "linux",   "arch": "x64", "version": common.version + "-" + common.build },
  }
  repo = repos[common.platform]
  branch = utils.get_env("BRANCH_NAME")
  core_7z = utils.get_path("build_tools/out/%s/%s/core.7z" % (prefix, company))
  dest_version = "%s/core/%s/%s/%s/" % (repo["repo"], branch, repo["version"], repo["arch"])
  dest_latest = "%s/core/%s/%s/%s/" % (repo["repo"], branch, "latest", repo["arch"])

  if branch is None:
    utils.log_err("BRANCH_NAME variable is undefined")
    utils.set_summary("core deploy", False)
    return
  if not utils.is_file(core_7z):
    utils.log_err("core.7z does not exist")
    utils.set_summary("core deploy", False)
    return

  utils.log_h2("core deploy")
  args = ["aws", "s3", "cp", "--acl", "public-read", "--no-progress",
          core_7z, "s3://" + branding.s3_bucket + "/" + dest_version + "core.7z"]
  if common.os_family == "windows":
    ret = utils.cmd(*args, verbose=True)
  else:
    ret = utils.sh(" ".join(args), verbose=True)
  if ret:
    utils.add_deploy_data("core", "Archive", core_7z, dest_version + "core.7z", branding.s3_bucket, branding.s3_region)
    args = ["aws", "s3", "sync", "--delete",
            "--acl", "public-read", "--no-progress",
            "s3://" + branding.s3_bucket + "/" + dest_version,
            "s3://" + branding.s3_bucket + "/" + dest_latest]
    if common.os_family == "windows":
      ret &= utils.cmd(*args, verbose=True)
    else:
      ret &= utils.sh(" ".join(args), verbose=True)
  utils.set_summary("core deploy", ret)
  return

def deploy_closure_maps(license):
  if not common.deploy: return
  utils.log_h1("CLOSURE MAPS")
  utils.set_cwd(utils.get_path("sdkjs/build"))

  branch = utils.get_env("BRANCH_NAME")
  maps = utils.glob_path("*.js.map")

  if branch is None:
    utils.log_err("BRANCH_NAME variable is undefined")
    utils.set_summary("closure maps " + license + " deploy", False)
    return
  if not maps:
    utils.log_err("files do not exist")
    utils.set_summary("closure maps " + license + " deploy", False)
    return

  utils.log_h2("closure maps " + license + " deploy")
  dest = "closure-maps/%s/%s/%s/%s" % (branch, common.build, license, common.platform)
  ret = True
  for file in maps:
    args = ["aws"]
    if hasattr(branding, "s3_endpoint_url"):
      args += ["--endpoint-url=" + branding.s3_endpoint_url]
    args += [
      "s3", "cp", "--no-progress", file,
      "s3://" + branding.s3_bucket + "/" + dest + "/"
    ]
    if common.os_family == "windows":
      upload = utils.cmd(*args, verbose=True)
    else:
      upload = utils.sh(" ".join(args), verbose=True)
    ret &= upload
    if upload:
      utils.add_deploy_data(
          "core", "Closure maps " + license, file, dest + "/" + file,
          branding.s3_bucket, branding.s3_region
      )
  utils.set_summary("closure maps " + license + " deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
