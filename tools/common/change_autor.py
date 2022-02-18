#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import shutil

params = sys.argv[1:]

if (3 > len(params)):
  print("use: change_autor.py path_to_input_files_directory path_to_output_files_directory author_name")
  exit(0)

cur_path = os.getcwd()
base.configure_common_apps()

directory_input = params[0].replace("\\", "/")
directory_output = params[1].replace("\\", "/")
author_name = params[2]

input_files = []
for file in glob.glob(os.path.join(u"" + directory_input, u'*')):
  input_files.append(file.replace("\\", "/"))

temp_dir = os.getcwd().replace("\\", "/") + "/temp"

def change_author_name(file_dist, output_file, author_name):
  app = "7za" if ("mac" == base.host_platform()) else "7z"
  base.cmd_exe(app, ["x", "-y", file_dist, "-o" + temp_dir, "docProps\\core.xml", "-r"])

  with open(temp_dir + "/docProps/core.xml", 'r') as file:
    data = file.read()

  creator_open = "<dc:creator>"
  creator_close = "</dc:creator>"
  open_tag_pos = data.find(creator_open)
  if open_tag_pos == -1:
    creator_close_to_find = "<dc:creator/>"
  else:
    creator_close_to_find = "</dc:creator>"
  close_tag_pos = data.find(creator_close_to_find)
  last_tag_pos = data.find("</cp:coreProperties>")

  if open_tag_pos != -1 and close_tag_pos != - 1:
    data = data[:open_tag_pos + len(creator_open)] + author_name + data[close_tag_pos:]
  elif close_tag_pos != - 1:
    data = data[:close_tag_pos] + creator_open + author_name + creator_close + data[close_tag_pos + len(creator_close_to_find):]
  else:
    data = data[:last_tag_pos] + creator_open + author_name + creator_close + data[last_tag_pos:]

  lastModified_open = "<cp:lastModifiedBy>"
  lastModified_close = "</cp:lastModifiedBy>"
  open_tag_pos = data.find(lastModified_open)
  if open_tag_pos == -1:
    lastModified_close_to_find = "<cp:lastModifiedBy/>"
  else:
    lastModified_close_to_find = "</cp:lastModifiedBy>"
  close_tag_pos = data.find(lastModified_close_to_find)
  last_tag_pos = data.find("</cp:coreProperties>")

  if open_tag_pos != -1 and close_tag_pos != - 1:
    data = data[:open_tag_pos + len(lastModified_open)] + author_name + data[close_tag_pos:]
  elif close_tag_pos != - 1:
    data = data[:close_tag_pos] + lastModified_open + author_name + lastModified_close + data[close_tag_pos + len(lastModified_close_to_find):]
  else:
    data = data[:last_tag_pos] + lastModified_open + author_name + lastModified_close + data[last_tag_pos:]

  with open(temp_dir + "/docProps/core.xml", 'w') as file:
    file.write(data)

  shutil.copyfile(file_dist, output_file)
  base.cmd_exe(app, ["a", "-r", output_file, temp_dir + "\\docProps"])

output_len = len(input_files)
output_cur = 1
for input_file in input_files:
  if base.is_dir(temp_dir):
    base.delete_dir(temp_dir)
  base.create_dir(temp_dir)
  print("process [" + str(output_cur) + " of " + str(output_len) + "]: " + str(input_file.encode("utf-8")))
  output_file = os.path.join(directory_output, os.path.splitext(os.path.basename(input_file))[0]) + u"." + input_file.split(".")[-1]
  change_author_name(input_file, output_file, author_name)
  base.delete_dir(temp_dir)
  output_cur += 1
