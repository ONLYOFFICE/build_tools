#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8_87"
if not base.is_dir(base_dir):
  base.create_dir(base_dir)

os.chdir(base_dir)
if not base.is_dir("depot_tools"):
  base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])

os.environ["PATH"] = base_dir + "/depot_tools" + os.pathsep + os.environ["PATH"]

if not base.is_dir("v8"):
  base.cmd("./depot_tools/fetch", ["v8"], True)
  base.cmd("./depot_tools/gclient", ["sync", "-r", "8.7.220.25"], True)
  base.cmd("gclient", ["sync", "--force"], True)

os.chdir("v8")

gn_args = ["target_cpu=\\\"x64\\\"", 
           "v8_target_cpu=\\\"x64\\\"",
           "v8_static_library=true",
           "is_component_build=false",
           "v8_monolithic=true",
           "v8_use_external_startup_data=false",
           "use_custom_libcxx=false",
           "is_debug=false"]

base.cmd2("gn", ["gen", "out.gn/mac_64", "--args=\"" + " ".join(gn_args) + "\""])
base.cmd("ninja", ["-C", "out.gn/mac_64"])
