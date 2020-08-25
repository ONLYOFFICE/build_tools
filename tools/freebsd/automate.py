#!/usr/bin/env python
# 
# Before calling this script:
#   - be sure that "git" (or "git-lite"), "sudo" and # "python27" are installed:
#     # pkg install git-lite sudo python27
#   - /usr/bin/python is a symlink to /usr/local/bin/python2.7:
#     # ln -s /usr/local/bin/python2.7 /usr/bin/python
#   - CC and CXX environment variables are respectively set to clang and clang++
#     # export CC=clang
#     # export CXX=clang++

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess

def get_branch_name(directory):
  cur_dir = os.getcwd()
  os.chdir(directory)
  # detect build_tools branch
  #command = "git branch --show-current"
  command = "git symbolic-ref --short -q HEAD"
  popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  current_branch = "master"
  try:
    stdout, stderr = popen.communicate()
    popen.wait()
    current_branch = stdout.strip().decode("utf-8")
  finally:
    popen.stdout.close()
    popen.stderr.close()
  os.chdir(cur_dir)
  return current_branch

def install_deps():
  # dependencies
  packages = ["git-lite",
  	      "bash",
  	      "png",
	      "jpeg",
	      "p7zip",
	      "qt5-qmake",
	      "boost-libs",
	      "npm-node10",
	      "openjdk8",
	      "subversion"]

  base.cmd("sudo", ["pkg", "install"] + packages)
  base.set_env('QT_SELECT', 'qt5')

  # nodejs
  if not base.is_file("./node_js_setup_10.x"):
    base.cmd("sudo", ["touch", "./node_js_setup_10.x"])
    base.cmd("sudo", ["npm", "install", "-g", "npm"])
    base.cmd("sudo", ["npm", "install", "-g", "grunt-cli"])
    base.cmd("sudo", ["npm", "install", "-g", "pkg"])
  return

if not base.is_file("./node_js_setup_10.x"):
  print("install dependencies...")
  install_deps()  

if not base.is_dir("./qt"):  
    base.cmd("mkdir", ["qt",])
    base.cmd("ln", ["-s", "/usr/local/lib/qt5", "qt/gcc_64"])

branch = get_branch_name("../..")

array_args = sys.argv[1:]
array_modules = []

config = {}
for arg in array_args:
  if (0 == arg.find("--")):
    indexEq = arg.find("=")
    if (-1 != indexEq):
      config[arg[2:indexEq]] = arg[indexEq + 1:]
  else:
    # XXX Currently only server has been checked for compilation under FreeBSD
    if arg != 'server': 
    	print("module %s not supported yet under FreeBSD" % arg)
    array_modules.append(arg)

if ("branch" in config):
  branch = config["branch"]

print("---------------------------------------------")
print("build branch: " + branch)
print("---------------------------------------------")

modules = " ".join(array_modules)
# XXX Currently only server has been checked for compilation under FreeBSD
if "" == modules:
  modules = "server"

print("---------------------------------------------")
print("build modules: " + modules)
print("---------------------------------------------")

build_tools_params = ["--branch", branch, 
                      "--module", modules, 
                      "--update", "1",
                      "--platform", "linux_64",
                      "--qt-dir", os.getcwd() + "/qt"]

base.cmd_in_dir("../..", "./configure.py", build_tools_params)
base.cmd_in_dir("../..", "./make.py")



