#!/usr/bin/env python

import sys
sys.path.append('../../build_tools/scripts')
import base
import os

args = sys.argv[1:]

if (1 > len(args)):
  print("Please use min.py PATH_TO_SCRIPT.js")
  exit(0)

script_path = args[0]
script_path = os.path.abspath(script_path)
script_dir = os.path.dirname(script_path)

script_name = os.path.splitext(os.path.basename(script_path))[0]
script_path_min = os.path.join(script_dir, script_name + ".min.js")

#compilation_level = "WHITESPACE_ONLY"
compilation_level = "SIMPLE_OPTIMIZATIONS"
base.cmd("java", ["-jar", "../../sdkjs/build/node_modules/google-closure-compiler-java/compiler.jar", 
                  "--compilation_level", compilation_level,
                  "--js_output_file", script_path_min,
                  "--js", script_path])

dev_content = base.readFile(script_path)
license = dev_content[0:dev_content.find("*/")+2]
min_content = base.readFile(script_path_min)
base.delete_file(script_path_min)
base.writeFile(script_path_min, license + "\n\n" + min_content)
