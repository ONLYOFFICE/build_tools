#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob

params = sys.argv[1:]

if (5 != len(params)):
  print("use: thumbnails.py path_to_builder_directory path_to_input_files_directory path_to_output_files_directory width height")
  exit(0)

base.configure_common_apps()

directory_x2t = params[0].replace("\\", "/")
directory_input = params[1].replace("\\", "/")
directory_output = params[2].replace("\\", "/")
th_width = params[3]
th_height = params[4]

output_dir = directory_output + "/[" + str(th_width) + "x" + str(th_height) + "]"
if base.is_dir(output_dir):
  base.delete_dir(output_dir)
base.create_dir(output_dir)

input_files = []
for file in glob.glob(directory_input + "/*"):
  input_files.append(file.replace("\\", "/"))

#print(input_files)
temp_dir = os.getcwd().replace("\\", "/") + "/temp"
if base.is_dir(temp_dir):
  base.delete_dir(temp_dir)
base.create_dir(temp_dir)

directory_fonts = directory_x2t + "/sdkjs/common"
if not base.is_file(directory_fonts + "/AllFonts.js"):
  base.cmd_in_dir(directory_x2t, "docbuilder", [], True)

output_len = len(input_files)
output_cur = 1
for input_file in input_files:
  print("process [" + str(output_cur) + " of " + str(output_len) + "]: " + os.path.basename(input_file))
  xml_convert = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
  xml_convert += "<TaskQueueDataConvert>"
  xml_convert += ("<m_sFileFrom>" + input_file + "</m_sFileFrom>")
  xml_convert += ("<m_sFileTo>" + output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0] + ".zip</m_sFileTo>")
  xml_convert += "<m_nFormatTo>1029</m_nFormatTo>"
  xml_convert += ("<m_sAllFontsPath>" + directory_fonts + "/AllFonts.js</m_sAllFontsPath>")
  xml_convert += ("<m_sFontDir>" + directory_fonts + "</m_sFontDir>")
  xml_convert += "<m_sJsonParams>{&quot;spreadsheetLayout&quot;:{&quot;fitToWidth&quot;:1,&quot;fitToHeight&quot;:1}}</m_sJsonParams>"
  xml_convert += "<m_nDoctParams>1</m_nDoctParams>"
  xml_convert += "<m_oThumbnail><first>false</first></m_oThumbnail>"
  xml_convert += "<m_nDoctParams>1</m_nDoctParams>"
  xml_convert += ("<m_sTempDir>" + temp_dir + "</m_sTempDir>")
  xml_convert += "</TaskQueueDataConvert>"
  base.save_as_script(temp_dir + "/to.xml", [xml_convert])
  base.cmd_in_dir(directory_x2t, "x2t", [temp_dir + "/to.xml"], True)
  base.delete_dir(temp_dir)
  base.create_dir(temp_dir)
  base.extract(output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0] + ".zip", output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0])
  base.delete_file(output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0] + ".zip")
  output_cur += 1

base.delete_dir(temp_dir)