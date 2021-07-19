#!/usr/bin/env python

import sys
sys.path.append('scripts')
sys.path.append('scripts/develop')
sys.path.append('scripts/develop/vendor')
sys.path.append('scripts/core_common')
sys.path.append('scripts/core_common/modules')
import config
import base
import packages

# parse configuration
config.parse()

base_dir = base.get_script_dir(__file__)

base.set_env("BUILD_PLATFORM", config.option("platform"))

# branding
if ("1" != base.get_env("OO_RUNNING_BRANDING")) and ("" != config.option("branding")):
  branding_dir = base_dir + "/../" + config.option("branding")

  if base.is_file(branding_dir + "/build_tools/make_packages.py"):
    base.check_build_version(branding_dir + "/build_tools")
    base.set_env("OO_RUNNING_BRANDING", "1")
    base.set_env("OO_BRANDING", config.option("branding"))
    base.cmd_in_dir(branding_dir + "/build_tools", "python", ["make_packages.py"])
    exit(0)

base.check_build_version(base_dir)

# build packages
packages.make()
