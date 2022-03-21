#!/usr/bin/env python

import base
import os
import platform

def parse():
  configfile = open(base.get_script_dir() + "/../config", "r")
  configOptions = {}
  for line in configfile:
    name, value = line.partition("=")[::2]
    k = name.strip()
    v = value.strip(" '\"\r\n")
    if ("true" == v.lower()):
      v = "1"
    if ("false" == v.lower()):
      v = "0"
    configOptions[k] = v
    os.environ["OO_" + k.upper().replace("-", "_")] = v

  # export options
  global options
  options = configOptions

  # all platforms
  global platforms
  platforms = ["win_64", "win_32", "win_64_xp", "win_32_xp", 
               "linux_64", "linux_32", "linux_arm64",
               "mac_64", "mac_arm64",
               "ios", 
               "android_arm64_v8a", "android_armv7", "android_x86", "android_x86_64"]

  # correction
  host_platform = base.host_platform()
  
  # platform
  if check_option("platform", "all"):
    if ("windows" == host_platform):
      options["platform"] += " win_64 win_32"
    elif ("linux" == host_platform):
      options["platform"] += " linux_64 linux_32"
    else:
      options["platform"] += " mac_64"

  if check_option("platform", "native"):
    bits = "32"
    if platform.machine().endswith('64'):
      bits = "64"
    if ("windows" == host_platform):
      options["platform"] += (" win_" + bits)
    elif ("linux" == host_platform):
      options["platform"] += (" linux_" + bits)
    else:
      options["platform"] += (" mac_" + bits)

  if ("mac" == host_platform) and check_option("platform", "mac_arm64") and not base.is_os_arm():
    if not check_option("platform", "mac_64"):
      options["platform"] = "mac_64 " + options["platform"]

  if ("linux" == host_platform) and check_option("platform", "linux_arm64") and not base.is_os_arm():
    if not check_option("platform", "linux_64"):
      # linux_64 binaries need only for desktop
      if check_option("module", "desktop"):
        options["platform"] = "linux_64 " + options["platform"]

  if check_option("platform", "xp") and ("windows" == host_platform):
    options["platform"] += " win_64_xp win_32_xp"

  if check_option("platform", "android"):
    options["platform"] += " android_arm64_v8a android_armv7 android_x86 android_x86_64"

  # check vs-version
  if ("" == option("vs-version")):
    options["vs-version"] = "2015"

  # check vs-path
  if ("windows" == host_platform) and ("" == option("vs-path")):
    programFilesDir = base.get_env("ProgramFiles")
    if ("" != base.get_env("ProgramFiles(x86)")):
      programFilesDir = base.get_env("ProgramFiles(x86)")
    if ("2015" == options["vs-version"]):
      options["vs-path"] = programFilesDir + "/Microsoft Visual Studio 14.0/VC"
    elif ("2019" == options["vs-version"]):
      if base.is_dir(programFilesDir + "/Microsoft Visual Studio/2019/Enterprise/VC/Auxiliary/Build"):
        options["vs-path"] = programFilesDir + "/Microsoft Visual Studio/2019/Enterprise/VC/Auxiliary/Build"
      elif base.is_dir(programFilesDir + "/Microsoft Visual Studio/2019/Professional/VC/Auxiliary/Build"):
        options["vs-path"] = programFilesDir + "/Microsoft Visual Studio/2019/Professional/VC/Auxiliary/Build"
      else:
        options["vs-path"] = programFilesDir + "/Microsoft Visual Studio/2019/Community/VC/Auxiliary/Build"

  # check sdkjs-plugins
  if not "sdkjs-plugin" in options:
    options["sdkjs-plugin"] = "default"
  if not "sdkjs-plugin-server" in options:
    options["sdkjs-plugin-server"] = "default"

  if not "arm64-toolchain-bin" in options:
    options["arm64-toolchain-bin"] = "/usr/bin"

  return

def check_compiler(platform):
  compiler = {}
  compiler["compiler"] = option("compiler")
  compiler["compiler_64"] = compiler["compiler"] + "_64"

  if ("" != compiler["compiler"]):
    if ("ios" == platform):
      compiler["compiler_64"] = compiler["compiler"]
    return compiler

  if (0 == platform.find("win")):
    compiler["compiler"] = "msvc" + options["vs-version"]
    compiler["compiler_64"] = "msvc" + options["vs-version"] + "_64"
  elif (0 == platform.find("linux")):
    compiler["compiler"] = "gcc"
    compiler["compiler_64"] = "gcc_64"
    if (0 == platform.find("linux_arm")) and not base.is_os_arm():
      compiler["compiler"] = "gcc_arm"
      compiler["compiler_64"] = "gcc_arm64"
  elif (0 == platform.find("mac")):
    compiler["compiler"] = "clang"
    compiler["compiler_64"] = "clang_64"
  elif ("ios" == platform):
    compiler["compiler"] = "ios"
    compiler["compiler_64"] = "ios"
  elif (0 == platform.find("android")):
    compiler["compiler"] = platform
    compiler["compiler_64"] = platform

  if base.host_platform() == "mac":
    if not base.is_dir(options["qt-dir"] + "/" + compiler["compiler_64"]):
      if base.is_dir(options["qt-dir"] + "/macos"):
        compiler["compiler"] = "macos"
        compiler["compiler_64"] = "macos"

  return compiler

def check_option(name, value):
  if not name in options:
    return False
  tmp = " " + options[name] + " "
  if (-1 == tmp.find(" " + value + " ")):
    return False
  return True

def option(name):
  if name in options:
    return options[name]
  return ""

def extend_option(name, value):
  if name in options:
    options[name] = options[name] + " " + value
  else:
    options[name] = value

def branding():
  branding = option("branding-name")
  if ("" == branding):
    branding = "onlyoffice"
  return branding

def is_mobile_platform():
  all_platforms = option("platform")
  if (-1 != all_platforms.find("android")):
    return True
  if (-1 != all_platforms.find("ios")):
    return True
  return False

def parse_defaults():
  defaults_path = base.get_script_dir() + "/../defaults"
  if ("" != option("branding")):
    defaults_path_branding = base.get_script_dir() + "/../../" + option("branding") + "/build_tools/defaults"
    if base.is_file(defaults_path_branding):
      defaults_path = defaults_path_branding
  defaults_file = open(defaults_path, "r")
  defaults_options = {}
  for line in defaults_file:
    name, value = line.partition("=")[::2]
    k = name.strip()
    v = value.strip(" '\"\r\n")
    if ("true" == v.lower()):
      v = "1"
    if ("false" == v.lower()):
      v = "0"
    defaults_options[k] = v

  for name in defaults_options:
    if name in options:
      options[name] = options[name].replace("default", defaults_options[name])
    else:
      options[name] = defaults_options[name]
  return
