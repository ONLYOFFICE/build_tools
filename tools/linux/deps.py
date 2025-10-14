#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess

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
              "libncurses5",
              "libncurses6",
              "curl",
              "libxkbcommon-dev",
              "libxkbcommon-x11-dev",
              "libnotify-dev"]

  for package in packages:
    base.cmd("sudo", ["apt-get", "install", "-y", package], True)

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
  if (nodejs_cur < 16000):
    print("Node.js version cannot be less 16")
    print("Reinstall")
    base.run_as_bat(["curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - &&sudo apt-get install -y nodejs"])    
  else:
    print("OK")
    base.cmd("sudo", ["apt-get", "-y", "install", "npm", "yarn"], True)
  base.cmd("sudo", ["npm", "install", "-g", "grunt-cli"])
  base.cmd("sudo", ["npm", "install", "-g", "@yao-pkg/pkg"])

  # java
  java_error = base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-11-jdk"], True)
  if (0 != java_error):
    base.cmd("sudo", ["apt-get", "-y", "install", "software-properties-common"])
    base.cmd("sudo", ["add-apt-repository", "-y", "ppa:openjdk-r/ppa"])
    base.cmd("sudo", ["apt-get", "update"])
    base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-11-jdk"])
    base.cmd("sudo", ["update-alternatives", "--config", "java"])
    base.cmd("sudo", ["update-alternatives", "--config", "javac"])

  base.writeFile("./packages_complete", "complete")
  return

if __name__ == "__main__":
  install_deps()
