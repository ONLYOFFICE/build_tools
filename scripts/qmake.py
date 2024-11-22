#!/usr/bin/env python

import os
import sys

__dir__name__ = os.path.dirname(__file__)
sys.path.append(__dir__name__ + '/core_common/modules/android')

import base
import config
import android_ndk
import multiprocessing

def get_make_file_suffix(platform):
  suffix = platform
  if config.check_option("config", "debug"):
    suffix += "_debug_"
  suffix += config.option("branding")
  return suffix

def get_j_num():
  if ("0" != config.option("multiprocess")):
    return ["-j" + str(multiprocessing.cpu_count())]
  return []

def check_support_platform(platform):
  qt_dir = base.qt_setup(platform)
  if not base.is_file(qt_dir + "/bin/qmake") and not base.is_file(qt_dir + "/bin/qmake.exe"):
    return False
  return True

def make(platform, project, qmake_config_addon="", is_no_errors=False):
  # check platform
  if not check_support_platform(platform):
    print("THIS PLATFORM IS NOT SUPPORTED")
    return

  old_env = dict(os.environ)
  
  # qt
  qt_dir = base.qt_setup(platform)
  base.set_env("OS_DEPLOY", platform)

  # pro & makefile
  file_pro = os.path.abspath(project)

  pro_dir = os.path.dirname(file_pro)
  if (pro_dir.endswith("/.")):
    pro_dir = pro_dir[:-2]
  if (pro_dir.endswith("/")):
    pro_dir = pro_dir[:-1]

  makefile_name = "Makefile." + get_make_file_suffix(platform) 
  makefile = pro_dir + "/" + makefile_name
  stash_file = pro_dir + "/.qmake.stash"

  old_cur = os.getcwd()
  os.chdir(pro_dir)

  if (base.is_file(stash_file)):
    base.delete_file(stash_file)
  if (base.is_file(makefile)):
    base.delete_file(makefile)

  base.set_env("DEST_MAKEFILE_NAME", "./" + makefile_name)

  # setup android env
  if (-1 != platform.find("android")):
    base.set_env("ANDROID_NDK_HOST", android_ndk.host["arch"])
    base.set_env("ANDROID_NDK_PLATFORM", "android-" + android_ndk.get_sdk_api())
    base.set_env("PATH", qt_dir + "/bin:" + android_ndk.toolchain_dir() + "/bin:" + base.get_env("PATH"))

  # setup ios env
  if (-1 != platform.find("ios")):
    base.hack_xcode_ios()

  if base.is_file(makefile):
    base.delete_file(makefile)

  config_param = base.qt_config(platform)
  if ("" != qmake_config_addon):
    config_param += (" " + qmake_config_addon)

  # qmake ADDON
  qmake_addon = []
  if ("" != config.option("qmake_addon")):
    qmake_addon = config.option("qmake_addon").split()

  clean_params = ["clean", "-f", makefile]
  distclean_params = ["distclean", "-f", makefile]
  build_params = ["-nocache", file_pro] + base.qt_config_as_param(config_param) + qmake_addon

  qmake_app = qt_dir + "/bin/qmake"
  # non windows platform
  if not base.is_windows():
    if base.is_file(qt_dir + "/onlyoffice_qt.conf"):
      build_params.append("-qtconf")
      build_params.append(qt_dir + "/onlyoffice_qt.conf")
    base.cmd(qmake_app, build_params)
    base.correct_makefile_after_qmake(platform, makefile)
    if ("1" == config.option("clean")):
      base.cmd_and_return_cwd("make", clean_params, True)
      base.cmd_and_return_cwd("make", distclean_params, True)
      base.cmd(qmake_app, build_params)
      base.correct_makefile_after_qmake(platform, makefile)
    base.cmd_and_return_cwd("make", ["-f", makefile] + get_j_num(), is_no_errors)
  else:
    config_params_array = base.qt_config_as_param(config_param)
    config_params_string = ""
    for item in config_params_array:
      config_params_string += (" \"" + item + "\"")
    qmake_addon_string = " ".join(qmake_addon)
    if ("" != qmake_addon_string):
      qmake_addon_string = " " + qmake_addon_string

    qmake_bat = []
    qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + ("x86" if base.platform_is_32(platform) else "x64"))
    qmake_addon_string = ""
    if ("" != config.option("qmake_addon")):
      qmake_addon_string = " " + (" ").join(["\"" + addon + "\"" for addon in qmake_addon])
    qmake_bat.append("call \"" + qmake_app + "\" -nocache " + file_pro + config_params_string + qmake_addon_string)
    if ("1" == config.option("clean")):
      qmake_bat.append("call nmake " + " ".join(clean_params))
      qmake_bat.append("call nmake " + " ".join(distclean_params))
      qmake_bat.append("call \"" + qmake_app + "\" -nocache " + file_pro + config_params_string + qmake_addon_string)
    if ("0" != config.option("multiprocess")):
      qmake_bat.append("set CL=/MP")
    qmake_bat.append("call nmake -f " + makefile)
    base.run_as_bat(qmake_bat, is_no_errors)

  if (base.is_file(stash_file)):
    base.delete_file(stash_file)

  os.chdir(old_cur)

  os.environ.clear()
  os.environ.update(old_env)
  return

def make_all_platforms(project, qmake_config_addon=""):
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    print("------------------------------------------")
    print("BUILD_PLATFORM: " + platform)
    print("------------------------------------------")
    make(platform, project, qmake_config_addon)
  return
