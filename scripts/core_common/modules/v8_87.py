#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def make_args(args, platform, is_64=True, is_debug=False):
  args_copy = args[:]
  if is_64:
    args_copy.append("target_cpu=\\\"x64\\\"") 
    args_copy.append("v8_target_cpu=\\\"x64\\\"")
  else:
    args_copy.append("target_cpu=\\\"x86\\\"") 
    args_copy.append("v8_target_cpu=\\\"x86\\\"")
  
  if is_debug:
    args_copy.append("is_debug=true")
  else:
    args_copy.append("is_debug=false")
  
  if (platform == "linux"):
    args_copy.append("is_clang=true")
    args_copy.append("use_sysroot=false")
  if (platform == "windows"):
    args_copy.append("is_clang=false")    

  return "--args=\"" + " ".join(args_copy) + "\""


def make():
  old_env = dict(os.environ)
  old_cur = os.getcwd()

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8_87"
  if not base.is_dir(base_dir):
    base.create_dir(base_dir)

  os.chdir(base_dir)
  if not base.is_dir("depot_tools"):
    base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])

  os.environ["PATH"] = base_dir + "/depot_tools" + os.pathsep + os.environ["PATH"]

  if ("windows" == base.host_platform()):
    base.set_env("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
    base.set_env("GYP_MSVS_VERSION", config.option("vs-version"))

  if not base.is_dir("v8"):
    base.cmd("./depot_tools/fetch", ["v8"], True)
    base.cmd("./depot_tools/gclient", ["sync", "-r", "8.7.220.25"], True)
    base.cmd("gclient", ["sync", "--force"], True)

  if ("windows" == base.host_platform()):
    base.replaceInFile("v8/build/config/win/BUILD.gn", ":static_crt", ":dynamic_crt")

  os.chdir("v8")
  
  gn_args = ["v8_static_library=true",
             "is_component_build=false",
             "v8_monolithic=true",
             "v8_use_external_startup_data=false",
             "use_custom_libcxx=false",
             "treat_warnings_as_errors=false"]

  if config.check_option("platform", "linux_64"):
    base.cmd2("gn", ["gen", "out.gn/linux_64", make_args(gn_args, "linux")])
    base.cmd("ninja", ["-C", "out.gn/linux_64"])

  if config.check_option("platform", "linux_32"):
    base.cmd2("gn", ["gen", "out.gn/linux_32", make_args(gn_args, "linux", False)])
    base.cmd("ninja", ["-C", "out.gn/linux_32"])

  if config.check_option("platform", "mac_64"):
    base.cmd2("gn", ["gen", "out.gn/mac_64", make_args(gn_args, "mac")])
    base.cmd("ninja", ["-C", "out.gn/mac_64"])

  if config.check_option("platform", "win_64"):
    if (-1 != config.option("config").lower().find("debug")):
      base.cmd2("gn", ["gen", "out.gn/win_64/debug", make_args(gn_args, "windows", True, True)])
      base.cmd("ninja", ["-C", "out.gn/win_64/debug"])      

    base.cmd2("gn", ["gen", "out.gn/win_64/release", make_args(gn_args, "windows")])
    base.cmd("ninja", ["-C", "out.gn/win_64/release"])

  if config.check_option("platform", "win_32"):
    if (-1 != config.option("config").lower().find("debug")):
      base.cmd2("gn", ["gen", "out.gn/win_32/debug", make_args(gn_args, "windows", False, True)])
      base.cmd("ninja", ["-C", "out.gn/win_32/debug"])    

    base.cmd2("gn", ["gen", "out.gn/win_32/release", make_args(gn_args, "windows", False)])
    base.cmd("ninja", ["-C", "out.gn/win_32/release"])

  os.chdir(old_cur)
  os.environ.clear()
  os.environ.update(old_env)
