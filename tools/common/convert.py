#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import convert_common

params = sys.argv[1:]

if (3 > len(params)):
  print("use: convert.py path_to_builder_directory path_to_input_file path_to_output_file [params]")
  exit(0)

base.configure_common_apps()

directory_x2t = params[0].replace("\\", "/")
file_input = params[1].replace("\\", "/")
file_output = params[2].replace("\\", "/")
convert_params = ""
if 4 == len(params):
  convert_params = params[3]

directory_fonts = directory_x2t + "/sdkjs/common"
if not base.is_file(directory_fonts + "/AllFonts.js"):
  base.cmd_in_dir(directory_x2t, "docbuilder", [], True)

convert_common.convertFile(directory_x2t, file_input, file_output, convert_params)
