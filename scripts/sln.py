#!/usr/bin/env python

import sys
sys.path.append('scripts')
import config
import json
import os

is_log = False

def is_exist_in_array(projects, proj):
  for p in projects:
    if p == proj:
      return True
  return False

def get_full_projects_list(json_data, list):
  result = []
  for rec in list:
    if rec in json_data:
      result += get_full_projects_list(json_data, json_data[rec])
    else:
      result.append(rec)
  return result

def adjust_project_params(params):
  ret_params = params
  
  # check aliases
  all_windows = []
  all_windows_xp = []
  all_linux = []
  all_mac = []
  all_android = []

  for i in config.platforms:
    if (0 == i.find("win")):
      all_windows.append(i)
      if (-1 != i.find("xp")):
        all_windows_xp.append(i)
    elif (0 == i.find("linux")):
      all_linux.append(i)
    elif (0 == i.find("mac")):
      all_mac.append(i)
    elif (0 == i.find("android")):
      all_android.append(i)

  if is_exist_in_array(params, "win"):
    ret_params += all_windows
  if is_exist_in_array(params, "!win"):
    ret_params += ["!" + x for x in all_windows]

  if is_exist_in_array(params, "win_xp"):
    ret_params += all_windows_xp
  if is_exist_in_array(params, "!win_xp"):
    ret_params += ["!" + x for x in all_windows_xp]

  if is_exist_in_array(params, "linux"):
    ret_params += all_linux
  if is_exist_in_array(params, "!linux"):
    ret_params += ["!" + x for x in all_linux]

  if is_exist_in_array(params, "mac"):
    ret_params += all_mac
  if is_exist_in_array(params, "!mac"):
    ret_params += ["!" + x for x in all_mac]

  if is_exist_in_array(params, "android"):
    ret_params += all_android
  if is_exist_in_array(params, "!android"):
    ret_params += ["!" + x for x in all_android]

  return ret_params

def get_projects(pro_json_path, platform):
  json_path = os.path.abspath(pro_json_path)
  data = json.load(open(json_path))

  root_dir_json = "../"
  if ("root" in data):
    root_dir_json = data["root"]

  root_dir = os.path.dirname(json_path)
  if ("/" != root_dir[-1] and "\\" != root_dir[-1]):
    root_dir += "/"
  root_dir += root_dir_json

  result = []
  modules = config.option("module").split(" ")
  for module in modules:
    if (module == ""):
      continue
    if not module in data:
      continue
    
    # check aliases to modules
    records_src = data[module]
    records = get_full_projects_list(data, records_src)

    #print(records)

    for rec in records:
      params = []
      record = rec
      if (0 == rec.find("[")):
        pos = rec.find("]")
        if (-1 == pos):
          continue
        record = rec[pos+1:]
        header = rec[1:pos].replace(" ", "")
        params_tmp = rec[1:pos].split(",")
        for par in params_tmp:
          if (par != ""):
            params.append(par)

        params = adjust_project_params(params)

      if is_exist_in_array(result, record):
        continue

      if is_log:
        print("params: " + ",".join(params))
        print("file: " + record)

      if is_exist_in_array(params, "!" + platform):
        continue

      platform_records = []
      platform_records += config.platforms
      platform_records += ["win", "win_xp", "linux", "mac", "android"]

      # if one platform exists => all needed must exists
      is_needed_platform_exist = False
      for pl in platform_records:
        if is_exist_in_array(params, pl):
          is_needed_platform_exist = True
          break

      # if one config exists => all needed must exists
      is_needed_config_exist = False
      for item in params:
        if (0 == item.find("!")):
          continue
        if is_exist_in_array(platform_records, item):
          continue
        is_needed_config_exist = True
        break

      if is_needed_platform_exist:
        if not is_exist_in_array(params, platform):
          continue

      config_params = config.option("config").split(" ") + config.option("features").split(" ")
      config_params = [x for x in config_params if x]      

      is_append = True
      for conf in config_params:
        if is_exist_in_array(params, "!" + conf):
          is_append = False
          break
        if is_needed_config_exist and not is_exist_in_array(params, conf):
          is_append = False
          break
      if is_append:
        result.append(root_dir + record)

  # delete duplicates
  old_results = result
  result = []

  map_results = set()
  for item in old_results:
    proj = item.replace("\\", "/")
    if proj in map_results:
      continue
    map_results.add(proj)
    result.append(proj)

  if is_log:
    print(result)
  return result

# test example
if __name__ == '__main__':
  # test
  config.parse()

  is_log = True
  projects = get_projects("./../sln.json", "win_64")
