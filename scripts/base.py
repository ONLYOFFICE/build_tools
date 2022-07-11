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
  return

def delete_dir_with_access_error(path):
  def delete_file_on_error(func, path, exc_info):
    if not os.access(path, os.W_OK):
      os.chmod(path, stat.S_IWUSR)
      func(path)
    return
  if not is_dir(path):
    print("delete warning [folder not exist]: " + path)
    return
  shutil.rmtree(get_path(path), ignore_errors=False, onerror=delete_file_on_error)
  return

def delete_dir(path):
  if not is_dir(path):
    print("delete warning [folder not exist]: " + path)
    return
  shutil.rmtree(get_path(path), ignore_errors=True)
  return

def copy_lib(src, dst, name):
  if (config.check_option("config", "bundle_dylibs")) and is_dir(src + "/" + name + ".framework"):
    copy_dir(src + "/" + name + ".framework", dst + "/" + name + ".framework")
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

def replaceInFile(path, text, textReplace):
  filedata = ""
  with open(get_path(path), "r") as file:
    filedata = file.read()
  filedata = filedata.replace(text, textReplace)
  delete_file(path)
  with open(get_path(path), "w") as file:
    file.write(filedata)
  return
def replaceInFileRE(path, pattern, textReplace):
  filedata = ""
  with open(get_path(path), "r") as file:
    filedata = file.read()
  filedata = re.sub(pattern, textReplace, filedata)
  delete_file(path)
  with open(get_path(path), "w") as file:
    file.write(filedata)
  return

def readFile(path):
  if not is_file(path):
    return ""
  filedata = ""
  with open(get_path(path), "r") as file:
    filedata = file.read()
  return filedata

def writeFile(path, data):
  if is_file(path):
    delete_file(path)
  with open(get_path(path), "w") as file:
    file.write(data)
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
      command += (" \"" + arg + "\"")
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

def cmd_exe(prog, args):
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
      command += (" \"" + arg + "\"")
    process = subprocess.Popen(command, stderr=subprocess.STDOUT, shell=True, env=env_dir)
    ret = process.wait()
  if ret != 0:
    sys.exit("Error (" + prog + "): " + str(ret))
  return ret

def cmd_in_dir(directory, prog, args=[], is_no_errors=False):
  dir = get_path(directory)
  cur_dir = os.getcwd()
  os.chdir(dir)
  ret = cmd(prog, args, is_no_errors)
  os.chdir(cur_dir)
  return ret

def cmd_and_return_cwd(prog, args=[], is_no_errors=False):
  cur_dir = os.getcwd()
  ret = cmd(prog, args, is_no_errors)
  os.chdir(cur_dir)
  return ret

def run_command(sCommand):
  popen = subprocess.Popen(sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  result = {'stdout' : '', 'stderr' : ''}
  try:
    stdout, stderr = popen.communicate()
    popen.wait()
    result['stdout'] = stdout.strip().decode('utf-8', errors='ignore')
    result['stderr'] = stderr.strip().decode('utf-8', errors='ignore')
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
def git_update(repo, is_no_errors=False, is_current_dir=False):
  print("[git] update: " + repo)
  url = "https://github.com/ONLYOFFICE/" + repo + ".git"
  if config.option("git-protocol") == "ssh":
    url = "git@github.com:ONLYOFFICE/" + repo + ".git"
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
  result.update(get_sdkjs_plugins())
  result.update(get_sdkjs_plugins_server())
  result["web-apps"] = [False, False]
  result.update(get_web_apps_addons())
  result["dictionaries"] = [False, False]

  if config.check_option("module", "builder"):
    result["DocumentBuilder"] = [False, False]

  if config.check_option("module", "desktop"):
    result["desktop-sdk"] = [False, False]
    result["desktop-apps"] = [False, False]
    result["document-templates"] = [False, False]

  if (config.check_option("module", "server")):
    result["server"] = [False, False]
    result.update(get_server_addons())
    result["document-server-integration"] = [False, False]
    result["document-templates"] = [False, False]
    
  if (config.check_option("module", "server") or config.check_option("platform", "ios")):
    result["core-fonts"] = [False, False]

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
  if config.option("git-protocol") == "ssh":
    url = "git@github.com:ONLYOFFICE/" + repo + ".git"
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

# qmake -------------------------------------------------
def qt_setup(platform):
  compiler = config.check_compiler(platform)
  qt_dir = config.option("qt-dir") if (-1 == platform.find("_xp")) else config.option("qt-dir-xp")
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

def qt_config(platform):
  config_param = config.option("module") + " " + config.option("config") + " " + config.option("features")
  config_param_lower = config_param.lower()
  if (-1 != platform.find("xp")):
    config_param += " build_xp"
  if ("ios" == platform):
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
  if (config.option("vs-version") == "2019"):
    config_param += " v8_version_89 vs2019"

  if ("linux_arm64" == platform):
    config_param += " linux_arm64"
  if config.check_option("platform", "linux_arm64"):
    config_param += " v8_version_89"
  return config_param

def qt_major_version():
  qt_dir = qt_version()
  return qt_dir.split(".")[0]

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
def generate_doctrenderer_config(path, root, product, vendor = ""):
  content = "<Settings>\n"

  content += ("<file>" + root + "sdkjs/common/Native/native.js</file>\n")
  content += ("<file>" + root + "sdkjs/common/Native/jquery_native.js</file>\n")

  if ("server" != product):
    content += ("<file>" + root + "sdkjs/common/AllFonts.js</file>\n")
  else:
    content += ("<file>./AllFonts.js</file>\n")

  vendor_dir = vendor
  if ("" == vendor_dir):
    vendor_dir = "sdkjs" if (product == "builder") else "web-apps"
    vendor_dir = root + vendor_dir + "/vendor/"

  content += ("<file>" + vendor_dir + "xregexp/xregexp-all-min.js</file>\n")
  content += ("<htmlfile>" + vendor_dir + "jquery/jquery.min.js</htmlfile>\n")

  content += "<DoctSdk>\n"
  content += ("<file>" + root + "sdkjs/word/sdk-all-min.js</file>\n")
  content += ("<file>" + root + "sdkjs/common/libfont/js/fonts.js</file>\n")
  content += ("<file>" + root + "sdkjs/word/sdk-all.js</file>\n")
  content += "</DoctSdk>\n"
  content += "<PpttSdk>\n"
  content += ("<file>" + root + "sdkjs/slide/sdk-all-min.js</file>\n")
  content += ("<file>" + root + "sdkjs/common/libfont/js/fonts.js</file>\n")
  content += ("<file>" + root + "sdkjs/slide/sdk-all.js</file>\n")
  content += "</PpttSdk>\n"
  content += "<XlstSdk>\n"
  content += ("<file>" + root + "sdkjs/cell/sdk-all-min.js</file>\n")
  content += ("<file>" + root + "sdkjs/common/libfont/js/fonts.js</file>\n")
  content += ("<file>" + root + "sdkjs/cell/sdk-all.js</file>\n")
  content += "</XlstSdk>\n"

  if ("desktop" == product):
    content += "<htmlnoxvfb/>\n"
    content += "<htmlfileinternal>./../</htmlfileinternal>\n"

  content += "</Settings>"

  file = codecs.open(path, "w", "utf-8")
  file.write(content)
  file.close()
  return

def generate_plist(path):
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

  for file in glob.glob(path + "/*.framework"):
    if not is_dir(file):
      continue
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
    content += "\t<string>10.0</string>\n"
    content += "</dict>\n"
    content += "</plist>"

    fileDst = file + "/Info.plist"
    if is_file(fileDst):
      delete_file(fileDst)

    fileInfo = codecs.open(fileDst, "w", "utf-8")
    fileInfo.write(content)
    fileInfo.close()
      
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

def get_plugins(plugins_list=""):
  result = {}
  if ("" == plugins_list):
    return result
  plugins_list = plugins_list.rsplit(", ")
  plugins_dir = get_script_dir() + "/../../sdkjs-plugins"
  for name in plugins_list:
    result["plugin-" + name] = [True, plugins_dir]
  return result

def get_sdkjs_plugins():
  return get_plugins(config.option("sdkjs-plugin"))

def get_sdkjs_plugins_server():
  return get_plugins(config.option("sdkjs-plugin-server"))

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

def extract(src, dst):
  app = "7za" if ("mac" == host_platform()) else "7z"
  return cmd_exe(app, ["x", "-y", src, "-o" + dst])

def archive_folder(src, dst):
  app = "7za" if ("mac" == host_platform()) else "7z"
  return cmd_exe(app, ["a", "-r", dst, src])

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
    cmd("install_name_tool", ["-change", "lib" + lib + ".dylib", "@rpath/lib" + lib + ".dylib", path])
  return

def mac_correct_rpath_library(name, libs):
  return mac_correct_rpath_binary("./lib" + name + ".dylib", libs)

def mac_correct_rpath_x2t(dir):
  cur_dir = os.getcwd()
  os.chdir(dir)
  mac_correct_rpath_library("icudata.58", [])
  mac_correct_rpath_library("icuuc.58", ["icudata.58"])
  mac_correct_rpath_library("UnicodeConverter", ["icuuc.58", "icudata.58", "kernel"])
  mac_correct_rpath_library("kernel", [])
  mac_correct_rpath_library("kernel_network", ["kernel"])
  mac_correct_rpath_library("graphics", ["UnicodeConverter", "kernel"])
  mac_correct_rpath_library("doctrenderer", ["UnicodeConverter", "kernel", "kernel_network", "graphics"])
  mac_correct_rpath_library("HtmlFile2", ["UnicodeConverter", "kernel", "kernel_network", "graphics"])
  mac_correct_rpath_library("EpubFile", ["kernel", "HtmlFile2", "graphics"])
  mac_correct_rpath_library("Fb2File", ["UnicodeConverter", "kernel", "graphics"])
  mac_correct_rpath_library("HtmlRenderer", ["UnicodeConverter", "kernel", "graphics"])
  mac_correct_rpath_library("PdfWriter", ["UnicodeConverter", "kernel", "graphics", "kernel_network"])
  mac_correct_rpath_library("DjVuFile", ["kernel", "UnicodeConverter", "graphics", "PdfWriter"])
  mac_correct_rpath_library("PdfReader", ["kernel", "UnicodeConverter", "graphics", "PdfWriter", "HtmlRenderer"])
  mac_correct_rpath_library("XpsFile", ["kernel", "UnicodeConverter", "graphics", "PdfWriter"])
  mac_correct_rpath_library("DocxRenderer", ["kernel", "UnicodeConverter", "graphics"])
  cmd("chmod", ["-v", "+x", "./x2t"])
  cmd("install_name_tool", ["-add_rpath", "@executable_path", "./x2t"], True)
  mac_correct_rpath_binary("./x2t", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfWriter", "HtmlRenderer", "PdfReader", "XpsFile", "DjVuFile", "HtmlFile2", "Fb2File", "EpubFile", "doctrenderer", "DocxRenderer"])
  if is_file("./allfontsgen"):
    cmd("chmod", ["-v", "+x", "./allfontsgen"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./allfontsgen"], True)
    mac_correct_rpath_binary("./allfontsgen", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "graphics"])
  if is_file("./allthemesgen"):
    cmd("chmod", ["-v", "+x", "./allthemesgen"])
    cmd("install_name_tool", ["-add_rpath", "@executable_path", "./allthemesgen"], True)
    mac_correct_rpath_binary("./allthemesgen", ["icudata.58", "icuuc.58", "UnicodeConverter", "kernel", "graphics", "kernel_network", "doctrenderer"])
  os.chdir(cur_dir)
  return

def mac_correct_rpath_desktop(dir):
  mac_correct_rpath_x2t(dir + "/converter")
  cur_dir = os.getcwd()
  os.chdir(dir)
  mac_correct_rpath_library("hunspell", [])
  mac_correct_rpath_library("ooxmlsignature", ["kernel"])
  mac_correct_rpath_library("ascdocumentscore", ["UnicodeConverter", "kernel", "graphics", "kernel_network", "PdfWriter", "HtmlRenderer", "PdfReader", "XpsFile", "DjVuFile", "hunspell", "ooxmlsignature"])
  cmd("install_name_tool", ["-change", "@executable_path/../Frameworks/Chromium Embedded Framework.framework/Chromium Embedded Framework", "@rpath/Chromium Embedded Framework.framework/Chromium Embedded Framework", "libascdocumentscore.dylib"])
  mac_correct_rpath_binary("./editors_helper.app/Contents/MacOS/editors_helper", ["ascdocumentscore", "UnicodeConverter", "kernel", "kernel_network", "graphics", "PdfWriter", "HtmlRenderer", "PdfReader", "XpsFile", "DjVuFile", "hunspell", "ooxmlsignature"])
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
  src_dir_path = src_dir + "/plugin-" + name
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
  copy_dir_content(src_dir_path, dst_dir + "/" + guid, "", ".git")
  if is_desktop_local:
    for file in glob.glob(dst_dir + "/" + guid + "/*.html"):
      replaceInFile(file, "https://onlyoffice.github.io/sdkjs-plugins/", "../")
  return

def copy_sdkjs_plugins(dst_dir, is_name_as_guid=False, is_desktop_local=False):
  plugins_dir = get_script_dir() + "/../../sdkjs-plugins"
  plugins_list_config = config.option("sdkjs-plugin")
  if ("" == plugins_list_config):
    return
  plugins_list = plugins_list_config.rsplit(", ")
  for name in plugins_list:
    copy_sdkjs_plugin(plugins_dir, dst_dir, name, is_name_as_guid, is_desktop_local)    
  return

def copy_sdkjs_plugins_server(dst_dir, is_name_as_guid=False, is_desktop_local=False):
  plugins_dir = get_script_dir() + "/../../sdkjs-plugins"
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
    directory_v8 += "/v8/v8_xp/"
  elif (-1 != config.option("config").lower().find("v8_version_89")):
    directory_v8 += "/v8_89/v8/out.gn/"
  if (config.option("vs-version") == "2019"):
    directory_v8 += "/v8_89/v8/out.gn/"
  else:
    directory_v8 += "/v8/v8/out.gn/"

  if is_xp:
    copy_files(directory_v8 + platform + "/release/icudt*.dll", deploy_dir + "/")
    return

  if (0 == platform.find("win")):
    copy_files(directory_v8 + platform + "/release/icudt*.dat", deploy_dir + "/")
  else:
    copy_file(directory_v8 + platform + "/icudtl.dat", deploy_dir + "/icudtl.dat")
  return
