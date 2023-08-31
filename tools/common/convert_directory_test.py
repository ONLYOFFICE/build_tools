#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import convert_common

params = sys.argv[1:]

if (5 > len(params)):
  print("use: convert_directory.py path_to_builder_directory path_to_sdkjs_directory editor_type path_to_input_files_directory path_to_output_files_directory")
  exit(0)

cur_path = os.getcwd()
base.configure_common_apps()

directory_x2t = params[0].replace("\\", "/")
directory_sdkjs = params[1].replace("\\", "/")
editor_type = params[2].replace("\\", "/")
directory_input = params[3].replace("\\", "/")
directory_output = params[4].replace("\\", "/")

input_files = [os.path.join(dirpath, f)
    for dirpath, dirnames, files in os.walk(directory_input)
    for f in files]

output_len = len(input_files)
output_cur = 1
for input_file in input_files:
  print("process [" + str(output_cur) + " of " + str(output_len) + "]: " + str(input_file.encode("utf-8")))
  output_file = os.path.join(directory_output, os.path.basename(input_file))
  base.cmd_in_dir(directory_x2t, "test", [directory_sdkjs, editor_type, input_file, output_file], True)
  output_cur += 1
