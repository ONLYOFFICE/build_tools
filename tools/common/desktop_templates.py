#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import base64

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

base.configure_common_apps()

def change_property(data_src, name, value):
  data = data_src
  creator_open = "<dc:" + name + ">"
  creator_close = "</dc:" + name + ">"
  open_tag_pos = data.find(creator_open)
  if open_tag_pos == -1:
    creator_close_to_find = "<dc:" + name + "/>"
  else:
    creator_close_to_find = "</dc:" + name + ">"
  close_tag_pos = data.find(creator_close_to_find)
  last_tag_pos = data.find("</cp:coreProperties>")

  if open_tag_pos != -1 and close_tag_pos != - 1:
    data = data[:open_tag_pos + len(creator_open)] + value + data[close_tag_pos:]
  elif close_tag_pos != - 1:
    data = data[:close_tag_pos] + creator_open + value + creator_close + data[close_tag_pos + len(creator_close_to_find):]
  else:
    data = data[:last_tag_pos] + creator_open + value + creator_close + data[last_tag_pos:]
  return data

def change_author_name(file_input):
  temp_dir = os.getcwd().replace("\\", "/") + "/temp"
  base.create_dir(temp_dir)

  app = "7za" if ("mac" == base.host_platform()) else "7z"
  base.cmd_exe(app, ["x", "-y", file_input, "-o" + temp_dir, "docProps/core.xml", "-r"])

  with open(temp_dir + "/docProps/core.xml", 'r', encoding='utf-8') as file:
    data = file.read()

  data = change_property(data, "creator", "")
  data = change_property(data, "lastModifiedBy", "")

  with open(temp_dir + "/docProps/core.xml", 'w', encoding='utf-8') as file:
    file.write(data)

  base.cmd_exe(app, ["a", "-r", file_input, temp_dir + "/docProps"])
  base.delete_dir(temp_dir)

def get_files(dir):
  arr_files = []
  for file in glob.glob(dir + "/*"):
    if base.is_file(file):
      arr_files.append(file)      
    elif base.is_dir(file):
      arr_files += get_files(file)
  return arr_files

def get_local_path(base, src_dir):
  test1 = base.replace("\\", "/")
  test2 = src_dir.replace("\\", "/")
  return test2[len(test1)+1:]

params = sys.argv[1:]

if (3 > len(params)):
  print("use: convert.py path_to_x2t_directory path_to_input_directory path_to_output_directory")
  exit(0)

base.configure_common_apps()

x2t_directory = params[0]
src_directory = params[1]
dst_directory = params[2]

if base.is_dir(dst_directory):
  base.delete_dir(dst_directory)
base.create_dir(dst_directory)

src_files = get_files(src_directory)

for file in src_files:
  directory = os.path.dirname(file)
  name = os.path.basename(file)
  directory_out_file = dst_directory + "/" + get_local_path(src_directory, directory)
  if not base.is_dir(directory_out_file):
    os.makedirs(directory_out_file, exist_ok=True)
  name_without_ext = os.path.splitext(name)[0]
  name_ext = os.path.splitext(name)[1][1:]

  dst_ext = name_ext
  if ("docx" == name_ext) or ("dotx" == name_ext):
    dst_ext = "dotx"
  elif ("pptx" == name_ext) or ("potx" == name_ext):
    dst_ext = "potx"
  elif ("xlsx" == name_ext) or ("xltx" == name_ext):
    dst_ext = "xltx"

  dst_name = name_without_ext
  if (len(dst_name) < 4) or (dst_name[0:4] != "[32]"):
    dst_name = "[32]" + base64.b32encode(name_without_ext.encode("utf-8")).decode("utf-8")

  dst_file = directory_out_file + "/" + dst_name + "." + dst_ext

  os.makedirs(directory_out_file, exist_ok=True)
  base.cmd_in_dir(x2t_directory, "x2t", [file, dst_file])

  change_author_name(dst_file)

  print(name_without_ext + " => " + dst_name)
