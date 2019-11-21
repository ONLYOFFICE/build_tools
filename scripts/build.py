import config
import base

# make build.pro
def make():
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue
    is_platform_32 = False
    if (-1 != platform.find("_32")):
      is_platform_32 = True

    suff = platform + config.option("branding")

    make_app = "make" if (0 != platform.find("win")) else "nmake"
 
    if ("windows" == base.host_platform()):
      base.cmd(config.option("vs-path") + "/vcvarsall.bat", ["x86" if is_platform_32 else "x64"])

    if ("1" == config.option("clean")):
      base.cmd(make_app, ["clean", "all", "-f", "makefiles/build.makefile_" + suff])
      base.cmd(make_app, ["distclean", "-f", "makefiles/build.makefile_" + suff])

    qt_dir = config.option("qt-dir") if (-1 == platform.find("xp")) else config.option("qt-dir-xp")
    qt_dir = (qt_dir + "/" + config.options["compiler"]) if is_platform_32 else (qt_dir + "/" + config.options["compiler_64"])

    config_param = config.option("module") + " " + config.option("config")
    if (-1 != platform.find("xp")):
      config_param += " build_xp"

    base.set_env("QT_DEPLOY", qt_dir + "/bin")
    base.set_env("OS_DEPLOY", platform)
    base.cmd(qt_dir + "/bin/qmake", ["-nocache", "build.pro", "CONFIG+=" + config_param])
    
    base.cmd(make_app, ["-f", "makefiles/build.makefile_" + platform])
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
