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
utils.set_env_default("OO_BRANDING", utils.get_branding_name())
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
utils.log("OO_BRANDING:   " + utils.get_env("OO_BRANDING"))
utils.log("timestamp:     " + common.timestamp)
utils.log("workspace_dir: " + common.workspace_dir)
utils.log("branding_dir:  " + common.branding_dir)

# package_branding.py of the branding overrides scripts/package_branding.py
branding_scripts_dir = None
if common.branding is not None:
  branding_scripts_dir = common.branding_dir + "/build_tools/scripts"
  sys.path.insert(-1, branding_scripts_dir)

import package_branding as branding
import package_core
import package_desktop
import package_server
import package_builder
import package_mobile

if common.deploy and not getattr(branding, "s3_bucket", None):
  utils.log_err("deploy: the branding does not define s3_bucket")
  exit(1)

# targets in build order; closure maps and server editions come from the branding
closuremaps = {
  "sdkjs":   package_core.deploy_closuremaps_sdkjs,
  "webapps": package_core.deploy_closuremaps_webapps
}
targets = [["core", package_core.make]]
for name, (component, label) in getattr(branding, "closuremaps_targets", {}).items():
  targets.append([name, lambda f=closuremaps[component], l=label: f(l)])
targets.append(["desktop", package_desktop.make])
targets.append(["builder", package_builder.make])
for edition in getattr(branding, "server_editions", {}):
  targets.append(["server_" + edition, lambda e=edition: package_server.make(e)])
targets.append(["mobile", package_mobile.make])

# an unknown target is an error, not a silent skip
names = [t[0] for t in targets] + ["clean", "sign", "deploy"]
unknown = [name for name in common.targets if name not in names]
if unknown:
  utils.log_err("unknown targets: " + " ".join(unknown))
  exit(1)

# build
utils.set_cwd(common.workspace_dir, verbose=True)
for name, make in targets:
  if name in common.targets:
    make()

# extra packaging steps of the branding, after all targets
if branding_scripts_dir and utils.is_file(branding_scripts_dir + "/package_correct.py"):
  import package_correct
  package_correct.make()

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
