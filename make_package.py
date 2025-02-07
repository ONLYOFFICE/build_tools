#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("scripts")
import argparse
import package_common as common
import package_utils as utils

# parse
parser = argparse.ArgumentParser(description="Build packages.")
parser.add_argument("-P", "--platform", dest="platform", type=str,
  action="store", help="Defines platform", required=True)
parser.add_argument("-T", "--targets",  dest="targets",  type=str, nargs="+",
  action="store", help="Defines targets",  required=True)
parser.add_argument("-V", "--version",  dest="version",  type=str,
  action="store", help="Defines version")
parser.add_argument("-B", "--build",    dest="build",    type=str,
  action="store", help="Defines build")
parser.add_argument("-H", "--branch",   dest="branch",   type=str,
  action="store", help="Defines branch")
parser.add_argument("-R", "--branding", dest="branding", type=str,
  action="store", help="Provides branding path")
args = parser.parse_args()

# vars
common.os_family = utils.host_platform()
common.platform = args.platform
common.prefix = common.platformPrefixes[common.platform] if common.platform in common.platformPrefixes else ""
common.targets = args.targets
common.clean = "clean" in args.targets
common.sign = "sign" in args.targets
common.deploy = "deploy" in args.targets
if args.version: common.version = args.version
else:            common.version = utils.get_env("PRODUCT_VERSION", "0.0.0")
utils.set_env("PRODUCT_VERSION", common.version)
utils.set_env("BUILD_VERSION", common.version)
if args.build: common.build = args.build
else:          common.build = utils.get_env("BUILD_NUMBER", "0")
utils.set_env("BUILD_NUMBER", common.build)
if args.branch: common.branch = args.branch
else:           common.branch = utils.get_env("BRANCH_NAME", "null")
utils.set_env("BRANCH_NAME", common.branch)
common.branding = args.branding
common.timestamp = utils.get_timestamp()
common.workspace_dir = utils.get_abspath(utils.get_script_dir(__file__) + "/..")
common.branding_dir = utils.get_abspath(common.workspace_dir + "/" + args.branding) if args.branding else common.workspace_dir
common.summary = []
utils.log("os_family:     " + common.os_family)
utils.log("platform:      " + str(common.platform))
utils.log("prefix:        " + str(common.prefix))
utils.log("targets:       " + str(common.targets))
utils.log("clean:         " + str(common.clean))
utils.log("sign:          " + str(common.sign))
utils.log("deploy:        " + str(common.deploy))
utils.log("version:       " + common.version)
utils.log("build:         " + common.build)
utils.log("branding:      " + str(common.branding))
utils.log("timestamp:     " + common.timestamp)
utils.log("workspace_dir: " + common.workspace_dir)
utils.log("branding_dir:  " + common.branding_dir)

# branding
if common.branding is not None:
  sys.path.insert(-1, \
      utils.get_path("../" + common.branding + "/build_tools/scripts"))

import package_core
import package_desktop
import package_server
import package_builder
import package_mobile

# build
utils.set_cwd(common.workspace_dir, verbose=True)
if "core" in common.targets:
  package_core.make()
if "closuremaps_sdkjs_opensource" in common.targets:
  package_core.deploy_closuremaps_sdkjs("opensource")
if "closuremaps_sdkjs_commercial" in common.targets:
  package_core.deploy_closuremaps_sdkjs("commercial")
if "closuremaps_webapps" in common.targets:
  package_core.deploy_closuremaps_webapps("opensource")
if "desktop" in common.targets:
  package_desktop.make()
if "builder" in common.targets:
  package_builder.make()
if "server_community" in common.targets:
  package_server.make("community")
if "server_enterprise" in common.targets:
  package_server.make("enterprise")
if "server_developer" in common.targets:
  package_server.make("developer")
if "server_prerequisites" in common.targets:
  package_server.make("prerequisites")
if "mobile" in common.targets:
  package_mobile.make()

# summary
utils.log_h1("Build summary")
exitcode = 0
for i in common.summary:
  if list(i.values())[0]:
    utils.log("[  OK  ] " + list(i.keys())[0])
  else:
    utils.log("[FAILED] " + list(i.keys())[0])
    exitcode = 1

exit(exitcode)
