#!/usr/bin/env python

import sys
sys.path.append('../../../scripts')
import base
import os

def docker_build(build_dir):
  image_name = "qt-arm64"
  base.cmd("docker", ["build", "-t", image_name, "."])
  base.cmd("docker", ["run", "--rm", "-v", build_dir + ":/build", image_name])
  base.cmd("docker", ["image", "rm", image_name])
  return

if __name__ == "__main__":
  args = sys.argv
  if len(args) < 2:
    print('Usage: python build_qt.py /path/to/build/dir')
    exit(1)

  build_dir = args[1]
  if not base.is_dir(build_dir):
    base.create_dir(build_dir)

  abs_build_path = os.path.abspath(build_dir)
  docker_build(abs_build_path)
