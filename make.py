#!/usr/bin/env python

import sys
sys.path.append('scripts')
sys.path.append('scripts/develop')
sys.path.append('scripts/core_common')
sys.path.append('scripts/core_common/modules')
import config
import base
import build
import build_js
import build_server
import deploy
import make_common
import config_server as develop_config_server

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
  base.git_update("core")
  base.git_update("sdkjs")
  base.sdkjs_addons_checkout()
  base.sdkjs_plugins_checkout()
  base.sdkjs_plugins_server_checkout()
  base.git_update("web-apps")
  base.web_apps_addons_checkout()
  base.git_update("desktop-sdk")
  base.git_update("dictionaries")

  if config.check_option("module", "builder"):
    base.git_update("DocumentBuilder")

  if config.check_option("module", "desktop"):
    base.git_update("desktop-apps")

  if (config.check_option("module", "server")):
    base.git_update("server")
    base.server_addons_checkout()
    base.git_update("document-server-integration")
    
  if (config.check_option("module", "server") or config.check_option("platform", "ios")):
    base.git_update("core-fonts")

base.configure_common_apps()

# developing...
if ("1" == config.option("develop")):
  build_server.build_server_develop()
  build_js.build_js_develop(base_dir + "/..")
  develop_config_server.make()
  exit(0)

# check only js builds
if ("1" == base.get_env("OO_ONLY_BUILD_JS")):
  build_js.make()
  exit(0)

# core 3rdParty
make_common.make()

# build updmodule for desktop (only for windows version)
if ("windows" == base.host_platform()) and (config.check_option("module", "desktop")):
  config.extend_option("config", "updmodule")
  config.extend_option("qmake_addon", "LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml")

  if not base.is_file(base_dir + "/tools/WinSparkle-0.7.0.zip"):
  	base.cmd("curl.exe", ["https://d2ettrnqo7v976.cloudfront.net/winsparkle/WinSparkle-0.7.0.zip", "--output", base_dir + "/tools/WinSparkle-0.7.0.zip"])
 
  if not base.is_dir(base_dir + "/tools/WinSparkle-0.7.0"):
  	base.cmd("7z.exe", ["x", base_dir + "/tools/WinSparkle-0.7.0.zip", "-otools"])

  base.create_dir(base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle")
  #base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/include", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/include")
  base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/Release", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/win_32")
  base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/x64/Release", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/win_64")

# build
build.make()

# js
build_js.make()

#server
build_server.make()

# deploy
deploy.make()
