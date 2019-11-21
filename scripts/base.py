import platform
import glob
import shutil
import os
import subprocess
import sys
import config

def get_script_dir(file=""):
  test_file = file
  if ("" == file):
    test_file = __file__
  scriptPath = os.path.realpath(test_file)
  scriptDir = os.path.dirname(scriptPath)
  return scriptDir

def get_path(path):
  if "Windows" == platform.system():
    return path.replace("/", "\\")
  return path

def is_file(path):
  return os.path.isfile(get_path(path))

def is_dir(path):
  return os.path.isdir(get_path(path))

def is_exist(path):
  if is_file(path) or is_dir(path):
    return True
  return False

def copy_file(src, dst):
  if is_file(dst):
    delete_file(dst)
  if not is_file(src):
    return
  return shutil.copy2(get_path(src), get_path(dst))

def copy_files(src, dst):
  for file in glob.glob(src):
    copy_file(file, dst)

def delete_file(path):
  return os.remove(get_path(path))

def create_dir(path):
  path2 = get_path(path)
  if not os.path.exists(path2):
    os.makedirs(path2)
  return

def copy_dir(src, dst):
  if is_dir(dst):
    delete_dir(dst)
  try:
    shutil.copytree(get_path(src), get_path(dst))    
  except OSError as e:
    print('Directory not copied. Error: %s' % e)

def delete_dir(path):
  shutil.rmtree(get_path(path))

def copy_lib(src, dst, name):
  lib_ext = ".so"
  if ("windows" == host_platform()):
    lib_ext = ".dll"
  elif ("mac" == host_platform()):
    lib_ext = ".dylib"
  copy_file(src + "/lib" + name + lib_ext, dst + "/lib" + name + lib_ext)
  return

def copy_exe(src, dst, name):
  exe_ext = ""
  if ("windows" == host_platform()):
    exe_ext = ".exe"
  copy_file(src + "/" + name + exe_ext, dst + "/" + name + exe_ext)
  return

def cmd(prog, args):  
  ret = 0
  if ("windows" == host_platform()):
    sub_args = args[:]
    sub_args.insert(0, get_path(prog))
    ret = subprocess.call(sub_args, stderr=subprocess.STDOUT, shell=True)
  else:
    command = prog
    for arg in args:
      command += (" \"" + arg + "\"")
    ret = subprocess.call(command, stderr=subprocess.STDOUT, shell=True)
  if ret != 0:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def bash(path):
  command = get_path(path)
  command += (".bat" if "windows" == host_platform() else ".sh")
  return cmd(command, [])

def host_platform():
  ret = platform.system().lower()
  if (ret == "darwin"):
    return "mac"
  return ret

def get_env(name):
  return os.getenv(name, "")

def set_env(name, value):
  os.environ[name] = value
  return

def git_update(repo):
  url = "https://github.com/ONLYOFFICE/" + repo + ".git"
  if config.option("git-protocol") == "ssh":
    url = "git@github.com:ONLYOFFICE/" + repo + ".git"
  folder = get_script_dir() + "/../../" + repo
  if not is_dir(folder):
    cmd("git", ["clone", url, folder])
  old_cur = os.getcwd()
  os.chdir(folder)
  cmd("git", ["fetch"])
  cmd("git", ["checkout", "-f", config.option("branch")])
  cmd("git", ["pull"])
  os.chdir(old_cur)

def get_qt_version():
  qtDir = get_env("QT_DEPLOY")
  return qtDir.split("/")[-2]

def get_qt_major_version():
  qtDir = get_env("QT_DEPLOY")
  return qtDir.split("/")[-2].split(".")[0]

def copy_qt_lib(lib, dir):
  qtDir = get_env("QT_DEPLOY")
  if ("windows" == host_platform()):
    copy_lib(qtDir, dir, lib)
  else:
    copy_file(qtDir + "/lib" + lib + ".so." + get_qt_version(), dir + "/lib" + lib + ".so." + get_qt_major_version())
  return

def _checkICU_common(dir, out):
  isExist = False
  for file in glob.glob(dir + "/libicu*"):
    isExist = True
    break

  if isExist:
    copy_files(dir + "/libicui18n*", out)
    copy_files(dir + "/libicuuc*", out)
    copy_files(dir + "/libicudata*", out)

  return isExist

def copy_qt_icu(out):
  tests = [get_env("QT_DEPLOY") + "/../lib", "/lib", "/lib/x86_64-linux-gnu", "/lib64", "/lib64/x86_64-linux-gnu"]
  tests += ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/lib64", "/usr/lib64/x86_64-linux-gnu"]
  tests += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]

  for test in tests:
    if (_checkICU_common(test, out)):
      return True

  return False

def copy_qt_plugin(name, out):
  src = get_env("QT_DEPLOY") + "/../plugins/" + name
  if not is_dir(src):
    return
    
  copy_dir(src, out + "/plugins")

  for file in glob.glob(out + "/plugins/*d.dll"):
    fileCheck = file[0:-5] + ".dll"
    if is_file(fileCheck):
      delete_file(file)
    
  return
