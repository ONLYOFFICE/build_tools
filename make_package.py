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
parser.add_argument("-T", "--targets", dest="targets",   type=str, nargs="+",
                    action="store", help="Defines targets",  required=True)
parser.add_argument("-R", "--branding", dest="branding", type=str,
                    action="store", help="Provides branding path")
parser.add_argument("-V", "--version",  dest="version",  type=str,
                    action="store", help="Defines version")
parser.add_argument("-B", "--build",    dest="build",    type=str,
                    action="store", help="Defines build")
args = parser.parse_args()

# vars
common.workspace_dir = utils.get_abspath(utils.get_script_dir(__file__) + "/..")
common.os_family = utils.host_platform()
common.platform = args.platform
common.targets = args.targets
common.clean = "clean" in args.targets
common.sign = "sign" in args.targets
common.deploy = "deploy" in args.targets
common.version = args.version if (args.version is not None) else utils.get_env("PRODUCT_VERSION", "1.0.0")
common.build = args.build if (args.build is not None) else utils.get_env("BUILD_NUMBER", "1")
common.channel = utils.get_env("BUILD_CHANNEL", "other")
common.branding = args.branding
common.timestamp = utils.get_timestamp()
common.summary = []
common.deploy_data = []
utils.log("workspace_dir: " + common.workspace_dir)
utils.log("os_family:     " + common.os_family)
utils.log("platform:      " + str(common.platform))
utils.log("targets:       " + str(common.targets))
utils.log("clean:         " + str(common.clean))
utils.log("sign:          " + str(common.sign))
utils.log("deploy:        " + str(common.deploy))
utils.log("version:       " + common.version)
utils.log("build:         " + common.build)
utils.log("branding:      " + str(common.branding))
utils.log("timestamp:     " + common.timestamp)

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
utils.delete_file("deploy.json")
if "core" in common.targets:
  package_core.make()
if "closure-maps-os" in common.targets:
  package_core.deploy_closure_maps("opensource")
if "closure-maps-com" in common.targets:
  package_core.deploy_closure_maps("commercial")
if "desktop" in common.targets:
  package_desktop.make()
if "builder" in common.targets:
  package_builder.make()
if "server-community" in common.targets:
  package_server.make("community")
if "server-enterprise" in common.targets:
  package_server.make("enterprise")
if "server-developer" in common.targets:
  package_server.make("developer")
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
