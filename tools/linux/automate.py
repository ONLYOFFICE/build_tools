#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base

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
            "libgtk3.0-dev",
            "libpulse-dev",
            "libtool",
            "p7zip-full",
            "subversion"]

base.cmd("sudo", ["apt-get", "install", "-y"] + packages)

# nodejs
base.cmd("curl", ["-sL", "https://deb.nodesource.com/setup_8.x", "|", "sudo", "-E", "bash", "-"])
base.cmd("sudo", ["apt-get", "install", "-y", "nodejs"])
base.cmd("sudo", ["npm", "install", "-g", "npm"])
base.cmd("sudo", ["npm", "install", "-g", "grunt-cli"])

# java
base.cmd("sudo", ["apt-get", "-y", "install", "software-properties-common"])
base.cmd("sudo", ["add-apt-repository", "ppa:openjdk-r/ppa"])
base.cmd("sudo", ["apt-get", "update"])
base.cmd("sudo", ["apt-get", "-y", "install", "openjdk-8-jdk"])
base.cmd("sudo", ["update-alternatives", "--config", "java"])
base.cmd("sudo", ["update-alternatives", "--config", "javac"])

# qt
base.download("http://download.qt.io/official_releases/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")
base.extract("./qt_source_5.9.9.tar.xz", "./qt_source_5.9.9")

qt_params = ["-opensource",
             "-confirm-license",
             "-release",
             "-shared",
             "-accessibility",
             "-prefix",
             "./../qt_build",
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

base.cmd_in_dir("qt_source_5.9.9", "./configure", qt_params)

build_tools_params = ["--branch", "master", 
                      "--module", "desktop builder server", 
                      "--update", "1",
                      "--qt-dir", os.getcwd() + "/qt_source_5.9.9/Qt-5.9.9"]

base.cmd_in_dir("../../build_tools", "./configure.py", [])
base.cmd_in_dir("../../build_tools", "./make.py")



