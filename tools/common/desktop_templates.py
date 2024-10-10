#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import glob
import base64

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

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

  print(name_without_ext + " => " + dst_name)
