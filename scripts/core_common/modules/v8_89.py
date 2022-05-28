#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess
import shutil

def make_args(args, platform, is_64=True, is_debug=False):
  args_copy = args[:]
  
  if os.uname().machine.startswith('a'):
    if is_64:
        args_copy.append("target_cpu=\\\"x64\\\"") 
        args_copy.append("v8_target_cpu=\\\"x64\\\"")
    else:
        args_copy.append("target_cpu=\\\"x86\\\"") 
        args_copy.append("v8_target_cpu=\\\"x86\\\"")
  else:
        args_copy = args[:]
        args_copy.append("target_cpu=\\\"arm64\\\"")
        args_copy.append("v8_target_cpu=\\\"arm64\\\"")
        args_copy.append("use_sysroot=true")
    
  if is_debug:
    args_copy.append("is_debug=true")
  else:
    args_copy.append("is_debug=false")
  
  if (platform == "linux"):
    args_copy.append("is_clang=true")
    if not os.uname().machine.startswith('a'):
        args_copy.append("use_sysroot=false")
  if (platform == "windows"):
    args_copy.append("is_clang=false")    

  return "--args=\"" + " ".join(args_copy) + "\""

def ninja_windows_make(args, is_64=True, is_debug=False):
  directory_out = "out.gn/"
  directory_out += ("win_64/" if is_64 else "win_32/")
  directory_out += ("debug" if is_debug else "release")

  base.cmd2("gn", ["gen", directory_out, make_args(args, "windows", is_64, is_debug)])
  base.copy_file("./" + directory_out + "/obj/v8_wrappers.ninja", "./" + directory_out + "/obj/v8_wrappers.ninja.bak")
  base.replaceInFile("./" + directory_out + "/obj/v8_wrappers.ninja", "target_output_name = v8_wrappers", "target_output_name = v8_wrappers\nbuild obj/v8_wrappers.obj: cxx ../../../src/base/platform/wrappers.cc")
  base.replaceInFile("./" + directory_out + "/obj/v8_wrappers.ninja", "build obj/v8_wrappers.lib: alink", "build obj/v8_wrappers.lib: alink obj/v8_wrappers.obj")
  base.cmd("ninja", ["-C", directory_out, "v8_wrappers"])
  base.cmd("ninja", ["-C", directory_out])
  base.delete_file("./" + directory_out + "/obj/v8_wrappers.ninja")
  base.move_file("./" + directory_out + "/obj/v8_wrappers.ninja.bak", "./" + directory_out + "/obj/v8_wrappers.ninja")
  return

def make():
  old_env = dict(os.environ)
  old_cur = os.getcwd()

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8_89"
  if not base.is_dir(base_dir):
    base.create_dir(base_dir)

  os.chdir(base_dir)
  if not base.is_dir("depot_tools"):
    base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])
    print("--- Clone complete ---")

  os.environ["PATH"] = base_dir + "/depot_tools" + os.pathsep + os.environ["PATH"]

  if ("windows" == base.host_platform()):
    base.set_env("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
    base.set_env("GYP_MSVS_VERSION", config.option("vs-version"))

  if not base.is_dir("v8"):
    print("--- Running fetch? ---")
    base.cmd("./depot_tools/fetch", ["v8"], True)
    if ("windows" == base.host_platform()):
      os.chdir("v8")
      base.cmd("git", ["config", "--system", "core.longpaths", "true"])
      os.chdir("../")
    print("--- gclient sync -r? ---")
    base.cmd("./depot_tools/gclient", ["sync", "-r", "remotes/branch-heads/8.9"], True)
    base.cmd("gclient", ["sync", "--force"], True)

  if ("windows" == base.host_platform()):
    base.replaceInFile("v8/build/config/win/BUILD.gn", ":static_crt", ":dynamic_crt")

    if not base.is_file("v8/src/base/platform/wrappers.cc"):
      base.writeFile("v8/src/base/platform/wrappers.cc", "#include \"src/base/platform/wrappers.h\"\n")

  os.chdir("v8")
  print("--- into v8 dir ---")
  
  gn_args = ["v8_static_library=true",
             "is_component_build=false",
             "v8_monolithic=true",
             "v8_use_external_startup_data=false",
             "use_custom_libcxx=false",
             "treat_warnings_as_errors=false"]

  if os.uname().machine.startswith('a'):
    print("--- Into the arm if ---")
    base.cmd("build/linux/sysroot_scripts/install-sysroot.py", ["--arch=arm64"], False)
    print("--- 1 done ---")
    base.cmd("git", ["clone", "https://github.com/ninja-build/ninja.git", "-b", "v1.8.2", "customnin"], False)
    # v8
    os.chdir("customnin")
    # v8/customnin
    base.cmd2("./configure.py", ["--bootstrap"])
    os.chdir("../")
    # v8
    base.cmd2("mv", ["-v", "customnin/ninja", "/core/Common/3dParty/v8_89/depot_tools/ninja"])
    shutil.rmtree("customnin")
    print("--- arm64 ninja done ---")
    base.cmd("git", ["clone", "https://gn.googlesource.com/gn", "customgn"], False)
    # in v8 dir
    os.chdir("customgn")
    # in v8/customgn
    base.cmd("git", ["checkout", "23d22bcaa71666e872a31fd3ec363727f305417e"], False)
    base.cmd("sed", ["-i", "-e", "\"s/-Wl,--icf=all//\"", "build/gen.py"], False)
    base.cmd("python", ["build/gen.py"], False)
    base.cmd("ninja", ["-C", "out"])
    # binary in v8/customgn/out/gn
    os.chdir("../")
    #now in v8 again
    base.cmd("cp", ["./customgn/out/gn", "./buildtools/linux64/gn"])
    shutil.rmtree("customgn") # pick up my trash
    print("--- arm64 gn done ---")
    base.cmd2("gn", ["gen", "out.gn/linux_arm64", make_args(gn_args, "linux_arm64", False)])
    print("--- 2 done ---")
    base.cmd("ninja", ["-C", "out.gn/linux_arm64"])  
    print("--- 3 done ---")
  elif config.check_option("platform", "linux_64"): # it will try to do x64 if it's arm
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
      if not base.is_file("out.gn/win_64/debug/obj/v8_monolith.lib"):
        ninja_windows_make(gn_args, True, True)

    if not base.is_file("out.gn/win_64/release/obj/v8_monolith.lib"):
      ninja_windows_make(gn_args)

  if config.check_option("platform", "win_32"):
    if (-1 != config.option("config").lower().find("debug")):
      if not base.is_file("out.gn/win_32/debug/obj/v8_monolith.lib"):
        ninja_windows_make(gn_args, False, True)

    if not base.is_file("out.gn/win_32/release/obj/v8_monolith.lib"):
      ninja_windows_make(gn_args, False)

  os.chdir(old_cur)
  os.environ.clear()
  os.environ.update(old_env)
