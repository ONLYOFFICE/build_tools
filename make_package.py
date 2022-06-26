#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("scripts")
import argparse
import package_common as common
import package_utils as utils
import package_core
import package_desktop
import package_server
import package_builder

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
common.branding = args.branding
common.timestamp = utils.get_timestamp()
common.summary = {}
common.deploy_list = []
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
utils.set_cwd(common.workspace_dir, verbose=True)

# branding
if common.branding is not None:
  sys.path.insert(-1, utils.get_path(common.branding + "/build_tools/scripts"))

# build
if not (common.platform.startswith(common.os_family) \
    and (common.platform in common.platforms)):
  exit("Unsupported platform on " + common.os_family)
package_core.make()
# package_desktop.make()
package_builder.make()
# package_server.make()

# summary
utils.log_h1("Build summary")
exitcode = 0
for task, rc in common.summary.items():
  if rc == 0:
    utils.log("[  OK  ] " + task)
  else:
    utils.log("[FAILED] " + task)
    exitcode = 1

exit(exitcode)
