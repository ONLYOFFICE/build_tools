#!/usr/bin/env python

import platform
import glob
import shutil
import os
import subprocess
import sys
import config
import codecs

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
  if "windows" == host_platform():
    return path.replace("/", "\\")
  return path

def get_env(name):
  return os.getenv(name, "")

def set_env(name, value):
  os.environ[name] = value
  return

def configure_common_apps():
  if ("windows" == host_platform()):
    os.environ["PATH"] = get_script_dir() + "/../tools/win/7z" + os.pathsep + get_script_dir() + "/../tools/win/curl" + os.pathsep + os.environ["PATH"]
  elif ("mac" == host_platform()):
    os.environ["PATH"] = get_script_dir() + "/../tools/mac" + os.pathsep + os.environ["PATH"]
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

def copy_files(src, dst):
  for file in glob.glob(src):
    if is_file(file):
      copy_file(file, dst)
    elif is_dir(file):
      copy_dir(file, dst + "/" + os.path.basename(file))
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

def delete_dir(path):
  if not is_dir(path):
    print("delete warning [folder not exist]: " + path)
    return
  shutil.rmtree(get_path(path))
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
def git_update(repo):
  print("[git] update: " + repo)
  url = "https://github.com/ONLYOFFICE/" + repo + ".git"
  if config.option("git-protocol") == "ssh":
    url = "git@github.com:ONLYOFFICE/" + repo + ".git"
  folder = get_script_dir() + "/../../" + repo
  is_not_exit = False
  if not is_dir(folder):
    cmd("git", ["clone", url, folder])
    is_not_exit = True
  old_cur = os.getcwd()
  os.chdir(folder)
  cmd("git", ["fetch"], False if ("1" != config.option("update-light")) else True)
  if is_not_exit or ("1" != config.option("update-light")):
    cmd("git", ["checkout", "-f", config.option("branch")])
  cmd("git", ["pull"], False if ("1" != config.option("update-light")) else True)
  os.chdir(old_cur)
  return

# qmake -------------------------------------------------
def qt_setup(platform):
  compiler = config.check_compiler(platform)
  qt_dir = config.option("qt-dir") if (-1 == platform.find("_xp")) else config.option("qt-dir-xp")
  qt_dir = (qt_dir + "/" + compiler["compiler"]) if platform_is_32(platform) else (qt_dir + "/" + compiler["compiler_64"])
  set_env("QT_DEPLOY", qt_dir + "/bin")
  return qt_dir  

def qt_version():
  qt_dir = get_env("QT_DEPLOY")
  qt_dir = qt_dir.split("/")[-3]
  return "".join(i for i in qt_dir if (i.isdigit() or i == "."))

def qt_config(platform):
  config_param = config.option("module") + " " + config.option("config")
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
  return config_param

def qt_major_version():
  qt_dir = qt_version()
  return qt_dir.split(".")[0]

def qt_copy_lib(lib, dir):
  qt_dir = get_env("QT_DEPLOY")
  if ("windows" == host_platform()):
    copy_lib(qt_dir, dir, lib)
  else:
    copy_file(qt_dir + "/../lib/lib" + lib + ".so." + qt_version(), dir + "/lib" + lib + ".so." + qt_major_version())
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
    bundle_version.append("255" if int(n) > 255 else n)

  for file in glob.glob(path + "/*.framework"):
    if not is_dir(file):
      continue
    name = os.path.basename(file)
    name = name.replace(".framework", "")

    content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    content += "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
    content += "<plist version=\"1.0\">\n"
    content += "<dict>\n"
    content += "<key>CFBundleExecutable</key>\n"
    content += ("<string>" + name + "</string>\n")
    content += "<key>CFBundleGetInfoString</key>\n"
    content += "<string>Created by " + bundle_creator + "</string>\n"
    content += "<key>CFBundleIdentifier</key>\n"
    content += "<string>" + bundle_id_url + name + "</string>\n"
    content += "<key>CFBundlePackageType</key>\n"
    content += "<string>FMWK</string>\n"
    content += "<key>CFBundleShortVersionString</key>\n"
    content += "<string>" + bundle_version[0] + "." + bundle_version[1] + "</string>\n"
    content += "<key>CFBundleSignature</key>\n"
    content += "<string>????</string>\n"
    content += "<key>CFBundleVersion</key>\n"
    content += "<string>" + bundle_version[0] + "." + bundle_version[1] + "." + bundle_version[2] + "</string>\n"
    content += "<key>LSMinimumSystemVersion</key>\n"
    content += "<string>10.0</string>\n"
    content += "</dict>\n"
    content += "</plist>"

    fileDst = file + "/Info.plist"
    if is_file(fileDst):
      delete_file(fileDst)

    fileInfo = codecs.open(fileDst, "w", "utf-8")
    fileInfo.write(content)
    fileInfo.close()
      
  return

def sdkjs_addons_checkout():
  if ("" == config.option("sdkjs-addons")):
    return
  addons_list = config.option("sdkjs-addons").rsplit(", ")
  for name in addons_list:
    if name in config.sdkjs_addons:
      git_update(config.sdkjs_addons[name])
  return

def sdkjs_addons_param():
  if ("" == config.option("sdkjs-addons")):
    return []
  params = []
  addons_list = config.option("sdkjs-addons").rsplit(", ")
  for name in addons_list:
    if name in config.sdkjs_addons:
      params.append("--addon=" + config.sdkjs_addons[name])
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

def run_as_bat(lines):
  name = "tmp.bat"
  content = "\n".join(lines)

  file = codecs.open(name, "w", "utf-8")
  file.write(content)
  file.close()

  cmd(name)
  delete_file(name)
  return

def save_as_script(path, lines):
  content = "\n".join(lines)

  file = codecs.open(path, "w", "utf-8")
  file.write(content)
  file.close()
  return

def get_file_last_modified_url(url):
  curl_command = 'curl --head %s' % (url)
  popen = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  retvalue = ""
  try:
    stdout, stderr = popen.communicate()
    popen.wait()

    lines = stdout.split("\n")
    for line in lines:
      if ':' not in line:
        continue
      line = line.strip()
      key, value = line.split(':', 1)
      key = key.upper()
      if key == "LAST-MODIFIED":
        retvalue = value

  finally:
    popen.stdout.close()
    popen.stderr.close()

  return retvalue
