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

def get_relpath(path, rel_path):
  return os.path.relpath(get_path(path), get_path(rel_path))

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

def get_hash_sha256(path):
  if os.path.exists(path):
    h = hashlib.sha256()
    h.update(open(path, "rb").read())
    return h.hexdigest()
  return

def get_hash_sha1(path):
  if os.path.exists(path):
    h = hashlib.sha1()
    h.update(open(path, "rb").read())
    return h.hexdigest()
  return

def get_hash_md5(path):
  if os.path.exists(path):
    h = hashlib.md5()
    h.update(open(path, "rb").read())
    return h.hexdigest()
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
    delete_file(dst, False)
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

def copy_dir(src, dst, verbose=True, symlinks=False):
  if verbose:
    log("- copy_dir:")
    log("    src: " + src)
    log("    dst: " + dst)
  shutil.copytree(src, dst, symlinks=symlinks)
  return

def copy_dir_content(src, dst, filter_include = "", filter_exclude = "", verbose=True):
  if verbose:
    log("- copy_dir_content:")
    log("    src: " + src)
    log("    dst: " + dst)
    log("    include: " + filter_include)
    log("    exclude: " + filter_exclude)
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if ("" != filter_include) and (-1 == item.find(filter_include)):
      continue
    if ("" != filter_exclude) and (-1 != item.find(filter_exclude)):
      continue
    if os.path.isdir(s):
      shutil.copytree(s, d)
    else:
      shutil.copy2(s, d)
    log(item)
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

def remove_all_symlinks(dir):
  for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
    for name in files:
      path = os.path.join(root, name)
      if os.path.islink(path):
        os.unlink(path)
    
    for name in list(dirs):
      path = os.path.join(root, name)
      if os.path.islink(path):
        os.unlink(path)
        dirs.remove(name)
  return

def set_summary(target, status):
  common.summary.append({target: status})
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
    set_cwd(kwargs["chdir"], verbose=False)
  ret = subprocess.call(
      [i for i in args], stderr=subprocess.STDOUT, shell=True
  ) == 0
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd, verbose=False)
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
    log("- ps1: " + file + " " + " ".join(args))
  if kwargs.get("creates") and is_exist(kwargs["creates"]):
    return True
  ret = subprocess.call(
    ["powershell", "-ExecutionPolicy", "ByPass", "-File", file] + args,
    stderr=subprocess.STDOUT, shell=True
  ) == 0
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
    set_cwd(kwargs["chdir"], verbose=False)
  ret = subprocess.call(
      command, stderr=subprocess.STDOUT, shell=True
  ) == 0
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd, verbose=False)
  return ret

def sh_output(command, **kwargs):
  if kwargs.get("verbose"):
    log("- sh_output:")
    log("    command: " + command)
    if kwargs.get("chdir"):
      log("    chdir: " + kwargs["chdir"])
  if kwargs.get("chdir") and is_dir(kwargs["chdir"]):
    oldcwd = get_cwd()
    set_cwd(kwargs["chdir"], verbose=False)
  ret = subprocess.check_output(
      command, stderr=subprocess.STDOUT, shell=True
  ).decode("utf-8")
  log(ret)
  if kwargs.get("chdir") and oldcwd:
    set_cwd(oldcwd, verbose=False)
  return ret

def s3_upload(src, dst, **kwargs):
  if not is_file(src):
    log_err("file not exist: " + src)
    return False
  metadata = "sha256=" + get_hash_sha256(src) \
          + ",sha1=" + get_hash_sha1(src) \
          + ",md5=" + get_hash_md5(src)
  args = ["aws"]
  if kwargs.get("endpoint_url"):
    args += ["--endpoint-url", kwargs["endpoint_url"]]
  args += ["s3", "cp", "--no-progress"]
  if kwargs.get("acl"):
    args += ["--acl", kwargs["acl"]]
  args += ["--metadata", metadata, src, dst]
  if is_windows():
    ret = cmd(*args, verbose=True)
  else:
    ret = sh(" ".join(args), verbose=True)
  return ret

def s3_copy(src, dst, **kwargs):
  args = ["aws"]
  if kwargs.get("endpoint_url"):
    args += ["--endpoint-url", kwargs["endpoint_url"]]
  args += ["s3", "cp", "--no-progress"]
  if kwargs.get("acl"):
    args += ["--acl", kwargs["acl"]]
  args += [src, dst]
  if is_windows():
    ret = cmd(*args, verbose=True)
  else:
    ret = sh(" ".join(args), verbose=True)
  return ret
