#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os

def install_deps():
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
              "libxrender-dev"]

  base.cmd("sudo", ["apt-get", "install", "-y"] + packages)

  # nodejs
  if not base.is_file("./node_js_setup_8.x"):
    base.download("https://deb.nodesource.com/setup_8.x", "./node_js_setup_8.x")
    base.cmd("sudo", ["bash", "./node_js_setup_8.x"])
    base.cmd("sudo", ["apt-get", "install", "-y", "nodejs"])
    base.cmd("sudo", ["npm", "install", "-g", "npm"])
    base.cmd("sudo", ["npm", "install", "-g", "grunt-cli"])

  # java
  base.cmd("sudo", ["apt-get", "-y", "install", "software-properties-common"])
  base.cmd("sudo", ["add-apt-repository", "-y", "ppa:openjdk-r/ppa"])
  base.cmd("sudo", ["apt-get", "update"])
  base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-8-jdk"])
  base.cmd("sudo", ["update-alternatives", "--config", "java"])
  base.cmd("sudo", ["update-alternatives", "--config", "javac"])
  return

def install_qt():
  # qt
  if not base.is_file("./qt_source_5.9.9.tar.xz"):
    base.download("http://download.qt.io/official_releases/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")

  if not base.is_dir("./qt-everywhere-opensource-src-5.9.9"):
    base.cmd("tar", ["-xf", "./qt_source_5.9.9.tar.xz"])

  qt_params = ["-opensource",
               "-confirm-license",
               "-release",
               "-shared",
               "-accessibility",
               "-prefix",
               "./../qt_build/gcc_64",
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

if not base.is_file("./node_js_setup_8.x"):
  print("install dependencies...")
  install_deps()  

if not base.is_dir("./qt_build"):  
  print("install qt...")
  install_qt()

build_tools_params = ["--branch", "master", 
                      "--module", "desktop builder server", 
                      "--update", "1",
                      "--qt-dir", os.getcwd() + "/qt_build"]

base.cmd_in_dir("../..", "./configure.py", build_tools_params)
base.cmd_in_dir("../..", "./make.py")



