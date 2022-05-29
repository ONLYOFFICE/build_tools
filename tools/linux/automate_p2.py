#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps
import shutil

def get_branch_name(directory):
  cur_dir = os.getcwd()
  os.chdir(directory)
  # detect build_tools branch
  #command = "git branch --show-current"
  command = "git symbolic-ref --short -q HEAD"
  current_branch = base.run_command(command)['stdout']
  os.chdir(cur_dir)
  return current_branch

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

modules = " ".join(array_modules)
if "" == modules:
  modules = "desktop builder server"

base.cmd_in_dir("../..", "./make_p2.py")



