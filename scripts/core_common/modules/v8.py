#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess
import v8_89

def clean():
  if base.is_dir("depot_tools"):
    base.delete_dir_with_access_error("depot_tools");
    base.delete_dir("depot_tools")
  if base.is_dir("v8"):
    base.delete_dir_with_access_error("v8");
    base.delete_dir("v8")
  if base.is_exist("./.gclient"):
    base.delete_file("./.gclient")
  if base.is_exist("./.gclient_entries"):
    base.delete_file("./.gclient_entries")
  if base.is_exist("./.cipd"):
    base.delete_dir("./.cipd")
  return

def is_main_platform():
  if (config.check_option("platform", "win_64") or config.check_option("platform", "win_32")):
    return True
  if (config.check_option("platform", "linux_64") or config.check_option("platform", "linux_32") or config.check_option("platform", "linux_arm64")):
    return True
  if config.check_option("platform", "mac_64"):
    return True
  if config.check_option("platform", "ios"):
    return True
  if (-1 != config.option("platform").find("android")):
    return True
  return False

def is_xp_platform():
  if config.check_option("platform", "win_64_xp") or config.check_option("platform", "win_32_xp"):
    return True
  return False

def is_use_clang():
  gcc_version = 4
  gcc_version_str = base.run_command("gcc -dumpfullversion -dumpversion")['stdout']
  if (gcc_version_str != ""):
    gcc_version = int(gcc_version_str.split(".")[0])
    
  is_clang = "false"
  if (gcc_version >= 6):
    is_clang = "true"

  print("gcc major version: " + str(gcc_version) + ", use clang:" + is_clang)
  return is_clang

def make():
  if not is_main_platform():
    make_xp()
    return

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8"
  if ("ios" == config.option("platform")):
    return

  if (-1 != config.option("platform").find("android")):
    base.cmd_in_dir(base_dir + "/android", "python", ["./make.py"])
    if (-1 == config.option("platform").find("linux")) and (-1 == config.option("platform").find("mac")) and (-1 == config.option("platform").find("win")):
      return

  if ("mac" == base.host_platform()) and (-1 == config.option("config").find("use_v8")):
    return

  use_v8_89 = False
  if (-1 != config.option("config").lower().find("v8_version_89")):
    use_v8_89 = True
  if ("windows" == base.host_platform()) and (config.option("vs-version") == "2019"):
    use_v8_89 = True
  if config.check_option("platform", "linux_arm64"):
    use_v8_89 = True

  if (use_v8_89):
    v8_89.make()
    return

  print("[fetch & build]: v8")
  old_env = dict(os.environ)

  old_cur = os.getcwd()
  os.chdir(base_dir)

  if ("windows" == base.host_platform()):
    base.set_env("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
    base.set_env("GYP_MSVS_VERSION", "2015")

  base.common_check_version("v8", "1", clean)

  if not base.is_dir("v8/out.gn"):
    clean()

  if not base.is_dir("depot_tools"):
    base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])
    if ("windows" == base.host_platform()):
      # hack for 32 bit system!!!
      if base.is_file("depot_tools/cipd.ps1"):
        base.replaceInFile("depot_tools/cipd.ps1", "windows-386", "windows-amd64")

  os.environ["PATH"] = base_dir + "/depot_tools" + os.pathsep + os.environ["PATH"]

  if not base.is_dir("v8/out.gn"):
    base.cmd("gclient")

  # --------------------------------------------------------------------------
  # fetch
  if not base.is_dir("v8"):
    base.cmd("./depot_tools/fetch", ["v8"], True)
    os.chdir(base_dir + "/v8")
    base.cmd("git", ["checkout", "-b", "6.0", "branch-heads/6.0"], True)
    os.chdir(base_dir)

  # --------------------------------------------------------------------------
  # correct
  if not base.is_dir("v8/out.gn"):
    
    # windows hack (delete later) ----------------------
    if ("windows" == base.host_platform()):
      base.delete_dir_with_access_error("v8/buildtools/win")
      base.cmd("git", ["config", "--system", "core.longpaths", "true"])
      base.cmd("gclient", ["sync", "--force"], True)
    else:
      base.cmd("gclient", ["sync"], True) 

    # normal version !!!
    #base.cmd("gclient", ["sync"], True)
    # --------------------------------------------------

    if ("linux" == base.host_platform()):
      if base.is_dir("v8/third_party/binutils/Linux_x64/Release"):
        base.delete_dir("v8/third_party/binutils/Linux_x64/Release")
      if base.is_dir("v8/third_party/binutils/Linux_ia32/Release"):
        base.delete_dir("v8/third_party/binutils/Linux_ia32/Release")

      base.cmd("gclient", ["sync", "--no-history"])

      if base.is_dir("v8/third_party/binutils/Linux_x64/Release/bin"):
        for file in os.listdir("v8/third_party/binutils/Linux_x64/Release/bin"):
          name = file.split("/")[-1]
          if ("ld.gold" != name):
            base.cmd("mv", ["v8/third_party/binutils/Linux_x64/Release/bin/" + name, "v8/third_party/binutils/Linux_x64/Release/bin/old_" + name])
            base.cmd("ln", ["-s", "/usr/bin/" + name, "v8/third_party/binutils/Linux_x64/Release/bin/" + name])

      if base.is_dir("v8/third_party/binutils/Linux_ia32/Release/bin"):
        for file in os.listdir("v8/third_party/binutils/Linux_ia32/Release/bin"):
          name = file.split("/")[-1]
          if ("ld.gold" != name):
            base.cmd("mv", ["v8/third_party/binutils/Linux_ia32/Release/bin/" + name, "v8/third_party/binutils/Linux_ia32/Release/bin/old_" + name])
            base.cmd("ln", ["-s", "/usr/bin/" + name, "v8/third_party/binutils/Linux_ia32/Release/bin/" + name])

    if ("windows" == base.host_platform()):
      base.replaceInFile("v8/build/config/win/BUILD.gn", ":static_crt", ":dynamic_crt")
    if ("mac" == base.host_platform()):
      base.replaceInFile("v8/build/config/mac/mac_sdk.gni", "if (mac_sdk_version != mac_sdk_min_build_override", "if (false && mac_sdk_version != mac_sdk_min_build_override")
      base.replaceInFile("v8/build/mac/find_sdk.py", "^MacOSX(10\\.\\d+)\\.sdk$", "^MacOSX(1\\d\\.\\d+)\\.sdk$")

      if (11003 <= base.get_mac_sdk_version_number()):
        base.copy_dir("v8/third_party/llvm-build/Release+Asserts/include", "v8/third_party/llvm-build/Release+Asserts/__include")
        base.delete_dir("v8/third_party/llvm-build/Release+Asserts/include")
        base.replaceInFile("v8/build/config/mac/BUILD.gn", "\"-mmacosx-version-min=$mac_deployment_target\",", "\"-mmacosx-version-min=$mac_deployment_target\",\n    \"-Wno-deprecated-declarations\",")

  # --------------------------------------------------------------------------
  # build
  os.chdir("v8")

  base_args64 = "target_cpu=\\\"x64\\\" v8_target_cpu=\\\"x64\\\" v8_static_library=true is_component_build=false v8_use_snapshot=false"
  base_args32 = "target_cpu=\\\"x86\\\" v8_target_cpu=\\\"x86\\\" v8_static_library=true is_component_build=false v8_use_snapshot=false"

  if config.check_option("platform", "linux_64"):
    base.cmd2("gn", ["gen", "out.gn/linux_64", "--args=\"is_debug=false " + base_args64 + " is_clang=" + is_use_clang() + " use_sysroot=false treat_warnings_as_errors=false\""])
    base.cmd("ninja", ["-C", "out.gn/linux_64"])

  if config.check_option("platform", "linux_32"):
    base.cmd2("gn", ["gen", "out.gn/linux_32", "--args=\"is_debug=false " + base_args32 + " is_clang=" + is_use_clang() + " use_sysroot=false treat_warnings_as_errors=false\""])
    base.cmd("ninja", ["-C", "out.gn/linux_32"])

  if config.check_option("platform", "mac_64"):
    base.cmd2("gn", ["gen", "out.gn/mac_64", "--args=\"is_debug=false " + base_args64 + "\""])
    base.cmd("ninja", ["-C", "out.gn/mac_64"])

  if config.check_option("platform", "win_64"):
    if (-1 != config.option("config").lower().find("debug")):
      base.cmd2("gn", ["gen", "out.gn/win_64/debug", "--args=\"is_debug=true " + base_args64 + " is_clang=false\""])
      base.cmd("ninja", ["-C", "out.gn/win_64/debug"])      

    base.cmd2("gn", ["gen", "out.gn/win_64/release", "--args=\"is_debug=false " + base_args64 + " is_clang=false\""])
    base.cmd("ninja", ["-C", "out.gn/win_64/release"])

  if config.check_option("platform", "win_32"):
    if (-1 != config.option("config").lower().find("debug")):
      base.cmd2("gn", ["gen", "out.gn/win_32/debug", "--args=\"is_debug=true " + base_args32 + " is_clang=false\""])
      base.cmd("ninja", ["-C", "out.gn/win_32/debug"])    

    base.cmd2("gn", ["gen", "out.gn/win_32/release", "--args=\"is_debug=false " + base_args32 + " is_clang=false\""])
    base.cmd("ninja", ["-C", "out.gn/win_32/release"])

  os.chdir(old_cur)
  os.environ.clear()
  os.environ.update(old_env)

  make_xp()
  return

def make_xp():
  if not is_xp_platform():
    return

  print("[fetch & build]: v8_xp")
  old_env = dict(os.environ)

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8/v8_xp"
  old_cur = os.getcwd()
  os.chdir(base_dir)

  if ("windows" == base.host_platform()):
    base.set_env("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
    base.set_env("GYP_MSVS_VERSION", "2015")

  base.common_check_version("v8", "1", clean)

  if not base.is_dir("win_64") and not base.is_dir("win_32"):
    clean()

  if not base.is_dir("depot_tools"):
    base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])
    if ("windows" == base.host_platform()):
      # hack for 32 bit system!!!
      if base.is_file("depot_tools/cipd.ps1"):
        base.replaceInFile("depot_tools/cipd.ps1", "windows-386", "windows-amd64")
  
  os.environ["PATH"] = os.pathsep.join([base_dir + "/depot_tools", 
    base_dir + "/depot_tools/win_tools-2_7_13_chromium7_bin/python/bin", 
    config.option("vs-path") + "/../Common7/IDE",
    os.environ["PATH"]])

  # --------------------------------------------------------------------------
  # fetch
  if not base.is_dir("v8"):
    base.cmd("./depot_tools/fetch", ["v8"], True)
    base.cmd("./depot_tools/gclient", ["sync", "-r", "4.10.253"], True)
    base.delete_dir_with_access_error("v8/buildtools/win")
    base.cmd("git", ["config", "--system", "core.longpaths", "true"])
    base.cmd("gclient", ["sync", "--force"], True)

  # save common py script
  base.save_as_script("v8/build/common_xp.py", [
    "import os",
    "def replaceInFile(path, text, textReplace):",
    "  filedata = '';",
    "  with open(path, 'r') as file:",
    "    filedata = file.read()",
    "  filedata = filedata.replace(text, textReplace)",
    "  os.remove(path)",
    "  with open(path, 'w') as file:",
    "    file.write(filedata)",
    "  return",
    "",
    "projects = ['v8/tools/gyp/v8_base_0.vcxproj', 'v8/tools/gyp/v8_base_1.vcxproj', 'v8/tools/gyp/v8_base_2.vcxproj', 'v8/tools/gyp/v8_base_3.vcxproj',",
    "'v8/tools/gyp/v8_libbase.vcxproj', 'v8/tools/gyp/v8_libplatform.vcxproj', 'v8/tools/gyp/v8_nosnapshot.vcxproj', 'v8/tools/gyp/mksnapshot.vcxproj',",
    "'v8/third_party/icu/icui18n.vcxproj', 'v8/third_party/icu/icuuc.vcxproj']",
    "",
    "for file in projects:",
    "  replaceInFile(file, '<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>', '<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>')",
    "  replaceInFile(file, '<RuntimeLibrary>MultiThreaded</RuntimeLibrary>', '<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>')",
    ]);

  if config.check_option("platform", "win_64_xp"):
    if not base.is_dir("win_64/release"):
      base.run_as_bat(["call python v8/build/gyp_v8 -Dtarget_arch=x64", "call python v8/build/common_xp.py", "call devenv v8/tools/gyp/v8.sln /Rebuild Release"])
      base.create_dir("win_64/release")
      base.copy_files("v8/build/Release/lib/*", "win_64/release/")
      base.copy_file("v8/build/Release/icudt.dll", "win_64/release/icudt.dll")
   
    if (-1 != config.option("config").lower().find("debug")) and not base.is_dir("win_64/debug"):
      base.run_as_bat(["call python v8/build/gyp_v8 -Dtarget_arch=x64", "call python v8/build/common_xp.py", "call devenv v8/tools/gyp/v8.sln /Rebuild Debug"])
      base.create_dir("win_64/debug")
      base.copy_files("v8/build/Debug/lib/*", "win_64/debug/")
      base.copy_file("v8/build/Debug/icudt.dll", "win_64/debug/icudt.dll")

  if config.check_option("platform", "win_32_xp"):
    if not base.is_dir("win_32/release"):
      base.run_as_bat(["call python v8/build/gyp_v8", "call python v8/build/common_xp.py", "call devenv v8/tools/gyp/v8.sln /Rebuild Release"])
      base.create_dir("win_32/release")
      base.copy_files("v8/build/Release/lib/*", "win_32/release/")
      base.copy_file("v8/build/Release/icudt.dll", "win_32/release/icudt.dll")
   
    if (-1 != config.option("config").lower().find("debug")) and not base.is_dir("win_32/debug"):
      base.run_as_bat(["call python v8/build/gyp_v8", "call python v8/build/common_xp.py", "call devenv v8/tools/gyp/v8.sln /Rebuild Debug"])
      base.create_dir("win_32/debug")
      base.copy_files("v8/build/Debug/lib/*", "win_32/debug/")
      base.copy_file("v8/build/Debug/icudt.dll", "win_32/debug/icudt.dll")

  os.chdir(old_cur)
  os.environ.clear()
  os.environ.update(old_env)
  return
