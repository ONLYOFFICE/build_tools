#!/usr/bin/env python

import config
import base
import datetime
import glob
import os

def make():
  #check server module to build
  if(not config.check_option("module", "server")):
    return

  git_dir = base.get_script_dir() + "/../.."
  server_dir = base.get_script_dir() + "/../../server"
  server_admin_panel_dir = base.get_script_dir() + "/../../server-admin-panel"
  branding_dir = server_dir + "/branding"

  if("" != config.option("branding")):
    branding_dir = git_dir + '/' + config.option("branding") + '/server'

  build_server_with_addons()

  # sharp arm64: npm ci on x86_64 host may install host sharp/libvips artifacts.
  # For linux_arm64 target, fetch linux-arm64 glibc libvips and .node before pkg packaging.
  if (-1 != config.option("platform").find("linux_arm64")):
    sharp_dir = server_dir + "/DocService/node_modules/sharp"
    if base.is_exist(sharp_dir):
      env_saved = {k: os.environ.get(k) for k in ["npm_config_platform", "npm_config_arch", "npm_config_libc"]}
      os.environ.update({"npm_config_platform": "linux", "npm_config_arch": "arm64", "npm_config_libc": "glibc"})
      try:
        base.cmd_in_dir(sharp_dir, "node", ["install/libvips"], True)
        base.cmd_in_dir(sharp_dir, "npm", ["exec", "--", "prebuild-install", "--platform", "linux", "--arch", "arm64", "--libc", "glibc"], True)
      finally:
        for k, v in env_saved.items():
          if v is None: os.environ.pop(k, None)
          else: os.environ[k] = v
      if not base.is_exist(sharp_dir + "/build/Release/sharp-linux-arm64v8.node"):
        base.print_info("sharp: WARNING - sharp-linux-arm64v8.node not found, image processing may be limited on arm64")
      if not glob.glob(sharp_dir + "/vendor/*/linux-arm64v8"):
        base.print_info("sharp: WARNING - linux-arm64v8 vendor/libvips not found, image processing may be limited on arm64")

  #env variables
  product_version = base.get_env('PRODUCT_VERSION')
  if(not product_version):
    product_version = "0.0.0"

  build_number = base.get_env('BUILD_NUMBER')
  if(not build_number):
    build_number = "0"

  cur_date = datetime.date.today().strftime("%m/%d/%Y")

  base.replaceInFileRE(server_dir + "/Common/sources/commondefines.js", "const buildNumber = [0-9]*", "const buildNumber = " + build_number)
  base.replaceInFileRE(server_dir + "/Common/sources/license.js", "const buildDate = '[0-9-/]*'", "const buildDate = '" + cur_date + "'")
  base.replaceInFileRE(server_dir + "/Common/sources/commondefines.js", "const buildVersion = '[0-9.]*'", "const buildVersion = '" + product_version + "'")

  custom_public_key = branding_dir + '/debug.js'

  if(base.is_exist(custom_public_key)):
      base.copy_file(custom_public_key, server_dir + '/Common/sources')

  #node22 packaging has issue https://github.com/yao-pkg/pkg/issues/87
  pkg_target = "node20"

  if ("linux" == base.host_platform()):
    pkg_target += "-linux"
    if (-1 != config.option("platform").find("linux_arm64")):
      pkg_target += "-arm64"

  if ("windows" == base.host_platform()):
    pkg_target += "-win"

  docservice_pkg_args = [".", "-t", pkg_target]
  docservice_max_old_space_size = config.option("server-docservice-pkg-max-old-space-size")
  if "" != docservice_max_old_space_size:
    docservice_pkg_args += ["--options", "max_old_space_size=" + docservice_max_old_space_size]
  docservice_pkg_args += ["-o", "docservice"]

  base.cmd_in_dir(server_dir + "/DocService", "pkg", docservice_pkg_args)
  base.cmd_in_dir(server_dir + "/FileConverter", "pkg", [".", "-t", pkg_target, "-o", "converter"])
  base.cmd_in_dir(server_dir + "/Metrics", "pkg", [".", "-t", pkg_target, "-o", "metrics"])
  if "server-admin-panel" in base.get_server_addons() and base.is_exist(server_admin_panel_dir):
    base.cmd_in_dir(server_admin_panel_dir + "/server", "pkg", [".", "-t", pkg_target, "-o", "adminpanel"])

  example_dir = base.get_script_dir() + "/../../document-server-integration/web/documentserver-example/nodejs"
  base.delete_dir(example_dir  + "/node_modules")
  base.cmd_in_dir(example_dir, "npm", ["ci"])
  base.cmd_in_dir(example_dir, "pkg", [".", "-t", pkg_target, "-o", "example"])

def build_server_with_addons():
  addons = {}
  addons["server"] = [True, False]
  addons.update(base.get_server_addons())
  for addon in addons:
    if (addon):
      addon_dir = base.get_script_dir() + "/../../" + addon
      if (base.is_exist(addon_dir + "/package.json")):
        base.print_info("npm ci: " + addon)
        base.cmd_in_dir(addon_dir, "npm", ["ci"])
        base.print_info("npm run build: " + addon)
        base.cmd_in_dir(addon_dir, "npm", ["run", "build"])

def build_server_develop():
  build_server_with_addons()
