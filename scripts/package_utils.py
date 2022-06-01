#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs
import glob
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import base

def parse():
  parser = argparse.ArgumentParser(description="Build packages.")
  parser.add_argument('-P', '--product', dest='product', type=str,
                      action='store', help="Defines product")
  parser.add_argument('-S', '--system', dest='system', type=str,
                      action='store', help="Defines system")
  parser.add_argument('-R', '--branding', dest='branding', type=str,
                      action='store', help="Provides branding path")
  parser.add_argument('-V', '--version', dest='version', type=str,
                      action='store', help="Defines version")
  parser.add_argument('-B', '--build', dest='build', type=str,
                      action='store', help="Defines build")
  parser.add_argument('-T', '--targets', dest='targets', type=str, nargs='+',
                      action='store', help="Defines targets")
  args = parser.parse_args()

  global product, system, targets, version, build, branding, clean, sign, deploy
  product = args.product
  system = args.system if (args.system is not None) else host_platform()
  targets = args.targets
  version = args.version if (args.version is not None) else get_env('PRODUCT_VERSION', '0.0.0')
  build = args.build if (args.build is not None) else get_env('BUILD_NUMBER', '0')
  branding = args.branding

  clean = 'clean' in targets
  sign = 'sign' in targets
  deploy = 'deploy' in targets
  return

def host_platform():
  return platform.system().lower()

def log(string, end='\n', bold=False):
  if bold:
    out = '\033[1m' + string + '\033[0m' + end
  else:
    out = string + end
  sys.stdout.write(out)
  sys.stdout.flush()
  return

def get_env(name, default=''):
  return os.getenv(name, default)

def set_env(name, value):
  os.environ[name] = value
  return

def set_cwd(dir):
  log("- change working dir: " + dir)
  os.chdir(dir)
  return

def get_path(*paths):
  arr = []
  for path in paths:
    if host_platform() == 'windows':
      arr += path.split('/')
    else:
      arr += [path]
  return os.path.join(*arr)

def get_abspath(*paths):
  arr = []
  for path in paths:
    arr += path.split('/')
  return os.path.abspath(os.path.join(*arr))

def is_file(path):
  return os.path.isfile(path)

def is_dir(path):
  return os.path.isdir(path)

def is_exist(path):
  if os.path.exists(path):
    return True
  return False

def get_dirname(path):
  return os.path.dirname(path)

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

def download_file(url, path):
  log("- download file: " + path + " < " + url)
  if is_file(path):
    os.remove(path)
  powershell(["Invoke-WebRequest", url, "-OutFile", path])
  return

def proc_open(command):
  log("- open process: " + command)
  popen = subprocess.Popen(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
  ret = {'stdout' : '', 'stderr' : ''}
  try:
    stdout, stderr = popen.communicate()
    popen.wait()
    ret['stdout'] = stdout.strip().decode('utf-8', errors='ignore')
    ret['stderr'] = stderr.strip().decode('utf-8', errors='ignore')
  finally:
    popen.stdout.close()
    popen.stderr.close()
  return ret

def cmd(prog, args=[], is_no_errors=False):  
  log("- cmd: " + prog + " " + ' '.join(args))
  ret = 0
  if host_platform() == 'windows':
    sub_args = args[:]
    sub_args.insert(0, get_path(prog))
    ret = subprocess.call(sub_args, stderr=subprocess.STDOUT, shell=True)
  else:
    command = prog
    for arg in args:
      command += (" \"%s\"" % arg)
    ret = subprocess.call(command, stderr=subprocess.STDOUT, shell=True)
  if ret != 0 and True != is_no_errors:
    sys.exit("! error (" + prog + "): " + str(ret))
  return ret

def run_ps1(file, args=[], verbose=False):
  if verbose:
    log("- powershell script: %s %s" % (file, ' '.join(args)))
  ret = subprocess.call(['powershell', file] + args,
                        stderr=subprocess.STDOUT,
                        shell=True)
  # if ret != 0:
  #   sys.exit("! error: " + str(ret))
  return ret

def powershell(cmd):
  log("- pwsh: " + ' '.join(cmd))
  ret = subprocess.call(['powershell', '-Command'] + cmd,
                        stderr=subprocess.STDOUT, shell=True)
  if ret != 0:
    sys.exit("! error: " + str(ret))
  return ret

def get_platform(target):
  xp = (-1 != target.find('-xp'))
  if (-1 != target.find('-x64')):
    return {'machine': "64", 'arch': "x64", 'xp': xp}
  elif (-1 != target.find('-x86')):
    return {'machine': "32", 'arch': "x86", 'xp': xp}
  return

global git_dir, out_dir, tsa_server, vcredist_links, tasks
git_dir = get_abspath(get_dirname(__file__), '../..')
out_dir = get_abspath(get_dirname(__file__), '../out')
timestamp = "%.f" % time.time()
tsa_server = "http://timestamp.digicert.com"
vcredist_links = {
  '2022': {
    '64': "https://aka.ms/vs/17/release/vc_redist.x64.exe",
    '32': "https://aka.ms/vs/17/release/vc_redist.x86.exe"
  },
  '2015': {
    '64': "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x64.exe",
    '32': "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x86.exe"
  },
  '2013': {
    '64': "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
    '32': "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe"
  }
}
tasks = []
