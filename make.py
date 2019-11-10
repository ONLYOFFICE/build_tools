import sys
sys.path.append('scripts')
import config
import base
import build
import deploy

# parse configuration
config.parse()

# update
if ("1" == config.option("update")):
  base.git_update("core")
  base.git_update("sdkjs")
  base.git_update("sdkjs-plugins")
  base.git_update("web-apps")
  base.git_update("desktop-sdk")
  base.git_update("dictionaries")
  base.git_update("core")

  if config.check_option("module", "builder"):
    base.git_update("DocumentBuilder")

  if config.check_option("module", "desktop"):
    base.git_update("desktop-apps")

base_dir = base.get_script_dir(__file__)
base.set_env("BUILD_PLATFORM", config.option("platform"))

# core 3rdParty
#base.bash(base_dir + "/../core/Common/3dParty/make")

# build updmodule for desktop (only for windows version)
if ("windows" == base.host_platform()) and (config.check_option("module", "desktop")):
  config.extend_option("config", "updmodule")
  config.extend_option("config", "LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml")

  if not base.is_file(base_dir + "/tools/WinSparkle-0.7.0.zip"):
  	base.cmd(base_dir + "/tools/win/curl/curl.exe", ["https://d2ettrnqo7v976.cloudfront.net/winsparkle/WinSparkle-0.7.0.zip", "--output", base_dir + "/tools/WinSparkle-0.7.0.zip"])
 
  if not base.is_dir(base_dir + "/tools/WinSparkle-0.7.0"):
  	base.cmd(base_dir + "/tools/win/7z/7z.exe", ["x", base_dir + "/tools/WinSparkle-0.7.0.zip", "-otools"])

  base.create_dir(base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle")
  base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/include", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/include")
  base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/Release", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/win_32")
  base.copy_dir(base_dir + "/tools/WinSparkle-0.7.0/x64/Release", base_dir + "/../desktop-apps/win-linux/3dparty/WinSparkle/win_64")

# build
build.make()

# js
if ("1" != base.get_env("OO_NO_BUILD_JS")):
  if (config.check_option("module", "builder") or config.check_option("module", "server")):
    build.build_interface(base_dir + "/../web-apps/build")
    build.build_sdk_builder(base_dir + "/../sdkjs/build")
  if config.check_option("module", "desktop"):
    build.build_sdk_desktop(base_dir + "/../sdkjs/build")

# deploy
if ("0" != config.option("deploy")):
  deploy.make()