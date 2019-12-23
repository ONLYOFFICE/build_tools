#!/usr/bin/env python

import config
import base

import re
import shutil
from tempfile import mkstemp

import datetime

def sed(pattern, replace, source, dest=None, count=0):
  """Reads a source file and writes the destination file.
  In each line, replaces pattern with replace.

  Args:
    pattern (str): pattern to match (can be re.pattern)
    replace (str): replacement str
    source  (str): input filename
    count (int):   number of occurrences to replace
    dest (str):    destination filename, if not given, source will be over written.
  """

  fin = open(source, 'r')
  num_replaced = count

  if dest:
    fout = open(dest, 'w')
  else:
    fd, name = mkstemp()
    fout = open(name, 'w')

  for line in fin:
    out = re.sub(pattern, replace, line)
    fout.write(out)

    if out != line:
      num_replaced += 1
    if count and num_replaced > count:
      break
  try:
    fout.writelines(fin.readlines())
  except Exception as E:
    raise E

  fin.close()
  fout.close()

  if not dest:
    shutil.move(name, source)


def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  plugins_dir = git_dir + "/sdkjs-plugins"
  branding = config.branding()

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    if (-1 != native_platform.find("_xp")):
      print("Server module not supported on Windows XP")
      continue

    if (-1 != native_platform.find("ios")):
      print("Server module not supported on iOS")
      continue

    if (-1 != native_platform.find("android")):
      print("Server module not supported on Android")
      continue

    root_dir = base_dir + ("/" + native_platform + "/" + branding + "/documentserver")
    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    build_server_dir = root_dir + '/server'
    server_dir = base.get_script_dir() + "/../../server"
    base.copy_dir(server_dir + '/build/server', build_server_dir)

    qt_dir = base.qt_setup(native_platform)
    platform = native_platform

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    converter_dir = root_dir + "/server/FileConverter/bin"
    base.create_dir(converter_dir)

    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "doctrenderer")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, converter_dir, "x2t")

    base.generate_doctrenderer_config(converter_dir + "/DoctRenderer.config", "../../../", "server")

    # icu
    if (0 == platform.find("win")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icudt58.dll", converter_dir + "/icudt58.dll")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icuuc58.dll", converter_dir + "/icuuc58.dll")

    if (0 == platform.find("linux")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.so.58", converter_dir + "/libicudata.so.58")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.so.58", converter_dir + "/libicuuc.so.58")

    if (0 == platform.find("mac")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.58.dylib", converter_dir + "/libicudata.58.dylib")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.58.dylib", converter_dir + "/libicuuc.58.dylib")

    if (0 == platform.find("win")):
      base.copy_files(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/release/icudt*.dat", converter_dir + "/")
    else:
      base.copy_file(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/icudtl.dat", converter_dir + "/icudtl.dat")

    # builder
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, converter_dir, "docbuilder")
    base.copy_dir(git_dir + "/DocumentBuilder/empty", converter_dir + "/empty")

    # html
    base.create_dir(converter_dir + "/HtmlFileInternal")
    base.copy_exe(core_build_dir + "/lib/" + platform_postfix, converter_dir + "/HtmlFileInternal", "HtmlFileInternal")
    base.copy_files(core_dir + "/Common/3dParty/cef/" + platform + "/build/*", converter_dir + "/HtmlFileInternal")
    if (0 == platform.find("win")):
      base.delete_file(root_dir + "/HtmlFileInternal/cef_sandbox.lib")
      base.delete_file(root_dir + "/HtmlFileInternal/libcef.lib")

    # js
    js_dir = root_dir
    base.copy_dir(base_dir + "/js/" + branding + "/builder/sdkjs", js_dir + "/sdkjs")
    base.copy_dir(base_dir + "/js/" + branding + "/builder/web-apps", js_dir + "/web-apps")
    
    # plugins
    base.create_dir(js_dir + "/sdkjs-plugins")
    
    # base.copy_dir(plugins_dir + "/clipart", js_dir + "/sdkjs-plugins/clipart")
    base.copy_dir(plugins_dir + "/code", js_dir + "/sdkjs-plugins/code")
    base.copy_dir(plugins_dir + "/macros", js_dir + "/sdkjs-plugins/macros")
    base.copy_dir(plugins_dir + "/ocr", js_dir + "/sdkjs-plugins/ocr")
    base.copy_dir(plugins_dir + "/photoeditor", js_dir + "/sdkjs-plugins/photoeditor")
    base.copy_dir(plugins_dir + "/speech", js_dir + "/sdkjs-plugins/speech")
    base.copy_dir(plugins_dir + "/synonim", js_dir + "/sdkjs-plugins/synonim")
    base.copy_dir(plugins_dir + "/translate", js_dir + "/sdkjs-plugins/translate")
    base.copy_dir(plugins_dir + "/youtube", js_dir + "/sdkjs-plugins/youtube")
    base.copy_file(plugins_dir + "/pluginBase.js", js_dir + "/sdkjs-plugins/pluginBase.js")
    base.copy_file(plugins_dir + "/plugins.css", js_dir + "/sdkjs-plugins/plugins.css")
    
    # tools
    tools_dir = root_dir + "/server/tools"
    base.create_dir(tools_dir)
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allfontsgen")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allthemesgen")

    #env variables
    product_version = base.get_env('PRODUCT_VERSION')
    if(not product_version):
      product_version = "0.0.0"
      base.set_env('PRODUCT_VERSION', product_version)

    build_number = base.get_env('BUILD_NUMBER')
    if(not build_number):
      build_number = "0"
      base.set_env('BUILD_NUMBER', build_number)

    publisher_name = base.get_env('PUBLISHER_NAME')
    if(not publisher_name):
      publisher_name = "Ascensio System SIA"
      base.set_env('PUBLISHER_NAME', publisher_name)

    publisher_url = base.get_env('PUBLISHER_URL')
    if(not publisher_url):
      publisher_url = "https://www.onlyoffice.com/"
      base.set_env('PUBLISHER_URL', publisher_url)

    base.set_env("PRODUCT_VERSION", product_version)
    base.set_env("BUILD_NUMBER", build_number)
    base.set_env("PUBLISHER_NAME", publisher_name)
    base.set_env("PUBLISHER_URL", publisher_url)

    branding_dir = base.get_env('BRANDING_DIR')
    if(not branding_dir):
      branding_dir = 'branding'

    #dictionaries
    spellchecker_dictionaries = build_server_dir + '/SpellChecker/dictionaries'
    spellchecker_dictionaries_files = server_dir + '/../dictionaries/*_*'
    base.create_dir(spellchecker_dictionaries)
    base.copy_files(spellchecker_dictionaries_files, spellchecker_dictionaries)

    if (0 == platform.find("win")):
      exec_ext = '.exe'
    else:
      exec_ext = ''

    #schema
    schema_files = server_dir + '/schema'
    schema = build_server_dir + '/schema'
    base.create_dir(schema)
    base.copy_dir(schema_files, schema)

    #core-fonts
    core_fonts_files = server_dir + '/../core-fonts'
    core_fonts = build_server_dir + '/../core-fonts'
    base.create_dir(core_fonts)
    base.copy_dir_content(core_fonts_files, core_fonts, "", ".git")

    #license
    license_file1 = server_dir + '/LICENSE.txt'
    license_file2 = server_dir + '/3rd-Party.txt'
    license_dir = server_dir + '/license'
    license = build_server_dir + '/license'
    base.copy_file(license_file1, build_server_dir)
    base.copy_file(license_file2, build_server_dir)
    base.copy_dir(license_dir, license)

    #branding
    welcome_files = server_dir + '/' + branding_dir + '/welcome'
    welcome = build_server_dir + '/welcome'
    base.create_dir(welcome)
    base.copy_dir(welcome_files, welcome)

    info_files = server_dir + '/' + branding_dir + '/info'
    info = build_server_dir + '/info'
    base.create_dir(info)
    base.copy_dir(info_files, info)

    custom_public_key = branding_dir + '/licenseKey.pem'

    if(base.is_exist(custom_public_key)):
      base.copy_file(custom_public_key, build_server_dir + '/Common/sources')

    cur_date = datetime.date.today().strftime("%m/%d/%Y")

    base.replaceInFileRE(build_server_dir + "/Common/sources/commondefines.js", "const buildNumber = [0-9]*", "const buildNumber = " + build_number)
    base.replaceInFileRE(build_server_dir + "/Common/sources/license.js", "const buildDate = '[0-9-/]*'", "const buildDate = '" + cur_date + "'")
    base.replaceInFileRE(build_server_dir + "/Common/sources/commondefines.js", "const buildVersion = '[0-9.]*'", "const buildVersion = '" + product_version + "'")

  return

