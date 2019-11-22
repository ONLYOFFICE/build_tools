import platform
import glob
import shutil
import os
import subprocess
import sys
import config

# common functions --------------------------------------
def get_script_dir(file=""):
  test_file = file
  if ("" == file):
    test_file = __file__
  scriptPath = os.path.realpath(test_file)
  scriptDir = os.path.dirname(scriptPath)
  return scriptDir

def host_platform():
  ret = platform.system().lower()
  if (ret == "darwin"):
    return "mac"
  return ret

def get_path(path):
  if "Windows" == host_platform():
    return path.replace("/", "\\")
  return path

def get_env(name):
  return os.getenv(name, "")

def set_env(name, value):
  os.environ[name] = value
  return

# file system -------------------------------------------
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

# system cmd methods ------------------------------------
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

# git ---------------------------------------------------
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

# qmake -------------------------------------------------
def qt_setup(platform):
  qt_dir = config.option("qt-dir") if (-1 == platform.find("_xp")) else config.option("qt-dir-xp")
  qt_dir = (qt_dir + "/" + config.options["compiler"]) if platform_is_32(platform) else (qt_dir + "/" + config.options["compiler_64"])
  set_env("QT_DEPLOY", qt_dir + "/bin")
  return qt_dir  

def qt_version():
  qt_dir = get_env("QT_DEPLOY")
  return qt_dir.split("/")[-2]

def qt_config(platform):
  config_param = config.option("module") + " " + config.option("config")
  if (-1 != platform.find("xp")):
      config_param += " build_xp"
  return config_param

def qt_major_version():
  qt_dir = get_env("QT_DEPLOY")
  return qt_dir.split("/")[-2].split(".")[0]

def qt_copy_lib(lib, dir):
  qt_dir = get_env("QT_DEPLOY")
  if ("windows" == host_platform()):
    copy_lib(qt_dir, dir, lib)
  else:
    copy_file(qt_dir + "/lib" + lib + ".so." + qt_version(), dir + "/lib" + lib + ".so." + qt_major_version())
  return

def _check_icu_common(dir, out):
  isExist = False
  for file in glob.glob(dir + "/libicu*"):
    isExist = True
    break

  if isExist:
    copy_files(dir + "/libicui18n*", out)
    copy_files(dir + "/libicuuc*", out)
    copy_files(dir + "/libicudata*", out)

  return isExist

def qt_copy_icu(out):
  tests = [get_env("QT_DEPLOY") + "/../lib", "/lib", "/lib/x86_64-linux-gnu", "/lib64", "/lib64/x86_64-linux-gnu"]
  tests += ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/lib64", "/usr/lib64/x86_64-linux-gnu"]
  tests += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]

  for test in tests:
    if (_check_icu_common(test, out)):
      return True

  return False

def qt_copy_plugin(name, out):
  src = get_env("QT_DEPLOY") + "/../plugins/" + name
  if not is_dir(src):
    return
    
  copy_dir(src, out + "/plugins")

  if ("windows" == host_platform()):
    for file in glob.glob(out + "/plugins/*d.dll"):
      fileCheck = file[0:-5] + ".dll"
      if is_file(fileCheck):
        delete_file(file)
    
  return

# common ------------------------------------------------
def is_windows():
  if "windows" == host_platform():
    return True
  return False

def platform_is_32(platform):
  if (-1 != platform.find("_32")):
    return True
  return False

# apps
def app_make():
  if is_windows():
    return "nmake"
  return "make"
