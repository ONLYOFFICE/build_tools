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

cur_path = os.getcwd()
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
for file in glob.glob(os.path.join(u"" + directory_input, u'*')):
  input_files.append(file.replace("\\", "/"))

#print(input_files)
temp_dir = os.getcwd().replace("\\", "/") + "/temp"
if base.is_dir(temp_dir):
  base.delete_dir(temp_dir)
base.create_dir(temp_dir)

directory_fonts = directory_x2t + "/sdkjs/common"
if not base.is_file(directory_fonts + "/AllFonts.js"):
  base.cmd_in_dir(directory_x2t, "docbuilder", [], True)

json_params = "{'spreadsheetLayout':{'fitToWidth':1,'fitToHeight':1},"
json_params += "'documentLayout':{'drawPlaceHolders':true,'drawFormHighlight':true,'isPrint':true}}"
json_params = json_params.replace("'", "&quot;")

output_len = len(input_files)
output_cur = 1
for input_file in input_files:
  print("process [" + str(output_cur) + " of " + str(output_len) + "]: " + str(input_file.encode("utf-8")))
  output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0])
  xml_convert = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
  xml_convert += u"<TaskQueueDataConvert>"
  xml_convert += (u"<m_sFileFrom>" + input_file + u"</m_sFileFrom>")
  xml_convert += (u"<m_sFileTo>" + output_file + u".zip</m_sFileTo>")
  xml_convert += u"<m_nFormatTo>1029</m_nFormatTo>"
  xml_convert += (u"<m_sAllFontsPath>" + directory_fonts + u"/AllFonts.js</m_sAllFontsPath>")
  xml_convert += (u"<m_sFontDir>" + directory_fonts + u"</m_sFontDir>")
  xml_convert += (u"<m_sJsonParams>" + json_params + u"</m_sJsonParams>")
  xml_convert += u"<m_nDoctParams>1</m_nDoctParams>"
  xml_convert += u"<m_oThumbnail>"
  xml_convert += u"<first>false</first>"
  if ((0 != th_width) and (0 != th_height)):
    xml_convert += u"<aspect>0</aspect>"
    xml_convert += (u"<width>" + str(th_width) + u"</width>")
    xml_convert += (u"<height>" + str(th_height) + u"</height>")
  xml_convert += u"</m_oThumbnail>"
  xml_convert += u"<m_nDoctParams>1</m_nDoctParams>"
  xml_convert += (u"<m_sTempDir>" + temp_dir + u"</m_sTempDir>")
  xml_convert += u"</TaskQueueDataConvert>"
  base.save_as_script(temp_dir + "/to.xml", [xml_convert])
  base.cmd_in_dir(directory_x2t, "x2t", [temp_dir + "/to.xml"], True)
  base.delete_dir(temp_dir)
  base.create_dir(temp_dir)
  base.extract_unicode(output_file + u".zip", output_file)
  base.delete_file(output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0] + ".zip")
  output_cur += 1

base.delete_dir(temp_dir)
os.chdir(cur_path)