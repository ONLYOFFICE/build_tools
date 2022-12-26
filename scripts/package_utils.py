#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import glob
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import package_common as common

def host_platform():
  return platform.system().lower()

def is_windows():
  return host_platform() == "windows"

def is_macos():
  return host_platform() == "darwin"

def is_linux():
  return host_platform() == "linux"

def log(string, end='\n'):
  sys.stdout.write(string + end)
  sys.stdout.flush()
  return

def log_h1(string):
  line = "#" * (len(string) + 8)
  log("\n" + line + "\n### " + string + " ###\n" + line + "\n")
  return

def log_h2(string):
  log("\n### " + string + "\n")
  return

def log_h3(string):
  log("# " + string)
  return

def log_err(string):
  log("!!! " + string)
  return

def get_timestamp():
  return "%.f" % time.time()

def get_env(key, default=None):
  return os.getenv(key, default)

def set_env(key, value):
  os.environ[key] = value
  return

def get_cwd():
  return os.getcwd()

def set_cwd(path, verbose=True):
  if verbose:
    log("- change working dir:")
    log("    path: " + path)
  os.chdir(path)
  return

def get_path(path):
  if is_windows():
    return path.replace("/", "\\")
  return path

def get_abspath(path):
  return os.path.abspath(get_path(path))

def get_basename(path):
  return os.path.basename(path)

def get_dirname(path):
  return os.path.dirname(path)

def get_file_size(path):
  return os.path.getsize(path)

def get_script_dir(path):
  return get_dirname(os.path.realpath(path))

def is_file(path):
  return os.path.isfile(path)

def is_dir(path):
  return os.path.isdir(path)

def is_exist(path):
  if os.path.exists(path):
    return True
  return False

def glob_path(path):
  return glob.glob(path)

def glob_file(path):
  if glob.glob(path) and is_file(glob.glob(path)[0]):
    return glob.glob(path)[0]
  return

def get_md5(path):
  if os.path.exists(path):
    md5_hash = hashlib.md5()
    md5_hash.update(open(path, "rb").read())
    return md5_hash.hexdigest()
  return

def create_dir(path, verbose=True):
  if verbose:
    log("- create_dir:")
    log("    path: " + path)
  if not is_exist(path):
    os.makedirs(path)
  else:
    log_err("dir exist")
  return

def write_file(path, data, encoding='utf-8', verbose=True):
  if is_file(path):
    delete_file(path)
  if verbose:
    log("- write_file:")
    log("    path: " + path)
    log("    encoding: " + encoding)
    log("    data: |\n" + data)
  with codecs.open(path, 'w', encoding) as file:
    file.write(data)
  return

def replace_in_file(path, pattern, text_replace, encoding='utf-8', verbose=True):
  if verbose:
    log("- replace_in_file:")
    log("    path: " + path)
    log("    pattern: " + pattern)
    log("    replace: " + text_replace)
    log("    encoding: " + encoding)
  file_data = ""
  with codecs.open(get_path(path), "r", encoding) as file:
    file_data = file.read()
  file_data = re.sub(pattern, text_replace, file_data)
  delete_file(path)
  with codecs.open(get_path(path), "w", encoding) as file:
    file.write(file_data)
  return

def copy_file(src, dst, verbose=True):
  if verbose:
    log("- copy_file:")
    log("    src: " + src)
    log("    dst: " + dst)
  if is_file(dst):
    delete_file(dst)
  if not is_file(src):
    log_err("file not exist: " + src)
    return
  return shutil.copy2(get_path(src), get_path(dst))

def copy_files(src, dst, override=True, verbose=True):
  if verbose:
    log("- copy_files:")
    log("    src: " + src)
    log("    dst: " + dst)
    log("    override: " + str(override))
  for file in glob.glob(src):
    file_name = os.path.basename(file)
    if is_file(file):
      if override and is_file(dst + "/" + file_name):
        delete_file(dst + "/" + file_name)
      if not is_file(dst + "/" + file_name):
        if verbose:
          log(file + " : " + get_path(dst))
        shutil.copy2(file, get_path(dst))
    elif is_dir(file):
      if not is_dir(dst + "/" + file_name):
        create_dir(dst + "/" + file_name)
      copy_files(file + "/*", dst + "/" + file_name, override)
  return

def copy_dir(src, dst, override=True, verbose=True):
  if verbose:
    log("- copy_dir:")
    log("    src: " + src)
    log("    dst: " + dst)
    log("    override: " + str(override))
  if is_dir(dst):
    delete_dir(dst)
  try:
    shutil.copytree(get_path(src), get_path(dst))    
  except OSError as e:
    log_err('directory not copied. Error: %s' % e)
  return

def copy_dir_content(src, dst, filter_include = "", filter_exclude = "", verbose=True):
  if verbose:
    log("- copy_dir_content:")
    log("    src: " + src)
    log("    dst: " + dst)
    log("    include: " + filter_include)
    log("    exclude: " + filter_exclude)
  src_folder = src
  if ("/" != src[-1:]):
    src_folder += "/"
  src_folder += "*"
  for file in glob.glob(src_folder):
    basename = os.path.basename(file)
    if ("" != filter_include) and (-1 == basename.find(filter_include)):
      continue
    if ("" != filter_exclude) and (-1 != basename.find(filter_exclude)):
      continue
    if is_file(file):
      copy_file(file, dst, verbose=False)
    elif is_dir(file):
      copy_dir(file, dst + "/" + basename)
  return

def delete_file(path, verbose=True):
  if verbose:
    log("- delete_file:")
    log("    path: " + path)
  if not is_file(path):
    log_err("file not exist")
    return
  return os.remove(path)

def delete_dir(path, verbose=True):
  if verbose:
    log("- delete_dir:")
    log("    path: " + path)
  if not is_dir(path):
    log_err("dir not exist")
    return
  shutil.rmtree(path, ignore_errors=True)
  return

def delete_files(src, verbose=True):
  if verbose:
    log("- delete_files:")
    log("    pattern: " + src)
  for path in glob.glob(src):
    if verbose:
      log(path)
    if is_file(path):
      os.remove(path)
    elif is_dir(path):
      shutil.rmtree(path, ignore_errors=True)
  return

def set_summary(target, status):
  common.summary.append({target: status})
  return

def add_deploy_data(product, ptype, src, dst, bucket, region):
  common.deploy_data.append({
    "platform": common.platforms[common.platform]["title"],
    "product": product,
    "type": ptype,
    # "local": get_path(src),
    "size": get_file_size(get_path(src)),
    "bucket": bucket,
    "region": region,
    "key": dst
  })
  file = open(get_path(common.workspace_dir + "/deploy.json"), 'w')
  file.write(json.dumps(common.deploy_data, sort_keys=True, indent=4))
  file.close()
  return

def cmd(*args, **kwargs):
  if kwargs.get("verbose"):
    log("- cmd:")
    log("    command: " + " ".join(args))
    if kwargs.get("chdir"):
      log("    chdir: " + kwargs["chdir"])
    if kwargs.get("creates"):
      log("    creates: " + kwargs["creates"])
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    log_err("creates exist")
    return False
  if kwargs.get("chdir") and is_dir(kwargs["chdir"]):
    oldcwd = get_cwd()
    set_cwd(kwargs["chdir"])
  ret = subprocess.call(
      [i for i in args], stderr=subprocess.STDOUT, shell=True
  ) == 0
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd)
  return ret

def cmd_output(*args, **kwargs):
  if kwargs.get("verbose"):
    log("- cmd_output:")
    log("    command: " + " ".join(args))
  return subprocess.check_output(
      [i for i in args], stderr=subprocess.STDOUT, shell=True
  ).decode("utf-8")

def powershell(*args, **kwargs):
  if kwargs.get("verbose"):
    log("- powershell:")
    log("    command: " + " ".join(args))
    if kwargs.get("chdir"):
      log("    chdir: " + kwargs["chdir"])
    if kwargs.get("creates"):
      log("    creates: " + kwargs["creates"])
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return False
  args = ["powershell", "-Command"] + [i for i in args]
  ret = subprocess.call(
      args, stderr=subprocess.STDOUT, shell=True
  ) == 0
  return ret

def ps1(file, args=[], **kwargs):
  if kwargs.get("verbose"):
    log_h2("powershell cmdlet: " + file + " " + " ".join(args))
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return True
  ret = subprocess.call(
      ["powershell", file] + args, stderr=subprocess.STDOUT, shell=True
  ) == 0
  return ret

def download_file(url, path, md5, verbose=False):
  if verbose:
    log("- download_file:")
    log("    url: " + path)
    log("    path: " + url)
    log("    md5: " + md5)
  if is_file(path):
    if get_md5(path) == md5:
      log_err("file already exist (match checksum)")
      return True
    else:
      log_err("wrong checksum (%s), delete" % md5)
      os.remove(path)
  ret = powershell(
      "(New-Object System.Net.WebClient).DownloadFile('%s','%s')" % (url, path),
      verbose=True
  )
  md5_new = get_md5(path)
  if md5 != md5_new:
    log_err("checksum didn't match (%s != %s)" % (md5, md5_new))
    return False
  return ret

def sh(command, **kwargs):
  if kwargs.get("verbose"):
    log("- sh:")
    log("    command: " + command)
    if kwargs.get("chdir"):
      log("    chdir: " + kwargs["chdir"])
    if kwargs.get("creates"):
      log("    creates: " + kwargs["creates"])
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    log_err("creates exist")
    return False
  if kwargs.get("chdir") and is_dir(kwargs["chdir"]):
    oldcwd = get_cwd()
    set_cwd(kwargs["chdir"])
  ret = subprocess.call(
      command, stderr=subprocess.STDOUT, shell=True
  ) == 0
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd)
  return ret

def sh_output(command, **kwargs):
  if kwargs.get("verbose"):
    log("- sh_output:")
    log("    command: " + command)
  return subprocess.check_output(
      command, stderr=subprocess.STDOUT, shell=True
  ).decode("utf-8")
