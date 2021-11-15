#!/usr/bin/env python

import config
import base
import os
import multiprocessing

def make_pro_file(makefiles_dir, pro_file):
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    print("------------------------------------------")
    print("BUILD_PLATFORM: " + platform)
    print("------------------------------------------")
    old_env = dict(os.environ)

    # if you need change output libraries path - set the env variable
    # base.set_env("DESTDIR_BUILD_OVERRIDE", os.getcwd() + "/out/android/" + config.branding() + "/mobile")

    isAndroid = False if (-1 == platform.find("android")) else True
    if isAndroid:
      toolchain_platform = "linux-x86_64"
      if ("mac" == base.host_platform()):
        toolchain_platform = "darwin-x86_64"
      base.set_env("ANDROID_NDK_HOST", toolchain_platform)
      old_path = base.get_env("PATH")
      new_path = base.qt_setup(platform) + "/bin:"
      new_path += (base.get_env("ANDROID_NDK_ROOT") + "/toolchains/llvm/prebuilt/" + toolchain_platform + "/bin:")
      new_path += old_path
      base.set_env("PATH", new_path)
      base.set_env("ANDROID_NDK_PLATFORM", "android-21")

    if (-1 != platform.find("ios")):
      base.hack_xcode_ios()

    # makefile suffix
    file_suff = platform
    if (config.check_option("config", "debug")):
      file_suff += "_debug_"
    file_suff += config.option("branding")

    # setup qt
    qt_dir = base.qt_setup(platform)
    base.set_env("OS_DEPLOY", platform)

    # qmake CONFIG+=...
    config_param = base.qt_config(platform)

    # qmake ADDON
    qmake_addon = []
    if ("" != config.option("qmake_addon")):
      qmake_addon.append(config.option("qmake_addon"))

    if not base.is_file(qt_dir + "/bin/qmake") and not base.is_file(qt_dir + "/bin/qmake.exe"):
      print("THIS PLATFORM IS NOT SUPPORTED")
      continue

    # non windows platform
    if not base.is_windows():
      if base.is_file(makefiles_dir + "/build.makefile_" + file_suff):
        base.delete_file(makefiles_dir + "/build.makefile_" + file_suff)
      print("make file: " + makefiles_dir + "/build.makefile_" + file_suff)
      base.cmd(qt_dir + "/bin/qmake", ["-nocache", pro_file, "CONFIG+=" + config_param] + qmake_addon)
      if ("1" == config.option("clean")):
        base.cmd_and_return_cwd(base.app_make(), ["clean", "-f", makefiles_dir + "/build.makefile_" + file_suff], True)
        base.cmd_and_return_cwd(base.app_make(), ["distclean", "-f", makefiles_dir + "/build.makefile_" + file_suff], True)
        base.cmd(qt_dir + "/bin/qmake", ["-nocache", pro_file, "CONFIG+=" + config_param] + qmake_addon)
        if not base.is_file(pro_file):
          base.cmd(qt_dir + "/bin/qmake", ["-nocache", pro_file, "CONFIG+=" + config_param] + qmake_addon)
      if ("0" != config.option("multiprocess")):
        base.cmd_and_return_cwd(base.app_make(), ["-f", makefiles_dir + "/build.makefile_" + file_suff, "-j" + str(multiprocessing.cpu_count())])
      else:
        base.cmd_and_return_cwd(base.app_make(), ["-f", makefiles_dir + "/build.makefile_" + file_suff])
    else:
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + ("x86" if base.platform_is_32(platform) else "x64"))
      qmake_bat.append("if exist ./" + makefiles_dir + "/build.makefile_" + file_suff + " del /F ./" + makefiles_dir + "/build.makefile_" + file_suff)
      qmake_addon_string = ""
      if ("" != config.option("qmake_addon")):
        qmake_addon_string = " \"" + config.option("qmake_addon") + "\""
      qmake_bat.append("call \"" + qt_dir + "/bin/qmake\" -nocache " + pro_file + " \"CONFIG+=" + config_param + "\"" + qmake_addon_string)
      if ("1" == config.option("clean")):
        qmake_bat.append("call nmake clean -f " + makefiles_dir + "/build.makefile_" + file_suff)
        qmake_bat.append("call nmake distclean -f " + makefiles_dir + "/build.makefile_" + file_suff)
        qmake_bat.append("call \"" + qt_dir + "/bin/qmake\" -nocache " + pro_file + " \"CONFIG+=" + config_param + "\"" + qmake_addon_string)
      if ("0" != config.option("multiprocess")):
        qmake_bat.append("set CL=/MP")
      qmake_bat.append("call nmake -f " + makefiles_dir + "/build.makefile_" + file_suff)
      base.run_as_bat(qmake_bat)
      
    os.environ.clear()
    os.environ.update(old_env)

    base.delete_file(".qmake.stash")

# make build.pro
def make():
  is_no_brandind_build = base.is_file("config")
  make_pro_file("makefiles", "build.pro")
  if config.check_option("module", "builder") and base.is_windows() and is_no_brandind_build:
    # check replace
    replace_path_lib = ""
    replace_path_lib_file = os.getcwd() + "/../core/DesktopEditor/doctrenderer/docbuilder.com/docbuilder.h"
    option_branding = config.option("branding")
    if (option_branding != ""):
      replace_path_lib = "../../../build/" + option_branding + "/lib/"
    # replace
    if (replace_path_lib != ""):
      base.replaceInFile(replace_path_lib_file, "../../../build/lib/", replace_path_lib)
    if ("2019" == config.option("vs-version")):
      base.make_sln("../core/DesktopEditor/doctrenderer/docbuilder.com", ["docbuilder.com_2019.sln", "/Rebuild", "\"Release|x64\""], True)
      base.make_sln("../core/DesktopEditor/doctrenderer/docbuilder.com", ["docbuilder.com_2019.sln", "/Rebuild", "\"Release|Win32\""], True)
    else:
      base.make_sln("../core/DesktopEditor/doctrenderer/docbuilder.com", ["docbuilder.com.sln", "/Rebuild", "\"Release|x64\""], True)
      base.make_sln("../core/DesktopEditor/doctrenderer/docbuilder.com", ["docbuilder.com.sln", "/Rebuild", "\"Release|Win32\""], True)
    # restore
    if (replace_path_lib != ""):
      base.replaceInFile(replace_path_lib_file, replace_path_lib, "../../../build/lib/")
  return
