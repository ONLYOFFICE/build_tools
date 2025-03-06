#!/usr/bin/env python

import platform
import struct
import glob
import shutil
import os
import fnmatch
import subprocess
import sys
import config
import codecs
import re
import stat
import json

__file__script__path__ = os.path.dirname( os.path.realpath(__file__))

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

def is_os_64bit():
  return platform.machine().endswith('64')

def is_os_arm():
  if -1 == platform.machine().find('arm'):
    return False
  return True

def get_platform():
  return platform.machine().lower()

def is_python_64bit():
  return (struct.calcsize("P") == 8)

def get_path(path):
  if "windows" == host_platform():
    return path.replace("/", "\\")
  return path

def get_env(name):
  return os.getenv(name, "")

def set_env(name, value):
  os.environ[name] = value
  return

def configure_common_apps(file=""):
  if ("windows" == host_platform()):
    os.environ["PATH"] = get_script_dir(file) + "/../tools/win/7z" + os.pathsep + get_script_dir(file) + "/../tools/win/curl" + os.pathsep + get_script_dir(file) + "/../tools/win/vswhere" + os.pathsep + os.environ["PATH"]
  elif ("mac" == host_platform()):
    os.environ["PATH"] = get_script_dir(file) + "/../tools/mac" + os.pathsep + os.environ["PATH"]
  return

def check_build_version(dir):
  if ("" == get_env("PRODUCT_VERSION")):
    version_number = readFile(dir + "/version")
    if ("" != version_number):
      version_number = version_number.replace("\r", "")
      version_number = version_number.replace("\n", "")
      set_env("PRODUCT_VERSION", version_number)
  if ("" == get_env("BUILD_NUMBER")):
    set_env("BUILD_NUMBER", "0")      
  return

def print_info(info=""):
  print("------------------------------------------")
  print(info)
  print("------------------------------------------")
  return

def print_error(error=""):
  print("\033[91m" + error + "\033[0m")

def print_list(list):
  print('[%s]' % ', '.join(map(str, list)))
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
    print("copy warning [file not exist]: " + src)
    return
  return shutil.copy2(get_path(src), get_path(dst))

def move_file(src, dst):
  if is_file(dst):
    delete_file(dst)
  if not is_file(src):
    print("move warning [file not exist]: " + src)
    return
  return shutil.move(get_path(src), get_path(dst))

def copy_files(src, dst, override=True):
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

def move_files(src, dst, override=True):
  for file in glob.glob(src):
    file_name = os.path.basename(file)
    if is_file(file):
      if override and is_file(dst + "/" + file_name):
        delete_file(dst + "/" + file_name)
      if not is_file(dst + "/" + file_name):
        move_file(file, dst)
    elif is_dir(file):
      if not is_dir(dst + "/" + file_name):
        create_dir(dst + "/" + file_name)
      move_files(file + "/*", dst + "/" + file_name, override)
  return

def copy_dir_content(src, dst, filterInclude = "", filterExclude = ""):
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
  if not is_file(path):
    print("delete warning [file not exist]: " + path)
    return
  return os.remove(get_path(path))

def delete_exe(path):
  return os.remove(get_path(path) + (".exe" if "windows" == host_platform() else ""))

def find_file(path, pattern):
  for root, dirnames, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, pattern):
      return os.path.join(root, filename)

def find_files(path, pattern):
  result = []
  for root, dirnames, filenames in os.walk(path):
    for filename in fnmatch.filter(filenames, pattern):
      result.append(os.path.join(root, filename))
  return result

def create_dir(path):
  path2 = get_path(path)
  if not os.path.exists(path2):
    os.makedirs(path2)
  return

def move_dir(src, dst):
  if is_dir(dst):
    delete_dir(dst)
  if is_dir(src):
    copy_dir(src, dst)
    delete_dir(src)
  return

def copy_dir(src, dst):
  if is_dir(dst):
    delete_dir(dst)
  try:
    shutil.copytree(get_path(src), get_path(dst))
  except:
    if ("windows" == host_platform()) and copy_dir_windows(src, dst):
      return
    print("Directory not copied")
  return

def copy_dir_windows(src, dst):
  if is_dir(dst):
    delete_dir(dst)
  err = cmd("robocopy", [get_path(src), get_path(dst), "/e", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"], True)
  if (1 == err):
    return True
  return False

def delete_dir_with_access_error(path):
  def delete_file_on_error(func, path, exc_info):
    if ("windows" != host_platform()):
      if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
      return
    elif (0 != path.find("\\\\?\\")):
      # abspath not work with long names
      full_path = path
      drive_pos = full_path.find(":")
      if (drive_pos < 0) or (drive_pos > 2):
        full_path = os.getcwd() + "\\" + full_path
      else:
        full_path = full_path
      if (len(full_path) >= 260):
        full_path = "\\\\?\\" + full_path
      if not os.access(full_path, os.W_OK):
        os.chmod(full_path, stat.S_IWUSR)
      func(full_path)
    return
  if not is_dir(path):
    print("delete warning [folder not exist]: " + path)
    return
  shutil.rmtree(os.path.normpath(get_path(path)), ignore_errors=False, onerror=delete_file_on_error)
  return

def delete_dir(path):
  if not is_dir(path):
    print("delete warning [folder not exist]: " + path)
    return
  if ("windows" == host_platform()):
    delete_dir_with_access_error(path)
  else:
    shutil.rmtree(get_path(path), ignore_errors=True)
  return

def copy_lib(src, dst, name):
  if (config.check_option("config", "bundle_dylibs")) and is_dir(src + "/" + name + ".framework"):
    copy_dir(src + "/" + name + ".framework", dst + "/" + name + ".framework")

    if (config.check_option("config", "bundle_xcframeworks")) and is_dir(src + "/simulator/" + name + ".framework"):
        create_dir(dst + "/simulator")
        copy_dir(src + "/simulator/" + name + ".framework", dst + "/simulator/" + name + ".framework")

        if is_dir(dst + "/" + name + ".xcframework"):
          delete_dir(dst + "/" + name + ".xcframework")

        cmd("xcodebuild", ["-create-xcframework", 
            "-framework", dst + "/" + name + ".framework", 
            "-framework", dst + "/simulator/" + name + ".framework", 
            "-output", dst + "/" + name + ".xcframework"])

        delete_dir(dst + "/" + name + ".framework")
        delete_dir(dst + "/simulator/" + name + ".framework")
        delete_dir(dst + "/simulator")

    return

  lib_ext = ".so"
  if ("windows" == host_platform()):
    lib_ext = ".dll"
  elif ("mac" == host_platform()):
    lib_ext = ".dylib"
  file_src = src + "/"
  if not ("windows" == host_platform()):
    file_src += "lib"
  file_src += name
  if not is_file(file_src + lib_ext):
    if is_file(file_src + ".a"):
      lib_ext = ".a"
    elif is_file(file_src + ".lib"):
      lib_ext = ".lib"
    elif is_file(file_src + ".so"):
      lib_ext = ".so"

  lib_dst = dst + "/"
  if not ("windows" == host_platform()):
    lib_dst += "lib"

  copy_file(file_src + lib_ext, lib_dst + name + lib_ext)
  return

def copy_exe(src, dst, name):
  exe_ext = ""
  if ("windows" == host_platform()):
    exe_ext = ".exe"
  copy_file(src + "/" + name + exe_ext, dst + "/" + name + exe_ext)
  return

def readFileCommon(path):
  file_data = ""
  try:
    with open(get_path(path), "r") as file:
      file_data = file.read()
  except Exception as e:
    with open(get_path(path), "r", encoding="utf-8") as file:
      file_data = file.read()
  return file_data

def writeFileCommon(path, data):
  file_data = ""
  try:
    with open(get_path(path), "w") as file:
      file.write(data)
  except Exception as e:
    with open(get_path(path), "w", encoding="utf-8") as file:
      file.write(data)
  return

def replaceInFile(path, text, textReplace):
  if not is_file(path):
    print("[replaceInFile] file not exist: " + path)
    return
  filedata = readFileCommon(path)
  filedata = filedata.replace(text, textReplace)
  delete_file(path)
  writeFileCommon(path, filedata)
  return
def replaceInFileUtf8(path, text, textReplace):
  if not is_file(path):
    print("[replaceInFile] file not exist: " + path)
    return
  filedata = ""
  with open(get_path(path), "rb") as file:
    filedata = file.read().decode("UTF-8")
  filedata = filedata.replace(text, textReplace)
  delete_file(path)
  with open(get_path(path), "wb") as file:
    file.write(filedata.encode("UTF-8"))
  return
def replaceInFileRE(path, pattern, textReplace):
  if not is_file(path):
    print("[replaceInFile] file not exist: " + path)
    return
  filedata = readFileCommon(path)
  filedata = re.sub(pattern, textReplace, filedata)
  delete_file(path)
  writeFileCommon(path, filedata)
  return

def readFile(path):
  if not is_file(path):
    return ""
  return readFileCommon(path)

def writeFile(path, data):
  if is_file(path):
    delete_file(path)
  writeFileCommon(path, data)
  return

# system cmd methods ------------------------------------
def cmd(prog, args=[], is_no_errors=False):  
  ret = 0
  if ("windows" == host_platform()):
    sub_args = args[:]
    sub_args.insert(0, get_path(prog))
    ret = subprocess.call(sub_args, stderr=subprocess.STDOUT, shell=True)
  else:
    command = prog
    for arg in args:
      command += (" \"" + arg.replace('\"', '\\\"') + "\"")
    ret = subprocess.call(command, stderr=subprocess.STDOUT, shell=True)
  if ret != 0 and True != is_no_errors:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def cmd2(prog, args=[], is_no_errors=False):  
  ret = 0
  command = prog if ("windows" != host_platform()) else get_path(prog)
  for arg in args:
    command += (" " + arg)
  print(command)
  ret = subprocess.call(command, stderr=subprocess.STDOUT, shell=True)
  if ret != 0 and True != is_no_errors:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def cmd_exe(prog, args, is_no_errors=False):
  prog_dir = os.path.dirname(prog)
  env_dir = os.environ
  if ("linux" == host_platform()):
    old = os.getenv("LD_LIBRARY_PATH", "")
    env_dir["LD_LIBRARY_PATH"] = prog_dir + ("" if "" == old else (":" + old))
  elif ("mac" == host_platform()):
    old = os.getenv("DYLD_LIBRARY_PATH", "")
    env_dir["DYLD_LIBRARY_PATH"] = prog_dir + ("" if "" == old else (":" + old))

  ret = 0
  if ("windows" == host_platform()):
    sub_args = args[:]
    sub_args.insert(0, get_path(prog + ".exe"))
    process = subprocess.Popen(sub_args, stderr=subprocess.STDOUT, shell=True, env=env_dir)
    ret = process.wait()
  else:
    command = prog
    for arg in args:
      command += (" \"" + arg.replace('\"', '\\\"') + "\"")
    process = subprocess.Popen(command, stderr=subprocess.STDOUT, shell=True, env=env_dir)
    ret = process.wait()
  if ret != 0 and True != is_no_errors:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def cmd_in_dir(directory, prog, args=[], is_no_errors=False):
  dir = get_path(directory)
  cur_dir = os.getcwd()
  os.chdir(dir)
  ret = cmd(prog, args, is_no_errors)
  os.chdir(cur_dir)
  return ret

def cmd_in_dir_qemu(platform, directory, prog, args=[], is_no_errors=False):
  if (platform == "linux_arm64"):
    return cmd_in_dir(directory, "qemu-aarch64", ["-L", "/usr/aarch64-linux-gnu", prog] + args, is_no_errors)
  if (platform == "linux_arm32"):
    return cmd_in_dir(directory, "qemu-arm", ["-L", "/usr/arm-linux-gnueabi", prog] + args, is_no_errors)
  return 0

def cmd_and_return_cwd(prog, args=[], is_no_errors=False):
  cur_dir = os.getcwd()
  ret = cmd(prog, args, is_no_errors)
  os.chdir(cur_dir)
  return ret

def run_command(sCommand):
  popen = subprocess.Popen(sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  result = {'stdout' : '', 'stderr' : '', 'returncode' : 0}
  try:
    stdout, stderr = popen.communicate()
    popen.wait()
    result['stdout'] = stdout.strip().decode('utf-8', errors='ignore')
    result['stderr'] = stderr.strip().decode('utf-8', errors='ignore')
    result['returncode'] = popen.returncode
  finally:
    popen.stdout.close()
    popen.stderr.close()
  
  return result

def run_command_in_dir(directory, sCommand):
  host = host_platform()
  if (host == 'windows'):
    dir = get_path(directory)
    cur_dir = os.getcwd()
    os.chdir(dir)

  ret = run_command(sCommand)

  if (host == 'windows'):
    os.chdir(cur_dir)
  return ret
  
def exec_command_in_dir(directory, sCommand):
  host = host_platform()
  if (host == 'windows'):
    dir = get_path(directory)
    cur_dir = os.getcwd()
    os.chdir(dir)

  ret = os.system(sCommand)

  if (host == 'windows'):
    os.chdir(cur_dir)
  return ret

def run_process(args=[]):
  subprocess.Popen(args)

def run_process_in_dir(directory, args=[]):
  dir = get_path(directory)
  cur_dir = os.getcwd()
  os.chdir(dir)
  run_process(args)
  os.chdir(cur_dir)

# nodejs ------------------------------------------------
def run_nodejs(args=[]):
  args.insert(0, 'node')
  run_process(args)

def run_nodejs_in_dir(directory, args=[]):
  args.insert(0, 'node')
  run_process_in_dir(directory, args)

def bash(path):
  command = get_path(path)
  command += (".bat" if "windows" == host_platform() else ".sh")
  return cmd(command, [])

def get_cwd():
  return os.getcwd()

def set_cwd(dir):
  os.chdir(dir)
  return

# git ---------------------------------------------------
def git_get_origin():
  cur_dir = os.getcwd()
  os.chdir(get_script_dir() + "/../")
  ret = run_command("git config --get remote.origin.url")["stdout"]
  os.chdir(cur_dir)
  return ret

def git_is_ssh():
  git_protocol = config.option("git-protocol")
  if (git_protocol == "https"):
    return False
  if (git_protocol == "ssh"):
    return True
  origin = git_get_origin()
  if (git_protocol == "auto") and (origin.find(":ONLYOFFICE/") != -1):
    return True
  return False

def get_ssh_base_url():
  cur_origin = git_get_origin()
  ind = cur_origin.find(":ONLYOFFICE/")
  if (ind == -1):
    return "git@github.com:ONLYOFFICE/"
  return cur_origin[:ind+12]

def git_update(repo, is_no_errors=False, is_current_dir=False, git_owner=""):
  print("[git] update: " + repo)
  owner = git_owner if git_owner else "ONLYOFFICE"
  url = "https://github.com/" + owner + "/" + repo + ".git"
  if git_is_ssh():
    url = get_ssh_base_url() + repo + ".git"
  folder = get_script_dir() + "/../../" + repo
  if is_current_dir:
    folder = repo
  is_not_exit = False
  if not is_dir(folder):
    retClone = cmd("git", ["clone", url, folder], is_no_errors)
    if retClone != 0:
      return
    is_not_exit = True
  old_cur = os.getcwd()
  os.chdir(folder)
  cmd("git", ["fetch"], False if ("1" != config.option("update-light")) else True)
  if is_not_exit or ("1" != config.option("update-light")):
    retCheckout = cmd("git", ["checkout", "-f", config.option("branch")], True)
    if (retCheckout != 0):
      print("branch does not exist...")
      print("switching to master...")
      cmd("git", ["checkout", "-f", "master"])
    cmd("git", ["submodule", "update", "--init", "--recursive"], True)
  if (0 != config.option("branch").find("tags/")):
    cmd("git", ["pull"], False if ("1" != config.option("update-light")) else True)
    cmd("git", ["submodule", "update", "--recursive", "--remote"], True)
  os.chdir(old_cur)
  return

def get_repositories():
  result = {}
  result["core"] = [False, False]
  result["sdkjs"] = [False, False]
  result.update(get_sdkjs_addons())
  result["onlyoffice.github.io"] = [False, False]
  result["web-apps"] = [False, False]
  result["dictionaries"] = [False, False]
  result["core-fonts"] = [False, False]

  if config.check_option("module", "server"):
    result.update(get_web_apps_addons())

  if config.check_option("module", "builder"):
    result["document-templates"] = [False, False]

  if config.check_option("module", "desktop"):
    result["desktop-sdk"] = [False, False]
    result["desktop-apps"] = [False, False]
    result["document-templates"] = [False, False]

  if (config.check_option("module", "server")):
    result["server"] = [False, False]
    result.update(get_server_addons())
    result["document-server-integration"] = [False, False]
    result["document-templates"] = [False, False]

  get_branding_repositories(result)
  return result

def get_branding_repositories(checker):
  modules = ["core", "server", "mobile", "desktop", "builder"]
  for mod in modules:
    if not config.check_option("module", mod):
      continue
    name = "repositories_" + mod
    repos = config.option(name).rsplit(", ")
    for repo in repos:
      if (repo != ""):
        checker[repo] = [False, False]
  return

def create_pull_request(branches_to, repo, is_no_errors=False, is_current_dir=False):
  print("[git] create pull request: " + repo)
  url = "https://github.com/ONLYOFFICE/" + repo + ".git"
  if git_is_ssh():
    url = get_ssh_base_url() + repo + ".git"
  folder = get_script_dir() + "/../../" + repo
  if is_current_dir:
    folder = repo
  is_not_exit = False
  if not is_dir(folder):
    retClone = cmd("git", ["clone", url, folder], is_no_errors)
    if retClone != 0:
      return
    is_not_exit = True
  old_cur = os.getcwd()
  os.chdir(folder)
  branch_from = config.option("branch")
  cmd("git", ["checkout", "-f", branch_from], is_no_errors)
  cmd("git", ["pull"], is_no_errors)
  for branch_to in branches_to:
    if "" != run_command("git log origin/" + branch_to + "..origin/" + branch_from)["stdout"]:
      cmd("git", ["checkout", "-f", branch_to], is_no_errors)
      cmd("git", ["pull"], is_no_errors)
      cmd("gh", ["pr", "create", "--base", branch_to, "--head", branch_from, "--title", "Merge branch " + branch_from + " to " + branch_to, "--body", ""], is_no_errors)
      if 0 != cmd("git", ["merge", "origin/" + branch_from, "--no-ff", "--no-edit"], is_no_errors):
        print_error("[git] Conflicts merge " + "origin/" + branch_from + " to " + branch_to + " in repo " + url)
        cmd("git", ["merge", "--abort"], is_no_errors)
      else:
        cmd("git", ["push"], is_no_errors)
      
  os.chdir(old_cur)
  return

def update_repositories(repositories):
  for repo in repositories:
    value = repositories[repo]
    current_dir = value[1]
    if current_dir == False:
      git_update(repo, value[0], False)
    else:
      if is_dir(current_dir + "/.git"):
        delete_dir_with_access_error(current_dir);
        delete_dir(current_dir)
      if not is_dir(current_dir):
        create_dir(current_dir)
      cur_dir = os.getcwd()
      os.chdir(current_dir)
      git_update(repo, value[0], True)
      os.chdir(cur_dir)

def git_dir():
  if ("windows" == host_platform()):
    return run_command("git --info-path")['stdout'] + "/../../.."

def get_prefix_cross_compiler_arm64():
  cross_compiler_arm64 = config.option("arm64-toolchain-bin")
  if is_file(cross_compiler_arm64 + "/aarch64-linux-gnu-g++") and is_file(cross_compiler_arm64 + "/aarch64-linux-gnu-gcc"):
    return "aarch64-linux-gnu-"
  if is_file(cross_compiler_arm64 + "/aarch64-unknown-linux-gnu-g++") and is_file(cross_compiler_arm64 + "/aarch64-unknown-linux-gnu-gcc"):
    return "aarch64-unknown-linux-gnu-"
  return ""

def get_gcc_version():
  gcc_version_major = 4
  gcc_version_minor = 0
  gcc_version_str = run_command("gcc -dumpfullversion -dumpversion")['stdout']
  if (gcc_version_str != ""):
    try:
      gcc_ver = gcc_version_str.split(".")
      gcc_version_major = int(gcc_ver[0])
      gcc_version_minor = int(gcc_ver[1])
    except Exception as e:
      gcc_version_major = 4
      gcc_version_minor = 0
  return gcc_version_major * 1000 + gcc_version_minor

# qmake -------------------------------------------------
def qt_setup(platform):
  compiler = config.check_compiler(platform)
  qt_dir = config.option("qt-dir") if (-1 == platform.find("_xp")) else config.option("qt-dir-xp")

  # qt bug
  if (host_platform() == "mac"):
    for compiler_folder in glob.glob(qt_dir + "/*"):
      if is_dir(compiler_folder):
        old_path_file = compiler_folder + "/mkspecs/features/toolchain.prf"
        new_path_file = compiler_folder + "/mkspecs/features/toolchain.prf.bak"
        if (is_file(old_path_file) and not is_file(new_path_file)):
          try:
            copy_file(old_path_file, new_path_file)
            copy_file(get_script_dir() + "/../tools/mac/toolchain.prf", old_path_file)
          except IOError as e:
            print("Unable to copy file: " + old_path_file)

  compiler_platform = compiler["compiler"] if platform_is_32(platform) else compiler["compiler_64"]
  qt_dir = qt_dir + "/" + compiler_platform

  if (0 == platform.find("linux_arm")) and not is_dir(qt_dir):
    if ("gcc_arm64" == compiler_platform):
      qt_dir = config.option("qt-dir") + "/gcc_64"
    if ("gcc_arm" == compiler_platform):
      qt_dir = config.option("qt-dir") + "/gcc"

  set_env("QT_DEPLOY", qt_dir + "/bin")

  if ("linux_arm64" == platform):
    cross_compiler_arm64 = config.option("arm64-toolchain-bin")
    if ("" != cross_compiler_arm64):
      set_env("ARM64_TOOLCHAIN_BIN", cross_compiler_arm64)
      set_env("ARM64_TOOLCHAIN_BIN_PREFIX", get_prefix_cross_compiler_arm64())

  return qt_dir  

def qt_version():
  qt_dir = get_env("QT_DEPLOY")
  qt_dir = qt_dir.split("/")[-3]
  return "".join(i for i in qt_dir if (i.isdigit() or i == "."))

def check_congig_option_with_platfom(platform, option_name):
  if config.check_option("config", option_name):
    return True
  if (0 == platform.find("win")) and config.check_option("config_addon_windows", option_name):
    return True
  elif (0 == platform.find("linux")) and config.check_option("config_addon_linux", option_name):
    return True
  elif (0 == platform.find("mac")) and config.check_option("config_addon_macos", option_name):
    return True
  elif (0 == platform.find("ios")) and config.check_option("config_addon_ios", option_name):
    return True
  elif (0 == platform.find("android")) and config.check_option("config_addon_android", option_name):
    return True
  return False

def correct_makefile_after_qmake(platform, file):
  if (0 == platform.find("android")):
    if ("android_arm64_v8a" == platform):
      replaceInFile(file, "_arm64-v8a.a", ".a")
      replaceInFile(file, "_arm64-v8a.so", ".so")
    if ("android_armv7" == platform):
      replaceInFile(file, "_armeabi-v7a.a", ".a")
      replaceInFile(file, "_armeabi-v7a.so", ".so")
    if ("android_x86_64" == platform):
      replaceInFile(file, "_x86_64.a", ".a")
      replaceInFile(file, "_x86_64.so", ".so")
    if ("android_x86" == platform):
      replaceInFile(file, "_x86.a", ".a")
      replaceInFile(file, "_x86.so", ".so")
  return

def qt_config_platform_addon(platform):
  config_addon = ""
  if (0 == platform.find("win")):
    config_addon += (" " + config.option("config_addon_windows"))
  elif (0 == platform.find("linux")):
    config_addon += (" " + config.option("config_addon_linux"))
  elif (0 == platform.find("mac")):
    config_addon += (" " + config.option("config_addon_macos"))
  elif (0 == platform.find("ios")):
    config_addon += (" " + config.option("config_addon_ios"))
  elif (0 == platform.find("android")):
    config_addon += (" " + config.option("config_addon_android"))
  if (config_addon == " "):
    config_addon = ""
  return config_addon

def qt_config(platform):
  config_param = config.option("module") + " " + config.option("config") + " " + config.option("features")
  config_param_lower = config_param.lower()
  if (-1 != platform.find("xp")):
    config_param += " build_xp"
  if ("ios" == platform):
    if (config.check_option("bitcode", "yes")):
      set_env("BITCODE_GENERATION_MODE", "bitcode")
      set_env("ENABLE_BITCODE", "YES")
    config_param = config_param.replace("desktop", "")
    config_param += " iphoneos device"
    if (-1 == config_param_lower.find("debug")):
      config_param += " release"
  if ("mac_arm64" == platform):
    config_param += " apple_silicon use_javascript_core"
  if config.check_option("module", "mobile"):
    config_param += " support_web_socket"

  is_disable_pch = False
  if ("ios" == platform):
    is_disable_pch = True
  if (0 == platform.find("android")):
    is_disable_pch = True
  if not config.check_option("config", "debug"):
    is_disable_pch = True

  if is_disable_pch:
    config_param += " disable_precompiled_header"

  if ("linux_arm64" == platform):
    config_param += " linux_arm64"

  config_param += qt_config_platform_addon(platform)
  return config_param

def qt_major_version():
  qt_dir = qt_version()
  return qt_dir.split(".")[0]

def qt_version_decimal():
  qt_dir = qt_version()
  return 10 * int(qt_dir.split(".")[0]) + int(qt_dir.split(".")[1])

def qt_config_as_param(value):
  qt_version = qt_version_decimal()
  ret_params = []
  if (66 > qt_version):
    ret_params.append("CONFIG+=" + value)
  else:
    params = value.split()
    for name in params:
      ret_params.append("CONFIG+=" + name)
  return ret_params

def qt_copy_lib(lib, dir):
  qt_dir = get_env("QT_DEPLOY")
  if ("windows" == host_platform()):
    if ("" == qt_dst_postfix()):
      copy_lib(qt_dir, dir, lib)
    else:
      copy_lib(qt_dir, dir, lib + "d")
  else:
    src_file = qt_dir + "/../lib/lib" + lib + ".so." + qt_version()
    if (is_file(src_file)):
      copy_file(src_file, dir + "/lib" + lib + ".so." + qt_major_version())
    else:
      libFramework = lib
      libFramework = libFramework.replace("Qt5", "Qt")
      libFramework = libFramework.replace("Qt6", "Qt")
      libFramework += ".framework"
      if (is_dir(qt_dir + "/../lib/" + libFramework)):
        copy_dir(qt_dir + "/../lib/" + libFramework, dir + "/" + libFramework)
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
    
  copy_dir(src, out + "/" + name)

  if ("windows" == host_platform()):
    for file in glob.glob(out + "/" + name + "/*d.dll"):
      fileCheck = file[0:-5] + ".dll"
      if is_file(fileCheck):
        if ("" == qt_dst_postfix()):
          delete_file(file)
        else:
          delete_file(fileCheck)
    for file in glob.glob(out + "/" + name + "/*.pdb"):
      delete_file(file)      
  return

def qt_dst_postfix():
  config_param = config.option("config").lower()
  if (-1 != config_param.find("debug")):
    return "/debug"
  return ""

# common ------------------------------------------------
def is_windows():
  if "windows" == host_platform():
    return True
  return False

def platform_is_32(platform):
  if (-1 != platform.find("_32")):
    return True
  return False

def host_platform_is64():
  return platform.machine().endswith("64")

# apps
def app_make():
  if is_windows():
    return "nmake"
  return "make"

# doctrenderer.config
def generate_doctrenderer_config(path, root, product, vendor = "", dictionaries = ""):
  content = "<Settings>\n"

  content += ("<file>" + root + "sdkjs/common/Native/native.js</file>\n")
  content += ("<file>" + root + "sdkjs/common/Native/jquery_native.js</file>\n")

  if ("server" != product):
    content += ("<allfonts>" + root + "sdkjs/common/AllFonts.js</allfonts>\n")
  else:
    content += ("<allfonts>./AllFonts.js</allfonts>\n")

  vendor_dir = vendor
  if ("" == vendor_dir):
    vendor_dir = "sdkjs" if (product == "builder") else "web-apps"
    vendor_dir = root + vendor_dir + "/vendor/"

  content += ("<file>" + vendor_dir + "xregexp/xregexp-all-min.js</file>\n")
  content += ("<sdkjs>" + root + "sdkjs</sdkjs>\n")

  if ("" != dictionaries):
    content += ("<dictionaries>" + dictionaries + "</dictionaries>\n")

  if (False): # old html file
    content += ("<htmlfile>" + vendor_dir + "jquery/jquery.min.js</htmlfile>\n")
    if ("desktop" == product):
      content += "<htmlnoxvfb/>\n"
      content += "<htmlfileinternal>./../</htmlfileinternal>\n"

  content += "</Settings>"

  file = codecs.open(path, "w", "utf-8")
  file.write(content)
  file.close()
  return

def generate_plist_framework_folder(file):
  bundle_id_url = "com.onlyoffice."
  if ("" != get_env("PUBLISHER_BUNDLE_ID")):
    bundle_id_url = get_env("PUBLISHER_BUNDLE_ID")
  bundle_creator = "Ascensio System SIA"
  if ("" != get_env("PUBLISHER_NAME")):
    bundle_creator = get_env("PUBLISHER_NAME")
  
  bundle_version_natural = readFile(get_script_dir() + "/../../core/Common/version.txt").split(".")
  bundle_version = []
  for n in bundle_version_natural:
    bundle_version.append(n)

  name = os.path.basename(file)
  name = name.replace(".framework", "")

  content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
  content += "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
  content += "<plist version=\"1.0\">\n"
  content += "<dict>\n"
  content += "\t<key>CFBundleExecutable</key>\n"
  content += ("\t<string>" + name + "</string>\n")
  content += "\t<key>CFBundleGetInfoString</key>\n"
  content += "\t<string>Created by " + bundle_creator + "</string>\n"
  content += "\t<key>CFBundleIdentifier</key>\n"
  content += "\t<string>" + bundle_id_url + correct_bundle_identifier(name) + "</string>\n"
  content += "\t<key>CFBundlePackageType</key>\n"
  content += "\t<string>FMWK</string>\n"
  content += "\t<key>CFBundleShortVersionString</key>\n"
  content += "\t<string>" + bundle_version[0] + "." + bundle_version[1] + "</string>\n"
  content += "\t<key>CFBundleSignature</key>\n"
  content += "\t<string>????</string>\n"
  content += "\t<key>CFBundleVersion</key>\n"
  content += "\t<string>" + bundle_version[0] + "." + bundle_version[1] + "." + bundle_version[2] + "</string>\n"
  content += "\t<key>MinimumOSVersion</key>\n"
  content += "\t<string>13.0</string>\n"
  content += "</dict>\n"
  content += "</plist>"

  fileDst = file + "/Info.plist"
  if is_file(fileDst):
    delete_file(fileDst)

  fileInfo = codecs.open(fileDst, "w", "utf-8")
  fileInfo.write(content)
  fileInfo.close()
  return

def generate_plist(path):
  src_folder = path
  if ("/" != path[-1:]):
    src_folder += "/"
  src_folder += "*"
  for file in glob.glob(src_folder):
    if (is_dir(file)):
      if file.endswith(".framework"):
        generate_plist_framework_folder(file)
      else:
        generate_plist(file)
  return

def correct_bundle_identifier(bundle_identifier):
  return re.sub("[^a-zA-Z0-9\.\-]", "-", bundle_identifier)

def get_sdkjs_addons():
  result = {}
  if ("" == config.option("sdkjs-addons")):
    return result
  addons_list = config.option("sdkjs-addons").rsplit(", ")
  for name in addons_list:
    result[name] = [True, False]

  if ("" != config.option("sdkjs-addons-desktop")):
    addons_list = config.option("sdkjs-addons-desktop").rsplit(", ")
    for name in addons_list:
      result[name] = [True, False]
  return result

def get_server_addons():
  result = {}
  if ("" == config.option("server-addons")):
    return result
  addons_list = config.option("server-addons").rsplit(", ")
  for name in addons_list:
    result[name] = [True, False]
  return result

def get_web_apps_addons():
  result = {}
  if ("" == config.option("web-apps-addons")):
    return result
  addons_list = config.option("web-apps-addons").rsplit(", ")
  for name in addons_list:
    result[name] = [True, False]
  return result

def sdkjs_addons_param():
  if ("" == config.option("sdkjs-addons")):
    return []
  params = []
  addons_list = config.option("sdkjs-addons").rsplit(", ")
  for name in addons_list:
    params.append("--addon=" + name)
  return params

def sdkjs_addons_desktop_param():
  if ("" == config.option("sdkjs-addons-desktop")):
    return []
  params = []
  addons_list = config.option("sdkjs-addons-desktop").rsplit(", ")
  for name in addons_list:
    params.append("--addon=" + name)
  return params

def server_addons_param():
  if ("" == config.option("server-addons")):
    return []
  params = []
  addons_list = config.option("server-addons").rsplit(", ")
  for name in addons_list:
    params.append("--addon=" + name)
  return params

def web_apps_addons_param():
  if ("" == config.option("web-apps-addons")):
    return []
  params = []
  addons_list = config.option("web-apps-addons").rsplit(", ")
  for name in addons_list:
    params.append("--addon=" + name)
  return params

# common apps
def download(url, dst):
  return cmd_exe("curl", ["-L", "-o", dst, url])

def extract(src, dst, is_no_errors=False):
  app = "7za" if ("mac" == host_platform()) else "7z"
  return cmd_exe(app, ["x", "-y", src, "-o" + dst], is_no_errors)

def extract_unicode(src, dst, is_no_errors=False):
  if "windows" == host_platform():
    run_as_bat_win_isolate([u"chcp 65001", u"call 7z.exe x -y \"" + src + u"\" \"-o" + dst + u"\"", u"exit"])
    return
  return extract(src, dst, is_no_errors)

def archive_folder(src, dst):
  app = "7za" if ("mac" == host_platform()) else "7z"
  return cmd_exe(app, ["a", dst, src])

# windows vcvarsall
def _call_vcvarsall_and_return_env(arch):
  vcvarsall = config.option("vs-path") + "/vcvarsall.bat"
  interesting = set(("INCLUDE", "LIB", "LIBPATH", "PATH"))
  result = {}

  keys = ""
  popen = subprocess.Popen('"%s" %s & set' % (vcvarsall, arch), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  try:
    stdout, stderr = popen.communicate()
    popen.wait()

    lines = stdout.split("\n")
    for line in lines:
      if '=' not in line:
        continue
      line = line.strip()
      key, value = line.split('=', 1)
      key = key.upper()
      if key in interesting:
        if value.endswith(os.pathsep):
          value = value[:-1]
        result[key] = value

  finally:
    popen.stdout.close()
    popen.stderr.close()

  return result

global _old_environment
_old_environment = os.environ.copy()

def vcvarsall_start(arch):
  _old_environment = os.environ.copy()
  vc_env = _call_vcvarsall_and_return_env(arch)
  os.environ['PATH'] = vc_env['PATH']
  os.environ['LIB'] = vc_env['LIB']
  os.environ['LIBPATH'] = vc_env['LIBPATH']
  os.environ['INCLUDE'] = vc_env['INCLUDE']
  return

def vcvarsall_end():
  os.environ = _old_environment.copy()
  return

def run_as_bat(lines, is_no_errors=False):
  name = "tmp.bat" if ("windows" == host_platform()) else "./tmp.sh"
  content = "\n".join(lines)

  file = codecs.open(name, "w", "utf-8")
  file.write(content)
  file.close()

  if ("windows" != host_platform()):
    os.system("chmod +x " + name)

  cmd(name, [], is_no_errors)
  delete_file(name)
  return

def run_as_bat_win_isolate(lines, is_no_errors=False):
  file = codecs.open("tmp.bat", "w", "utf-8")
  file.write("\n".join(lines))
  file.close()

  file2 = codecs.open("tmp2.bat", "w", "utf-8")
  file2.write("start /wait /min tmp.bat")
  file2.close()

  cmd("tmp2.bat", [], is_no_errors)
  delete_file("tmp.bat")
  delete_file("tmp2.bat")
  return

def save_as_script(path, lines):
  content = "\n".join(lines)

  file = codecs.open(path, "w", "utf-8")
  file.write(content)
  file.close()
  return

def join_scripts(files, path):
  files_data = []
  for file in files:
    with open(get_path(file), "r") as content:
      files_data.append(content.read())

  dst_content = "\n".join(files_data)
  dst_file = codecs.open(path, "w", "utf-8")
  dst_file.write(dst_content)
  dst_file.close()
  return

def get_file_last_modified_url(url):
  retvalue = ""
  curl_command = 'curl --head %s' % (url)
  lines = run_command(curl_command)['stdout'].split("\n")
  for line in lines:
    if ':' not in line:
      continue
    line = line.strip()
    key, value = line.split(':', 1)
    key = key.upper()
    if key == "LAST-MODIFIED":
      retvalue = value
  
  return retvalue

def mac_correct_rpath_binary(path, libs):
  for lib in libs:
    cmd("install_name_tool", ["-change", "lib" + lib + ".dylib", "@rpath/lib" + lib + ".dylib", path], True)
  return

def mac_correct_rpath_library(name, libs):
  return mac_correct_rpath_binary("./lib" + name + ".dylib", libs)

def mac_correct_rpath_x2t(dir):
  cur_dir = os.getcwd()
  os.chdir(dir)
  mac_correct_rpath_library("icudata.58", [])
  mac_correct_rpath_library("icuuc.58", ["icudata.58"])
  mac_correct_rpath_library("UnicodeConverter", ["icuuc.58", "icudata.58"])
  mac_correct_rpath_library("kernel", ["UnicodeConverter"])
  mac_correct_rpath_library("kernel_network", ["UnicodeConverter", "kernel"])
  mac_correct_rpath_library("graphics", ["UnicodeConverter", "kernel"])
  mac_correct_rpath_library("doctrenderer", ["UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfFile", "XpsFile", "DjVuFile", "DocxRenderer"])
  mac_correct_rpath_library("HtmlFile2", ["UnicodeConverter", "kernel", "kernel_network", "graphics"])
  mac_correct_rpath_library("EpubFile", ["UnicodeConverter", "kernel", "HtmlFile2", "graphics"])
  mac_correct_rpath_library("Fb2File", ["UnicodeConverter", "kernel", "graphics"])
  mac_correct_rpath_library("PdfFile", ["UnicodeConverter", "kernel", "graphics", "kernel_network"])
  mac_correct_rpath_library("DjVuFile", ["UnicodeConverter", "kernel", "graphics", "PdfFile"])
  mac_correct_rpath_library("XpsFile", ["UnicodeConverter", "kernel", "graphics", "PdfFile"])
  mac_correct_rpath_library("DocxRenderer", ["UnicodeConverter", "kernel", "graphics"])
  mac_correct_rpath_library("IWorkFile", ["UnicodeConverter", "kernel"])
  mac_correct_rpath_library("HWPFile", ["UnicodeConverter", "kernel", "graphics"])
  cmd("chmod", ["-v", "+x", "./x2t"])
  cmd("install_name_tool", ["-add_rpath", "@executable_path", "./x2t"], True)
  mac_correct_rpath_binary("./x2t", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfFile", "XpsFile", "DjVuFile", "HtmlFile2", "Fb2File", "EpubFile", "doctrenderer", "DocxRenderer", "IWorkFile", "HWPFile"])
  if is_file("./allfontsgen"):
    cmd("chmod", ["-v", "+x", "./allfontsgen"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./allfontsgen"], True)
    mac_correct_rpath_binary("./allfontsgen", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "graphics"])
  if is_file("./allthemesgen"):
    cmd("chmod", ["-v", "+x", "./allthemesgen"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./allthemesgen"], True)
    mac_correct_rpath_binary("./allthemesgen", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "graphics", "kernel_network", "doctrenderer", "PdfFile", "XpsFile", "DjVuFile", "DocxRenderer"])
  if is_file("./pluginsmanager"):
    cmd("chmod", ["-v", "+x", "./pluginsmanager"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./pluginsmanager"], True)
    mac_correct_rpath_binary("./pluginsmanager", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network"])
  if is_file("./vboxtester"):
    cmd("chmod", ["-v", "+x", "./vboxtester"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./vboxtester"], True)
    mac_correct_rpath_binary("./vboxtester", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network"])
  os.chdir(cur_dir)
  return

def mac_correct_rpath_docbuilder(dir):
  cur_dir = os.getcwd()
  os.chdir(dir)
  cmd("chmod", ["-v", "+x", "./docbuilder"])
  cmd("install_name_tool", ["-add_rpath", "@executable_path", "./docbuilder"], True)
  mac_correct_rpath_binary("./docbuilder", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfFile", "XpsFile", "DjVuFile", "HtmlFile2", "Fb2File", "EpubFile", "IWorkFile", "HWPFile", "doctrenderer", "DocxRenderer"])  
  mac_correct_rpath_library("docbuilder.c", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network", "graphics", "doctrenderer", "PdfFile", "XpsFile", "DjVuFile", "DocxRenderer"])

  def add_loader_path_to_rpath(libs):
    for lib in libs:
      cmd("install_name_tool", ["-add_rpath", "@loader_path", "lib" + lib + ".dylib"], True)

  add_loader_path_to_rpath(["icuuc.58", "UnicodeConverter", "kernel", "kernel_network", "graphics", "doctrenderer", "PdfFile", "XpsFile", "DjVuFile", "DocxRenderer", "docbuilder.c"])
  os.chdir(cur_dir)
  return

def mac_correct_rpath_desktop(dir):
  mac_correct_rpath_x2t(dir + "/converter")
  cur_dir = os.getcwd()
  os.chdir(dir)
  mac_correct_rpath_library("hunspell", [])
  mac_correct_rpath_library("ooxmlsignature", ["kernel"])
  mac_correct_rpath_library("ascdocumentscore", ["UnicodeConverter", "kernel", "graphics", "kernel_network", "PdfFile", "XpsFile", "DjVuFile", "hunspell", "ooxmlsignature"])
  cmd("install_name_tool", ["-change", "@executable_path/../Frameworks/Chromium Embedded Framework.framework/Chromium Embedded Framework", "@rpath/Chromium Embedded Framework.framework/Chromium Embedded Framework", "libascdocumentscore.dylib"])
  mac_correct_rpath_binary("./editors_helper.app/Contents/MacOS/editors_helper", ["ascdocumentscore", "UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfFile", "XpsFile", "DjVuFile", "hunspell", "ooxmlsignature"])
  cmd("install_name_tool", ["-add_rpath", "@executable_path/../../../../Frameworks", "./editors_helper.app/Contents/MacOS/editors_helper"], True)
  cmd("install_name_tool", ["-add_rpath", "@executable_path/../../../../Resources/converter", "./editors_helper.app/Contents/MacOS/editors_helper"], True)
  cmd("chmod", ["-v", "+x", "./editors_helper.app/Contents/MacOS/editors_helper"])

  replaceInFile("./editors_helper.app/Contents/Info.plist", "</dict>", "\t<key>LSUIElement</key>\n\t<true/>\n</dict>")

  if is_dir("./editors_helper (GPU).app"):
    delete_dir("./editors_helper (GPU).app")
  if is_dir("./editors_helper (Renderer).app"):
    delete_dir("./editors_helper (Renderer).app")
  copy_dir("./editors_helper.app", "./editors_helper (GPU).app")
  copy_dir("./editors_helper.app", "./editors_helper (Renderer).app")
  copy_file("./editors_helper (GPU).app/Contents/MacOS/editors_helper", "./editors_helper (GPU).app/Contents/MacOS/editors_helper (GPU)")
  delete_file("./editors_helper (GPU).app/Contents/MacOS/editors_helper")
  copy_file("./editors_helper (Renderer).app/Contents/MacOS/editors_helper", "./editors_helper (Renderer).app/Contents/MacOS/editors_helper (Renderer)")
  delete_file("./editors_helper (Renderer).app/Contents/MacOS/editors_helper")
  replaceInFile("./editors_helper (GPU).app/Contents/Info.plist", "<string>editors_helper</string>", "<string>editors_helper (GPU)</string>")
  replaceInFile("./editors_helper (GPU).app/Contents/Info.plist", "<string>asc.onlyoffice.editors-helper</string>", "<string>asc.onlyoffice.editors-helper-gpu</string>")
  replaceInFile("./editors_helper (Renderer).app/Contents/Info.plist", "<string>editors_helper</string>", "<string>editors_helper (Renderer)</string>")
  replaceInFile("./editors_helper (Renderer).app/Contents/Info.plist", "<string>asc.onlyoffice.editors-helper</string>", "<string>asc.onlyoffice.editors-helper-renderer</string>")
  os.chdir(cur_dir)
  return

def linux_set_origin_rpath_libraries(dir, libs):
  tools_dir = get_script_dir() + "/../tools/linux/elf/"
  cur_dir = os.getcwd()
  os.chdir(dir)
  for lib in libs:
    cmd(tools_dir + "patchelf", ["--set-rpath", "\\$ORIGIN", "lib" + lib], True)
  os.chdir(cur_dir)
  return

def linux_correct_rpath_docbuilder(dir):
  linux_set_origin_rpath_libraries(dir, ["docbuilder.jni.so", "docbuilder.c.so", "icuuc.so.58", "doctrenderer.so", "graphics.so", "kernel.so", "kernel_network.so", "UnicodeConverter.so", "PdfFile.so", "XpsFile.so", "DjVuFile.so", "DocxRenderer.so"])
  return

def common_check_version(name, good_version, clean_func):
  version_good = name + "_version_" + good_version
  version_path = "./" + name + ".data"
  version = readFile(version_path)
  if (version != version_good):
    delete_file(version_path)
    writeFile(version_path, version_good)
    clean_func()
  return

def copy_sdkjs_plugin(src_dir, dst_dir, name, is_name_as_guid=False, is_desktop_local=False):
  src_dir_path = src_dir + "/" + name
  if not is_dir(src_dir_path):
    src_dir_path = src_dir + "/" + name
  if not is_file(src_dir_path + "/config.json"):
    # all variation subfolders
    if is_file(src_dir_path + "/src/config.json"):
      src_dir_path = src_dir_path + "/src"
  if not is_name_as_guid:
    dst_dir_path = dst_dir + "/" + name
    if is_dir(dst_dir_path):
      delete_dir(dst_dir_path)
    create_dir(dst_dir_path)
    copy_dir_content(src_dir_path, dst_dir_path, "", ".git")
    if is_desktop_local:
      for file in glob.glob(dst_dir_path + "/*.html"):
        replaceInFile(file, "https://onlyoffice.github.io/sdkjs-plugins/", "../")
    return
  if not is_file(src_dir_path + "/config.json"):
    return
  config_content = readFile(src_dir_path + "/config.json")
  index_start = config_content.find("\"asc.{")
  index_start += 5
  index_end = config_content.find("}", index_start)
  index_end += 1
  guid = config_content[index_start:index_end]
  dst_dir_path = dst_dir + "/" + guid
  if is_dir(dst_dir_path):
    delete_dir(dst_dir_path)
  create_dir(dst_dir_path)
  copy_dir_content(src_dir_path, dst_dir_path, "", ".git")
  if is_desktop_local:
    for file in glob.glob(dst_dir_path + "/*.html"):
      replaceInFile(file, "https://onlyoffice.github.io/sdkjs-plugins/", "../")
  dst_deploy_dir = dst_dir_path + "/deploy"
  if is_dir(dst_deploy_dir):
    delete_dir(dst_deploy_dir)
  return

def copy_marketplace_plugin(dst_dir, is_name_as_guid=False, is_desktop_local=False, is_store_copy=False):
  git_dir = __file__script__path__ + "/../.."
  if False:
    # old version
    copy_sdkjs_plugin(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins", dst_dir, "manager", is_name_as_guid, is_desktop_local)
    return
  src_dir_path = git_dir + "/onlyoffice.github.io/store/plugin"
  name = "marketplace"
  if is_name_as_guid:
    name = "{AA2EA9B6-9EC2-415F-9762-634EE8D9A95E}"

  dst_dir_path = dst_dir + "/" + name
  if is_dir(dst_dir_path):
    delete_dir(dst_dir_path)
  create_dir(dst_dir_path)

  copy_dir_content(src_dir_path, dst_dir_path)
  if is_desktop_local:
    for file in glob.glob(dst_dir_path + "/*.html"):
      replaceInFile(file, "https://onlyoffice.github.io/sdkjs-plugins/", "../")

  if is_store_copy:
    copy_dir(git_dir + "/onlyoffice.github.io/store", dst_dir_path + "/store")
    delete_dir(dst_dir_path + "/store/plugin")
    delete_dir(dst_dir_path + "/store/plugin-dev")
  return

def copy_sdkjs_plugins(dst_dir, is_name_as_guid=False, is_desktop_local=False, isXp=False):
  plugins_dir = __file__script__path__ + "/../../onlyoffice.github.io/sdkjs-plugins/content"
  plugins_list_config = config.option("sdkjs-plugin")
  if isXp:
    plugins_list_config="photoeditor, macros, highlightcode, doc2md"
  if ("" == plugins_list_config):
    return
  plugins_list = plugins_list_config.rsplit(", ")
  for name in plugins_list:
    copy_sdkjs_plugin(plugins_dir, dst_dir, name, is_name_as_guid, is_desktop_local)    
  return

def copy_sdkjs_plugins_server(dst_dir, is_name_as_guid=False, is_desktop_local=False):
  plugins_dir = __file__script__path__ + "/../../onlyoffice.github.io/sdkjs-plugins/content"
  plugins_list_config = config.option("sdkjs-plugin-server")
  if ("" == plugins_list_config):
    return
  plugins_list = plugins_list_config.rsplit(", ")
  for name in plugins_list:
    copy_sdkjs_plugin(plugins_dir, dst_dir, name, is_name_as_guid, is_desktop_local)    
  return

def support_old_versions_plugins(out_dir):
  if is_file(out_dir + "/pluginBase.js"):
    return
  download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js", out_dir + "/plugins.js")
  download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins-ui.js", out_dir + "/plugins-ui.js")
  download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.css", out_dir + "/plugins.css")
  content_plugin_base = ""
  with open(get_path(out_dir + "/plugins.js"), "r") as file:
    content_plugin_base += file.read()
  content_plugin_base += "\n\n"
  with open(get_path(out_dir + "/plugins-ui.js"), "r") as file:
    content_plugin_base += file.read()  
  with open(get_path(out_dir + "/pluginBase.js"), "w") as file:
    file.write(content_plugin_base)
  delete_file(out_dir + "/plugins.js")
  delete_file(out_dir + "/plugins-ui.js")  
  return

def generate_sdkjs_plugin_list(dst):
  plugins_list = config.option("sdkjs-plugin").rsplit(", ") \
               + config.option("sdkjs-plugin-server").rsplit(", ")
  plugins_list = list(filter(None, plugins_list))
  with open(get_path(dst), 'w') as file:
    dump = json.dumps(sorted(plugins_list), indent=4)
    file.write(re.sub(r"^(\s{4})", '\t', dump, 0, re.MULTILINE))
  return

def get_xcode_major_version():
  version = run_command("xcodebuild -version")['stdout']
  return int(version.split('.')[0][6:])

def hack_xcode_ios():
  if (12 > get_xcode_major_version()):
    return

  qmake_spec_file = config.option("qt-dir") + "/ios/mkspecs/macx-ios-clang/qmake.conf"

  filedata = ""
  with open(get_path(qmake_spec_file), "r") as file:
    filedata = file.read()

  content_hack = "QMAKE_CXXFLAGS += -arch $$QT_ARCH"
  if (-1 != filedata.find(content_hack)):
    return

  filedata += "\n"
  filedata += content_hack
  filedata += "\n\n"
  
  delete_file(qmake_spec_file)
  with open(get_path(qmake_spec_file), "w") as file:
    file.write(filedata)
  return

def find_mac_sdk_version():
  sdk_dir = run_command("xcode-select -print-path")['stdout']
  sdk_dir = os.path.join(sdk_dir, "Platforms/MacOSX.platform/Developer/SDKs")
  sdks = [re.findall('^MacOSX(1\d\.\d+)\.sdk$', s) for s in os.listdir(sdk_dir)]
  sdks = [s[0] for s in sdks if s]
  return sdks[0]

def find_mac_sdk():
  return run_command("xcrun --sdk macosx --show-sdk-path")['stdout']

def get_mac_sdk_version_number():
  ver = find_mac_sdk_version()
  ver_arr = ver.split(".")
  if 0 == len(ver_arr):
    return 0
  if 1 == len(ver_arr):
    return 1000 * int(ver_arr[0])
  return 1000 * int(ver_arr[0]) + int(ver_arr[1])

def make_sln(directory, args, is_no_errors):
  programFilesDir = get_env("ProgramFiles")
  if ("" != get_env("ProgramFiles(x86)")):
    programFilesDir = get_env("ProgramFiles(x86)")
  dev_path = programFilesDir + "\\Microsoft Visual Studio 14.0\\Common7\\IDE"
  if ("2019" == config.option("vs-version")):
    dev_path = programFilesDir + "\\Microsoft Visual Studio\\2019\\Community\\Common7\\IDE"
    if not is_dir(dev_path):
      dev_path = programFilesDir + "\\Microsoft Visual Studio\\2019\\Enterprise\\Common7\\IDE"
    if not is_dir(dev_path):
      dev_path = programFilesDir + "\\Microsoft Visual Studio\\2019\\Professional\\Common7\\IDE"

  old_env = dict(os.environ)
  os.environ["PATH"] = dev_path + os.pathsep + os.environ["PATH"]

  old_cur = os.getcwd()
  os.chdir(directory)
  run_as_bat(["call devenv " + " ".join(args)], is_no_errors)
  os.chdir(old_cur)

  os.environ.clear()
  os.environ.update(old_env)
  return

def make_sln_project(directory, sln_path):
  args = []
  args.append(sln_path)
  args.append("/Rebuild")
  if (config.check_option("platform", "win_64")):
    make_sln(directory, args + ["\"Release|x64\""], True)
  if True:#(config.check_option("platform", "win_32")):
    make_sln(directory, args + ["\"Release|Win32\""], True)
  return

def get_android_sdk_home():
  ndk_root_path = get_env("ANDROID_NDK_ROOT")
  if (-1 != ndk_root_path.find("/ndk/")):
    return ndk_root_path + "/../.."
  return ndk_root_path + "/.."

def readFileLicence(path):
  content = readFile(path)
  index = content.find("*/")
  if index >= 0:
    return content[0:index+2]
  return ""

def replaceFileLicence(path, license):
  old_licence = readFileLicence(path)
  replaceInFile(path, old_licence, license)
  return

def copy_v8_files(core_dir, deploy_dir, platform, is_xp=False):
  if (-1 != config.option("config").find("use_javascript_core")):
    return
  directory_v8 = core_dir + "/Common/3dParty"
  
  if is_xp:
    directory_v8 += "/v8/v8_xp"
    copy_files(directory_v8 + platform + "/release/icudt*.dll", deploy_dir + "/")
    return
  
  if config.check_option("config", "v8_version_60"):
    directory_v8 += "/v8/v8/out.gn/"
  else:
    directory_v8 += "/v8_89/v8/out.gn/"

  if (0 == platform.find("win")):
    copy_files(directory_v8 + platform + "/release/icudt*.dat", deploy_dir + "/")
  else:
    copy_files(directory_v8 + platform + "/icudt*.dat", deploy_dir + "/")
  return

def clone_marketplace_plugin(out_dir, is_name_as_guid=False, is_replace_paths=False, is_delete_git_dir=True, git_owner=""):  
  old_cur = os.getcwd()
  os.chdir(out_dir)
  git_update("onlyoffice.github.io", False, True, git_owner)
  os.chdir(old_cur)

  dst_dir_name = "marketplace"
  if is_name_as_guid:
    config_content = readFile(out_dir + "/onlyoffice.github.io/store/plugin/config.json")
    index_start = config_content.find("\"asc.{")
    index_start += 5
    index_end = config_content.find("}", index_start)
    index_end += 1
    guid = config_content[index_start:index_end]
    dst_dir_name = guid

  dst_dir_path = out_dir + "/" + dst_dir_name

  if is_dir(dst_dir_path):
    delete_dir(dst_dir_path)
  copy_dir(out_dir + "/onlyoffice.github.io/store/plugin", dst_dir_path)
  
  if is_replace_paths:
    for file in glob.glob(dst_dir_path + "/*.html"):
      replaceInFile(file, "https://onlyoffice.github.io/sdkjs-plugins/", "../")
        
  if is_delete_git_dir:
    delete_dir_with_access_error(out_dir + "/onlyoffice.github.io")
  return

def correctPathForBuilder(path):
  replace_value = "../../../build/"
  if (config.option("branding") != ""):
    replace_value += (config.option("branding") + "/")
  replace_value += "lib/"
  if (config.check_option("config", "debug")):
    replace_value += ("debug/")
  if (replace_value == "../../../build/lib/"):
    return ""
  new_path = path + ".bak"
  copy_file(path, new_path)
  replaceInFile(path, "../../../build/lib/", replace_value)
  return new_path

def restorePathForBuilder(new_path):
  if ("" == new_path):
    return
  old_path = new_path[:-4]
  delete_file(old_path)
  copy_file(new_path, old_path)
  delete_file(new_path);
  return

def generate_check_linux_system(build_tools_dir, out_dir):
  create_dir(out_dir + "/.system")
  copy_file(build_tools_dir + "/tools/linux/check_system/check.sh", out_dir + "/.system/check.sh")
  copy_file(build_tools_dir + "/tools/linux/check_system/libstdc++.so.6", out_dir + "/.system/libstdc++.so.6")
  return

def convert_ios_framework_to_xcframework(folder, lib):
  cur_dir = os.getcwd()
  os.chdir(folder)
  
  create_dir(lib + "_xc_tmp")
  create_dir(lib + "_xc_tmp/iphoneos")
  create_dir(lib + "_xc_tmp/iphonesimulator")
  copy_dir(lib + ".framework", lib + "_xc_tmp/iphoneos/" + lib + ".framework")
  copy_dir(lib + ".framework", lib + "_xc_tmp/iphonesimulator/" + lib + ".framework")

  cmd("xcrun", ["lipo", "-remove", "x86_64", "./" + lib + "_xc_tmp/iphoneos/" + lib + ".framework/" + lib, 
    "-o", "./" + lib + "_xc_tmp/iphoneos/" + lib + ".framework/" + lib])
  cmd("xcrun", ["lipo", "-remove", "arm64", "./" + lib + "_xc_tmp/iphonesimulator/" + lib + ".framework/" + lib, 
    "-o", "./" + lib + "_xc_tmp/iphonesimulator/" + lib + ".framework/" + lib])

  cmd("xcodebuild", ["-create-xcframework", 
    "-framework", "./" + lib + "_xc_tmp/iphoneos/" + lib + ".framework/", 
    "-framework", "./" + lib + "_xc_tmp/iphonesimulator/" + lib + ".framework/",
    "-output", lib + ".xcframework"])

  delete_dir(lib + "_xc_tmp")

  os.chdir(cur_dir)
  return

def convert_ios_framework_to_xcframework_folder(folder, libs):
  for lib in libs:
    convert_ios_framework_to_xcframework(folder, lib)
  return

def change_elf_rpath(path, origin):
  # excludes ---
  if (-1 != path.find("libicudata.so.58")):
    return
  # ------------
  tools_dir = get_script_dir() + "/../tools/linux/elf/"
  result_obj = run_command(tools_dir + "readelf -d '" + path + "' | grep R*PATH")
  result = result_obj["stdout"]
  result_error = result_obj["stderr"]
  if (result_error != ""):
    return
  if (-1 != result.find("Error:")) or (-1 != result.find(" ELF ")):
    return
  is_rpath = True
  if (-1 != result.find("Library runpath: [")):
    is_rpath = False
  old_path = run_command(tools_dir + "patchelf --print-rpath '" + path + "'")['stdout']
  if (-1 != old_path.find(origin)):
    return
  new_path = old_path
  new_path = new_path.replace("$ORIGIN", "\$ORIGIN")
  if ("" != new_path):
    new_path += ":"
  new_path += origin
  if (-1 != old_path.find("$ORIGIN/converter")) or (-1 != path.find("/desktopeditors/converter")):
    new_path += (":" + origin + "/converter")
  if (-1 != old_path.find("$ORIGIN/system")):
    new_path += (":" + origin + "/system")
  if is_rpath:
    cmd(tools_dir + "patchelf", ["--force-rpath", "--set-rpath", new_path, path], True)
  else:
    cmd(tools_dir + "patchelf", ["--set-rpath", new_path, path], True)
  #print("[" + os.path.basename(path) + "] old: " + old_path + "; new: " + new_path)
  return
  
def correct_elf_rpath_directory(directory, origin, is_recursion = True):
  for file in glob.glob(directory + "/*"):
    if is_file(file):
      change_elf_rpath(file, origin)
    elif is_dir(file) and is_recursion:
      correct_elf_rpath_directory(file, origin)
  return

def is_need_build_js():
  if "osign" == config.option("module"):
    return False
  return True

def copy_dictionaries(src, dst, is_hyphen = True, is_spell = True):
  if (False == is_hyphen) and (False == is_spell):
    return

  if not is_dir(dst):
    create_dir(dst)

  src_folder = src
  if ("/" != src[-1:]):
    src_folder += "/"
  src_folder += "*"
  for file in glob.glob(src_folder):
    if is_file(file):
      copy_file(file, dst)
      continue

    basename = os.path.basename(file)
    if (".git" == basename):
      continue

    if (True == is_hyphen) and (True == is_spell):
      copy_dir(file, dst + "/" + basename)
      continue

    is_spell_present = is_file(file + "/" + basename + ".dic")
    is_hyphen_present = is_file(file + "/hyph_" + basename + ".dic")

    is_dir_need = False
    if (is_hyphen and is_hyphen_present) or (is_spell and is_spell_present):
      is_dir_need = True

    if not is_dir_need:
      continue

    lang_folder = dst + "/" + basename
    create_dir(lang_folder)

    if is_hyphen and is_hyphen_present:
      copy_dir_content(file, lang_folder, "hyph_", "")
    
    if is_spell and is_spell_present:
      copy_dir_content(file, lang_folder, "", "hyph_")

  if is_file(dst + "/en_US/en_US_thes.dat"):
    delete_file(dst + "/en_US/en_US_thes.dat")
    delete_file(dst + "/en_US/en_US_thes.idx")
  
  if is_file(dst + "/ru_RU/ru_RU_oo3.dic"):
    delete_file(dst + "/ru_RU/ru_RU_oo3.dic")
    delete_file(dst + "/ru_RU/ru_RU_oo3.aff")

  if is_file(dst + "/uk_UA/th_uk_UA.dat"):
    delete_file(dst + "/uk_UA/th_uk_UA.dat")
    delete_file(dst + "/uk_UA/th_uk_UA.idx")

  return

def check_module_version(actual_version, clear_func):
  module_file = "./module.version"
  current_module_version = readFile(module_file)
  if (actual_version == current_module_version):
    return
  if is_file(module_file):
    delete_file(module_file)
  writeFile(module_file, actual_version)
  clear_func()
  return

def check_python():
  if ("linux" != host_platform()):
    return
  directory = __file__script__path__ + "/../tools/linux"
  directory_bin = __file__script__path__ + "/../tools/linux/python3/bin"

  if not is_dir(directory + "/python3"):
    cmd("tar", ["xfz", directory + "/python3.tar.gz", "-C", directory])
    cmd("ln", ["-s", directory_bin + "/python3", directory_bin + "/python"])
  directory_bin = directory_bin.replace(" ", "\\ ")
  os.environ["PATH"] = directory_bin + os.pathsep + os.environ["PATH"]
  return

def check_tools():
  if ("linux" == host_platform()):
    directory = __file__script__path__ + "/../tools/linux"
    if not is_os_arm() and config.check_option("platform", "linux_arm64"):
      if not is_dir(directory + "/qt"):
        create_dir(directory + "/qt")
      cmd("python", [directory + "/arm/build_qt.py", "--arch", "arm64", directory + "/qt/arm64"])
  return

def apply_patch(file, patch):
  patch_content = readFile(patch)
  index1 = patch_content.find("<<<<<<<")
  index2 = patch_content.find("=======")
  index3 = patch_content.find(">>>>>>>")
  file_content_old = patch_content[index1 + 7:index2].strip()
  file_content_new = patch_content[index2 + 7:index3].strip()
  #file_content_new = "\n#if 0" + file_content_old + "#else" + file_content_new + "#endif\n"
  replaceInFile(file, file_content_old, file_content_new)
  return

def get_autobuild_version(product, platform="", branch="", build=""):
  download_platform = platform
  if ("" == download_platform):
    osType = get_platform()
    isArm = True if (-1 != osType.find("arm")) else False
    is64 = True if (osType.endswith("64")) else False
    
    if ("windows" == host_platform()):
      download_platform = "win-"
    elif ("linux" == host_platform()):
      download_platform = "linux-"
    else:
      download_platform = "mac-"

    download_platform += ("arm" if isArm else "")
    download_platform += ("64" if is64 else "32")
  else:
    download_platform = download_platform.replace("_", "-")

  download_build = build
  if ("" == download_build):
    download_build = "latest"

  download_branch = branch
  if ("" == download_branch):
    download_branch = "develop"

  download_addon = download_branch + "/" + download_build + "/" + product + "-" + download_platform + ".7z"
  return "http://repo-doc-onlyoffice-com.s3.amazonaws.com/archive/" + download_addon

def create_x2t_js_cache(dir, product, platform):
  if is_file(dir + "/libdoctrenderer.dylib") and (os.path.getsize(dir + "/libdoctrenderer.dylib") < 5*1024*1024):
    return

  if ((platform == "linux_arm64") and not is_os_arm()):
    cmd_in_dir_qemu(platform, dir, "./x2t", ["-create-js-snapshots"], True)
    return

  cmd_in_dir(dir, "./x2t", ["-create-js-snapshots"], True)
  return

def setup_local_qmake(dir_qmake):
  dir_base = os.path.dirname(dir_qmake)
  writeFile(dir_base + "/onlyoffice_qt.conf", "Prefix = " + dir_base)  
  return
  