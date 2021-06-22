#!/usr/bin/env python

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
  current_branch = base.run_command(command)['stdout']
  os.chdir(cur_dir)
  return current_branch

def install_deps():
  if base.is_file("./packages_complete"):
    return

  # dependencies
  packages = ["apt-transport-https", 
              "autoconf2.13",
              "build-essential",
              "ca-certificates",
              "cmake",
              "curl",
              "git",
              "glib-2.0-dev",
              "libglu1-mesa-dev",
              "libgtk-3-dev",
              "libpulse-dev",
              "libtool",
              "p7zip-full",
              "subversion",
              "gzip",
              "libasound2-dev",
              "libatspi2.0-dev",
              "libcups2-dev",
              "libdbus-1-dev",
              "libicu-dev",
              "libglu1-mesa-dev",
              "libgstreamer1.0-dev",
              "libgstreamer-plugins-base1.0-dev",
              "libx11-xcb-dev",
              "libxcb*",
              "libxi-dev",
              "libxrender-dev",
              "libxss1",
              "libncurses5"]

  base.cmd("sudo", ["apt-get", "install", "-y"] + packages)

  # nodejs
  base.cmd("sudo", ["apt-get", "install", "-y", "nodejs"])
  nodejs_cur = 0
  try:
    nodejs_version = base.run_command('node -v')['stdout']
    nodejs_cur_version_major = int(nodejs_version.split('.')[0][1:])
    nodejs_cur_version_minor = int(nodejs_version.split('.')[1])
    nodejs_cur = nodejs_cur_version_major * 1000 + nodejs_cur_version_minor
    print("Installed Node.js version: " + str(nodejs_cur_version_major) + "." + str(nodejs_cur_version_minor))
  except:
    nodejs_cur = 1
  if (nodejs_cur < 10020):
    print("Node.js version cannot be less 10.20")
    print("Reinstall")
    if (base.is_dir("./node_js_setup_10.x")):
      base.delete_dir("./node_js_setup_10.x")
    base.cmd("sudo", ["apt-get", "remove", "--purge", "-y", "nodejs"])
    base.download("https://deb.nodesource.com/setup_10.x", "./node_js_setup_10.x")
    base.cmd('curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -')
    base.cmd("sudo", ["bash", "./node_js_setup_10.x"])
    base.cmd("sudo", ["apt-get", "install", "-y", "nodejs"])
    base.cmd("sudo", ["npm", "install", "-g", "npm@6"])
  else:
    print("OK")
    base.cmd("sudo", ["apt-get", "-y", "install", "npm", "yarn"], True)
  base.cmd("sudo", ["npm", "install", "-g", "grunt-cli"])
  base.cmd("sudo", ["npm", "install", "-g", "pkg"])

  # java
  java_error = base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-11-jdk"], True)
  if (0 != java_error):
    java_error = base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-8-jdk"], True)
  if (0 != java_error):
    base.cmd("sudo", ["apt-get", "-y", "install", "software-properties-common"])
    base.cmd("sudo", ["add-apt-repository", "-y", "ppa:openjdk-r/ppa"])
    base.cmd("sudo", ["apt-get", "update"])
    base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-8-jdk"])
    base.cmd("sudo", ["update-alternatives", "--config", "java"])
    base.cmd("sudo", ["update-alternatives", "--config", "javac"])
    
  base.writeFile("./packages_complete", "complete")
  return

def install_qt():
  # qt
  if not base.is_file("./qt_source_5.9.9.tar.xz"):
    base.download("https://download.qt.io/archive/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")

  if not base.is_dir("./qt-everywhere-opensource-src-5.9.9"):
    base.cmd("tar", ["-xf", "./qt_source_5.9.9.tar.xz"])

  qt_params = ["-opensource",
               "-confirm-license",
               "-release",
               "-shared",
               "-accessibility",
               "-prefix",
               "./../qt_build/Qt-5.9.9/gcc_64",
               "-qt-zlib",
               "-qt-libpng",
               "-qt-libjpeg",
               "-qt-xcb",
               "-qt-pcre",
               "-no-sql-sqlite",
               "-no-qml-debug",
               "-gstreamer", "1.0",
               "-nomake", "examples",
               "-nomake", "tests",
               "-skip", "qtenginio",
               "-skip", "qtlocation",
               "-skip", "qtserialport",
               "-skip", "qtsensors",
               "-skip", "qtxmlpatterns",
               "-skip", "qt3d",
               "-skip", "qtwebview",
               "-skip", "qtwebengine"]

  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "./configure", qt_params)
  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", ["-j", "4"])
  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", ["install"])
  return

if not base.is_file("./node_js_setup_10.x"):
  print("install dependencies...")
  install_deps()  

if not base.is_dir("./qt_build"):  
  print("install qt...")
  install_qt()

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
                      "--update", "1",
                      "--qt-dir", os.getcwd() + "/qt_build/Qt-5.9.9"]

base.cmd_in_dir("../..", "./configure.py", build_tools_params)
base.cmd_in_dir("../..", "./make.py")


base.cmd("sudo", ["apt-get", "-y", "install", "dpkg-dev", "debhelper"], True)
base.cmd('mkdir -p ../../out/package')
base.cmd('cp -a ../../debianpackage ../../out/package/onlyoffice')
base.cmd_in_dir("../../out/package/onlyoffice", "sudo", ["dpkg-buildpackage", "-b", "-us", "-uc"])

