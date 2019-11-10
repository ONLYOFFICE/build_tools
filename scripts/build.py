import config
import base

# make build.pro
def make():
  base_dir = base.get_script_dir()
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue
    is_platform_32 = False
    if (-1 != platform.find("_32")):
      is_platform_32 = True

    platform_base = platform
    suff = platform + config.option("branding")

    if ("1" == config.option("clean")):
      base.cmd("make", ["clean", "all", "-f", base_dir + "/makefiles/build.makefile_" + suff])
      base.cmd("make", ["distclean", "-f", base_dir + "/makefiles/build.makefile_" + suff])

    qt_dir = config.option("qt-dir")
    if (-1 != platform.find("xp")):
      qt_dir = config.option("qt-dir-xp")

    if is_platform_32:
      qt_dir += ("/" + config.options["compiler"])
    else:
      qt_dir += ("/" + config.options["compiler_64"])
 
    config_param = config.option("module") + " " + config.option("config")
    if (-1 != platform.find("xp")):
      config_param += " build_xp"

    base.cmd(qt_dir + "/bin/qmake", ["-nocache", "build.pro", "CONFIG+=" + config_param])
    make_app = "make"
    if (0 == platform.find("win")):
      make_app = "nmake"

    base.set_env("QT_DEPLOY", qt_dir + "/bin")
    base.set_env("OS_DEPLOY", platform_base)

    base.cmd(make_app, ["-f", "makefiles/build.makefile_" + platform])
    base.remove_file(base_dir + ".qmake.stash")

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