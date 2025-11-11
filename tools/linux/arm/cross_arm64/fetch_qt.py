#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.dirname(__file__) + '../../../scripts')

import base # type: ignore


def make():
  qt_build_path = os.path.dirname(os.path.abspath(__file__)) + "/qt_cross_build/Qt-5.9.9"
  qt_binary_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/qt/qt_binary_linux_cross_arm64.7z"
  
  if not base.is_file(os.path.dirname(__file__) + "/qt_binary_linux_cross_arm64.7z"):
    base.download(qt_binary_url, os.path.dirname(__file__) + "/qt_binary_linux_cross_arm64.7z")
    
  if not base.is_dir(qt_build_path):
    os.makedirs(qt_build_path)
    base.cmd("tar", ["-xf", os.path.dirname(__file__) + "/qt_binary_linux_cross_arm64.7z", "-C", qt_build_path])

if __name__ == "__main__":
  make()