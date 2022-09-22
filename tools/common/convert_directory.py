#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import convert_common

params = sys.argv[1:]

if (4 > len(params)):
  print("use: convert_directory.py path_to_builder_directory path_to_input_files_directory path_to_output_files_directory format_ext [convert_params]")
  exit(0)

cur_path = os.getcwd()
base.configure_common_apps()

directory_x2t = params[0].replace("\\", "/")
directory_input = params[1].replace("\\", "/")
directory_output = params[2].replace("\\", "/")
format_ext = params[3]
convert_params = ""
if (5 == len(params)):
  convert_params = params[4]

input_files = []
for file in glob.glob(os.path.join(u"" + directory_input, u'*')):
  input_files.append(file.replace("\\", "/"))

directory_fonts = directory_x2t + "/sdkjs/common"
if not base.is_file(directory_fonts + "/AllFonts.js"):
  base.cmd_in_dir(directory_x2t, "docbuilder", [], True)

output_len = len(input_files)
output_cur = 1
for input_file in input_files:
  print("process [" + str(output_cur) + " of " + str(output_len) + "]: " + str(input_file.encode("utf-8")))
  output_file = os.path.join(directory_output, os.path.splitext(os.path.basename(input_file))[0]) + u"." + format_ext
  convert_common.convertFile(directory_x2t, input_file, output_file, convert_params)
  output_cur += 1
