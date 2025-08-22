#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')

import base


def make():
  tar_path = "./arm_sysroot/sysroot_ubuntu_1604_arm64v8.tar.xz"
  sysroot_dir = "./arm_sysroot"
  sysroot_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/sysroot/sysroot_ubuntu_1604_arm64v8.tar.xz"
  
  if not base.is_file(tar_path):
    base.download(sysroot_url, tar_path)
    
  if not base.is_dir(sysroot_dir):
    os.makedirs(sysroot_dir)

  if not base.is_dir(sysroot_dir + "/sysroot_ubuntu_1604_arm64v8"):
    base.cmd("tar", ["-xf", tar_path, "-C", sysroot_dir])

if __name__ == "__main__":
  make()