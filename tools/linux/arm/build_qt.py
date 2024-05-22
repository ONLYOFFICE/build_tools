#!/usr/bin/env python

import sys
import os
import argparse

__dir__name__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__name__ + '/../../../scripts')
import base

def docker_build(image_name, dockerfile_dir, build_dir):
  base.cmd("docker", ["build", "-t", image_name, dockerfile_dir])
  base.cmd("docker", ["run", "--rm", "-v", build_dir + ":/build", image_name])
  base.cmd("docker", ["image", "rm", image_name])
  return

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Build qt for linux arm architecture')
  parser.add_argument('build_dir', help='the path to build directory (directory may not exist)')
  parser.add_argument('-a', '--arch', action='store', help='target architecture (arm32 or arm64)', choices=['arm32', 'arm64'], required=True)
  args = parser.parse_args()

  build_dir = args.build_dir
  if base.is_dir(build_dir):
    base.delete_dir(build_dir)
  base.create_dir(build_dir)

  abs_build_path = os.path.abspath(build_dir)
  arch = args.arch
  docker_build('qt-' + arch, __dir__name__ + "/" + arch, abs_build_path)
