#!/usr/bin/env python

import sys
sys.path.append('../../../scripts')
import base
import os
import subprocess

base.cmd("git", ["clone", "https://github.com/NixOS/patchelf.git", "patchelf_dir"])
cur_dir = os.getcwd()
os.chdir("patchelf_dir")
base.cmd("git", ["checkout", "tags/0.17.2"])
base.cmd("./bootstrap.sh")
base.cmd("./configure")
base.replaceInFile("./src/Makefile.am", "AM_CXXFLAGS = ", "AM_CXXFLAGS = -static-libstdc++ -static-libgcc ")
base.cmd("make")
os.chdir(cur_dir)
if base.is_file("./patchelf"):
  base.delete_file("./patchelf")
base.copy_file("./patchelf_dir/src/patchelf", "./patchelf")
base.delete_dir("patchelf_dir")
