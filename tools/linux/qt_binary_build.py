#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps

def install_qt():
  # qt
  if not base.is_file("./qt_source_5.9.9.tar.xz"):
    base.download("https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/qt/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")

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
