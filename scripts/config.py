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
    configOptions[k] = v
    os.environ["OO_" + k.upper().replace("-", "_")] = v

  # export options
  global options
  options = configOptions

  # all platforms
  global platforms
  platforms = ["win_64", "win_32", "win_64_xp", "win_32_xp", "linux_64", "linux_32", "mac_64", "ios"]

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

  if check_option("platform", "xp") and ("windows" == host_platform):
    options["platform"] += " win_64_xp win_32_xp"

  # correct compiler
  if ("" == option("compiler")):
    if ("windows" == host_platform):
      options["compiler"] = "msvc2015"
      options["compiler_64"] = "msvc2015_64"
    elif ("linux" == host_platform):
      options["compiler"] = "gcc"
      options["compiler_64"] = "gcc_64"
    elif ("mac" == host_platform):
      options["compiler"] += "clang"
      options["compiler_64"] += "clang_64"
    elif ("ios" == host_platform):
      options["compiler"] += "ios"
      options["compiler_64"] += "ios"
  elif ("windows" == host_platform):
    options["compiler_64"] = options["compiler"] + "_64"
  elif ("linux" == host_platform):
    options["compiler_64"] = options["compiler"] + "_64"
  elif ("mac" == host_platform):
    options["compiler_64"] = options["compiler"] + "_64"
  else:
    options["compiler_64"] = options["compiler"]

  # check vs-path
  if ("windows" == host_platform):
    options["vs-path"] = base.get_env("ProgramFiles") + "/Microsoft Visual Studio 14.0/VC"
    if ("" != base.get_env("ProgramFiles(x86)")):
      options["vs-path"] = base.get_env("ProgramFiles(x86)") + "/Microsoft Visual Studio 14.0/VC"

  return

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
