import config
import base

# make build.pro
def make():
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    file_suff = platform + config.option("branding")
 
    if base.is_windows():
      base.cmd(config.option("vs-path") + "/vcvarsall.bat", ["x86" if base.platform_is_32() else "x64"])

    if ("1" == config.option("clean")):
      base.cmd(base.app_make(), ["clean", "all", "-f", "makefiles/build.makefile_" + file_suff])
      base.cmd(base.app_make(), ["distclean", "-f", "makefiles/build.makefile_" + file_suff])

    qt_dir = base.qt_setup(platform)
    config_param = base.qt_config(platform)

    base.set_env("OS_DEPLOY", platform)
    base.cmd(qt_dir + "/bin/qmake", ["-nocache", "build.pro", "CONFIG+=" + config_param])
    
    base.cmd(base.app_make(), ["-f", "makefiles/build.makefile_" + file_suff])
    base.delete_file(".qmake.stash")

  return

# JS build
def _run_npm( directory ):
  dir = base.get_path(directory)
  return base.cmd("npm", ["--prefix", dir, "install", dir])

def _run_grunt( directory, params=[] ):
  dir = base.get_path(directory)
  return base.cmd("grunt", ["--base", dir] + params)

def build_interface( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--force"])
  return

def build_sdk_desktop( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--level=ADVANCED", "--desktop=true"])
  return

def build_sdk_builder( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--level=ADVANCED"])
  return
