import platform
import shutil
import os
import subprocess
import sys

def get_script_dir():
  scriptPath = os.path.realpath(__file__)
  scriptDir = os.path.dirname(scriptPath)
  return scriptDir

def get_path( path ):
  if "Windows" == platform.system():
    return path.replace("/", "\\")
  return path

def is_file( path ):
  return os.path.isfile(get_path(path))

def is_dir( path ):
  return os.path.isdir(get_path(path))

def is_exist(path):
  return is_file(path) || is_dir(path)

def copy_file( src, dst ):
  return shutil.copy2(get_path(src), get_path(dst))

def delete_file( path ):
  return os.remove(get_path(path))

def create_dir( path ):
  path2 = get_path(path)
  if not os.path.exists(path2):
    os.makedirs(path2)
  return

def copy_dir( src, dst ):
  try:
    shutil.copytree(get_path(src), get_path(dst))    
  except OSError as e:
    print('Directory not copied. Error: %s' % e)

def delete_dir( path ):
  shutil.rmtree(get_path(path))

def cmd( prog, args )
  sub_args = args[:].insert(0, prog)
  ret = subprocess.call(sub_args, stderr=subprocess.STDOUT, shell=True)
  if ret != 0:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def bash( path )
  command = get_path(path)
  if ("Windows" == platform.system()):
    command += ".bat"
  else:
    command += ".sh"
  return cmd(command, [])

def get_native_platform():
  cur_system = platform.system()
  if "Windows" == cur_system:
    cur_system = "win_"
  elif "Linux" == cur_system:
    cur_system = "linux_"
  else:
    cur_system = "mac_"
  if platform.machine().endswith('64'):
    cur_system += cur_system + "64"
  else:
    cur_system += cur_system + "32"
  return cur_system

def host_platform():
  ret = platform.system.lower()
  if (ret == "darwin"):
    return "mac"
  return ret

def get_env(name):
  return os.environ.getenv(name, "")

def git_update( repo ):
  url = "https://github.com/ONLYOFFICE/" + repo + ".git"
  if config.options["git-protocol"] == "ssh":
    url = "git@github.com:ONLYOFFICE/" + repo + ".git"
  folder = base.get_script_dir() + "/../../" + repo
  if not base.is_dir(folder):
    base.cmd("git", ["clone", url, folder])
  old_cur = os.getcwd()
  os.chdir(folder)
  base.cmd("git", ["fetch"])
  base.cmd("git", ["checkout", "-f", config.options["branch"]])
  base.cmd("git", ["pull"])
  os.chdir(old_cur)