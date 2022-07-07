#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import glob
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import time

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
  line = "-" * (len(string) + 8)
  log("\n" + line + "\n--- " + string + " ---\n" + line + "\n")
  return

def log_h2(string):
  log("--- " + string)
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
    log_h2("change working dir: " + path)
  os.chdir(path)
  return

def get_path(path):
  if is_windows():
    return path.replace("/", "\\")
  return path

def get_abspath(path):
  return os.path.abspath(get_path(path))

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

def get_md5(path):
  if os.path.exists(path):
    md5_hash = hashlib.md5()
    md5_hash.update(open(path, "rb").read())
    return md5_hash.hexdigest()
  return

def create_dir(path):
  log("- create dir: " + path)
  if not is_exist(path):
    os.makedirs(path)
  else:
    log("! dir exist")
  return

def write_file(path, data, encoding='utf-8'):
  if is_file(path):
    delete_file(path)
  log("- write file: " + path)
  with codecs.open(path, 'w', encoding) as file:
    file.write(data)
  return

def write_template(src, dst, encoding='utf-8', **kwargs):
  template = Template(open(src).read())
  if is_file(dst):
    os.remove(dst)
  log("- write template: " + dst + " < " + src)
  with codecs.open(dst, 'w', encoding) as file:
    file.write(template.render(**kwargs))
  return

def replace_in_file(path, pattern, textReplace, encoding='utf-8'):
  log("- replace in file: " + path + \
      "\n  pattern: " + pattern + \
      "\n  replace: " + textReplace)
  filedata = ""
  with codecs.open(get_path(path), "r", encoding) as file:
    filedata = file.read()
  filedata = re.sub(pattern, textReplace, filedata)
  delete_file(path)
  with codecs.open(get_path(path), "w", encoding) as file:
    file.write(filedata)
  return

def copy_file(src, dst):
  log("- copy file: " + dst + " < " + src)
  if is_file(dst):
    delete_file(dst)
  if not is_file(src):
    log("! file not exist: " + src)
    return
  return shutil.copy2(get_path(src), get_path(dst))

def copy_files(src, dst, override=True):
  log("- copy files: " + dst + " < " + src)
  for file in glob.glob(src):
    file_name = os.path.basename(file)
    if is_file(file):
      if override and is_file(dst + "/" + file_name):
        delete_file(dst + "/" + file_name)
      if not is_file(dst + "/" + file_name):
        copy_file(file, dst)
    elif is_dir(file):
      if not is_dir(dst + "/" + file_name):
        create_dir(dst + "/" + file_name)
      copy_files(file + "/*", dst + "/" + file_name, override)
  return

def copy_dir(src, dst):
  if is_dir(dst):
    delete_dir(dst)
  try:
    shutil.copytree(get_path(src), get_path(dst))    
  except OSError as e:
    log('! Directory not copied. Error: %s' % e)
  return

def copy_dir_content(src, dst, filterInclude = "", filterExclude = ""):
  log("- copy dir content: " + src + " " + dst + " " + filterInclude + " " + filterExclude)
  src_folder = src
  if ("/" != src[-1:]):
    src_folder += "/"
  src_folder += "*"
  for file in glob.glob(src_folder):
    basename = os.path.basename(file)
    if ("" != filterInclude) and (-1 == basename.find(filterInclude)):
      continue
    if ("" != filterExclude) and (-1 != basename.find(filterExclude)):
      continue
    if is_file(file):
      copy_file(file, dst)
    elif is_dir(file):
      copy_dir(file, dst + "/" + basename)
  return

def delete_file(path):
  log("- delete file: " + path)
  if not is_file(path):
    log("! file not exist")
    return
  return os.remove(path)

def delete_dir(path):
  log("- delete dir: " + path)
  if not is_dir(path):
    log("! dir not exist")
    return
  shutil.rmtree(path, ignore_errors=True)
  return

def delete_files(src):
  for path in glob.glob(src):
    if is_file(path):
      delete_file(path)
    elif is_dir(path):
      delete_dir(path)
  return

def cmd(*args, **kwargs):
  if kwargs.get("verbose"):
    log_h2("cmd: " + " ".join(args))
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return 0
  if kwargs.get("chdir") and is_dir(kwargs["chdir"]):
    oldcwd = get_cwd()
    set_cwd(kwargs["chdir"])
  ret = subprocess.call(
      [i for i in args], stderr=subprocess.STDOUT, shell=True
  )
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd)
  return ret

def cmd_output(*args, **kwargs):
  if kwargs.get("verbose"):
    log_h2("cmd output: " + " ".join(args))
  return subprocess.check_output(
      [i for i in args], stderr=subprocess.STDOUT, shell=True
  ).decode("utf-8")

def powershell(*args, **kwargs):
  if kwargs.get("verbose"):
    log_h2("powershell: " + " ".join(args))
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return 0
  args = ["powershell", "-Command"] + [i for i in args]
  ret = subprocess.call(
      args, stderr=subprocess.STDOUT, shell=True
  )
  return ret

def ps1(file, args=[], **kwargs):
  if kwargs.get("verbose"):
    log_h2("powershell cmdlet: " + file + " " + " ".join(args))
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return 0
  ret = subprocess.call(
      ["powershell", file] + args, stderr=subprocess.STDOUT, shell=True
  )
  return ret

def download_file(url, path, md5, verbose=False):
  if verbose:
    log("download file: %s < %s (%s)" % (path, url, md5))
  if is_file(path):
    if get_md5(path) == md5:
      log("! file already exist (match checksum)")
      return 0
    else:
      log("! wrong checksum (%s), delete" % md5)
      os.remove(path)
  ret = powershell("(New-Object System.Net.WebClient).DownloadFile('%s','%s')" % (url, path), verbose=True)
  md5_new = get_md5(path)
  if md5 != md5_new:
    log("! checksum didn't match (%s != %s)" % (md5, md5_new))
    return 1
  return ret

def sh(command, **kwargs):
  if kwargs.get("verbose"):
    log_h2("sh: " + command)
  return subprocess.call(command, stderr=subprocess.STDOUT, shell=True)

def sh_output(command, **kwargs):
  if kwargs.get("verbose"):
    log_h2("sh output: " + command)
  return subprocess.check_output(
      command, stderr=subprocess.STDOUT, shell=True
  ).decode("utf-8")
