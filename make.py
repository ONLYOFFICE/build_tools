#!/usr/bin/env python

import sys
sys.path.append('scripts')
sys.path.append('scripts/develop')
sys.path.append('scripts/develop/vendor')
sys.path.append('scripts/core_common')
sys.path.append('scripts/core_common/modules')
import config
import base
import build
import build_js
import build_server
import deploy
import make_common
import develop
import os
import platform

# set up environment
if "ppc64" in platform.machine():
  # PhantomJS has been ignoring requests to support non-Intel machines upstream,
  # (issues #15432, #14421, #13708) so we have to use the distro version.  The
  # distro version in turn fails if there is no X server available and this
  # environment variable is not set, so set it here...
  os.environ["QT_QPA_PLATFORM"] = "offscreen"

  # Debian builds libpng without VSX support for some reason (bug #959487)
  os.environ["CFLAGS"] = "-DPNG_POWERPC_VSX_OPT=0"

# parse configuration
config.parse()

base_dir = base.get_script_dir(__file__)

base.set_env("BUILD_PLATFORM", config.option("platform"))

# branding
if ("1" != base.get_env("OO_RUNNING_BRANDING")) and ("" != config.option("branding")):
  branding_dir = base_dir + "/../" + config.option("branding")

  if ("1" == config.option("update")):
    is_exist = True
    if not base.is_dir(branding_dir):
      is_exist = False
      base.cmd("git", ["clone", config.option("branding-url"), branding_dir])

    base.cmd_in_dir(branding_dir, "git", ["fetch"], True)
   
    if not is_exist or ("1" != config.option("update-light")):
      base.cmd_in_dir(branding_dir, "git", ["checkout", "-f", config.option("branch")], True)

    base.cmd_in_dir(branding_dir, "git", ["pull"], True)

  if base.is_file(branding_dir + "/build_tools/make.py"):
    base.check_build_version(branding_dir + "/build_tools")
    base.set_env("OO_RUNNING_BRANDING", "1")
    base.set_env("OO_BRANDING", config.option("branding"))
    base.cmd_in_dir(branding_dir + "/build_tools", "python", ["make.py"])
    exit(0)

# correct defaults (the branding repo is already updated)
config.parse_defaults()

base.check_build_version(base_dir)

# update
if ("1" == config.option("update")):
  repositories = base.get_repositories()
  base.update_repositories(repositories)

base.configure_common_apps()

# developing...
develop.make();

# check only js builds
if ("1" == base.get_env("OO_ONLY_BUILD_JS")):
  build_js.make()
  exit(0)

# core 3rdParty
make_common.make()

# build updmodule for desktop (only for windows version)
if config.check_option("module", "desktop"):
  config.extend_option("qmake_addon", "URL_WEBAPPS_HELP=https://download.onlyoffice.com/install/desktop/editors/help/v" + base.get_env('PRODUCT_VERSION') + "-1/apps")

  if "windows" == base.host_platform():
    config.extend_option("config", "updmodule")
    config.extend_option("qmake_addon", "LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.json")



    if ("windows" == base.host_platform()):
      base.set_env("VIDEO_PLAYER_VLC_DIR", base_dir + "/../desktop-sdk/ChromiumBasedEditors/videoplayerlib/vlc")

# build
build.make()

# js
build_js.make()

#server
build_server.make()

# deploy
deploy.make()
