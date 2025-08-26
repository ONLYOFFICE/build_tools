#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../../../../scripts')

import base


def make():
  sysroot_dir = os.path.abspath(os.path.dirname(__file__) + "/arm_sysroot")
  tar_path = sysroot_dir + "/sysroot_ubuntu_1604_arm64v8.tar.xz"
  sysroot_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/sysroot/sysroot_ubuntu_1604_arm64v8.tar.xz"
  
  if not base.is_file(tar_path):
    base.download(sysroot_url, tar_path)
    
  if not base.is_dir(sysroot_dir):
    os.makedirs(sysroot_dir)

  if not base.is_dir(sysroot_dir + "/sysroot_ubuntu_1604_arm64v8"):
    base.cmd("tar", ["-xf", tar_path, "-C", sysroot_dir])

if __name__ == "__main__":
  make()