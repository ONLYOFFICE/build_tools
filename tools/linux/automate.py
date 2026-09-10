#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps
import qt_binary_build

def get_branch_name(directory):
  cur_dir = os.getcwd()
  os.chdir(directory)
  # detect build_tools branch
  #command = "git branch --show-current"
  command = "git symbolic-ref --short -q HEAD"
  current_branch = base.run_command(command)['stdout']
  os.chdir(cur_dir)
  return current_branch

if not base.is_dir("./python3"):
  base.cmd("./python.sh")

if not base.is_file("./packages_complete"):
  base.cmd("./python3/bin/python3", ["./deps.py"])
  base.cmd("sudo", ["./cmake.sh"])

if not base.is_dir("./qt_build"):
  base.cmd("./python3/bin/python3", ["./qt_binary_fetch.py", "all"])

if not base.is_dir("./sysroot/ubuntu16-amd64-sysroot"):
  base.cmd_in_dir("./sysroot", "./../python3/bin/python3", ["./fetch.py", "all"])

branch = get_branch_name("../..")

array_args = sys.argv[1:]
array_modules = []
params = []

config = {}
for arg in array_args:
  if (0 == arg.find("--")):
    indexEq = arg.find("=")
    if (-1 != indexEq):
      config[arg[2:indexEq]] = arg[indexEq + 1:]
      params.append(arg[:indexEq])
      params.append(arg[indexEq + 1:])
  else:
    array_modules.append(arg)

if ("branch" in config):
  branch = config["branch"]

print("---------------------------------------------")
print("build branch: " + branch)
print("---------------------------------------------")

modules = " ".join(array_modules)
if "" == modules:
  modules = "desktop builder server"

print("---------------------------------------------")
print("build modules: " + modules)
print("---------------------------------------------")

build_tools_params = ["--branch", branch, 
                      "--module", modules,
                      "--sysroot", "1",
                      "--update", "1",
                      "--qt-dir", os.getcwd() + "/qt_build/Qt-5.9.9"] + params

base.cmd_in_dir("../..", "./tools/linux/python3/bin/python", ["./configure.py"] + build_tools_params)
base.cmd_in_dir("../..", "./tools/linux/python3/bin/python", ["./make.py"])
