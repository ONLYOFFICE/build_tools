#!/usr/bin/env python

import argparse
import platform
import os
import sys
import glob
import shutil
import subprocess
import base

global git_dir, tsa_server, vcredist_links
git_dir = os.path.abspath(os.path.dirname(__file__) + "/../..")
tsa_server = "http://timestamp.digicert.com"
vcredist_links = {
  "2015": {
    "64": "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x64.exe",
    "32": "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x86.exe"
  },
  "2013": {
    "64": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
    "32": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe"
  }
}

def parse():
  parser = argparse.ArgumentParser(description='Build packages.')
  parser.add_argument("-P","--product", dest="product", type=str, action="store", help="Defines product")
  parser.add_argument("-S","--system", dest="system", type=str, action="store", help="Defines system")
  parser.add_argument("-T","--targets", dest="targets", type=str, nargs='+', action="store", help="Defines targets")
  parser.add_argument("-V","--version", dest="version", type=str, action="store", help="Defines version")
  parser.add_argument("-B","--build", dest="build", type=str, action="store", help="Defines build")
  parser.add_argument("-R","--branding", dest="branding_dir", type=str, action="store", help="Provides branding path")
  args = parser.parse_args()
  
  global product, system, targets, version, build, branding_dir, sign, clean
  product = args.product
  system = args.system
  targets = args.targets
  version = args.version # base.get_env("PRODUCT_VERSION")
  build = args.build # base.get_env("BUILD_NUMBER")
  branding_dir = args.branding_dir # base.get_env("BRANDING_DIR")
  return

def log(string, end='\n', bold=False):
  if bold:
    out = "\033[1m" + string + "\033[0m" + end
  else:
    out = string + end
  sys.stdout.write(out)
  sys.stdout.flush()
  return

def set_cwd(dir):
  log("- change working dir: " + dir)
  os.chdir(dir)
  return

def host_platform():
  return platform.system().lower()

def is_file(path):
  return os.path.isfile(path)

def is_dir(path):
  return os.path.isdir(path)

def is_exist(path):
  if os.path.exists(path):
    return True
  return False

def create_dir(path):
  log("- create dir: " + path)
  if not is_exist(path):
    os.makedirs(path)
  else:
    log("! dir exist")
  return

def write_file(path, data):
  if is_file(path):
    delete_file(path)
  log("- write file: " + path)
  with open(path, "w") as file:
    file.write(data)
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

def download(url, path):
  log("- download file: " + path + " < " + url)
  base.download(url, path)
  return

def cmd(prog, args=[], is_no_errors=False):
  log("- cmd: " + prog + " " + " ".join(args))
  base.cmd(prog, args, is_no_errors)
  return

def powershell(self, cmd):
  log("- pwsh: " + cmd)
  completed = subprocess.call(["powershell", "-Command", cmd], stderr=subprocess.STDOUT, shell=True)
  return completed

def get_platform(target):
  xp = (-1 != target.find("-xp"))
  if (-1 != target.find("-x64")):
    return { "machine": "64", "arch": "x64", "xp": xp }
  elif (-1 != target.find("-x86")):
    return { "machine": "32", "arch": "x86", "xp": xp }
  return
