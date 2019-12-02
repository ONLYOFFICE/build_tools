#!/usr/bin/env python

import config
import base
import os

def make():
  git_dir = base.get_script_dir() + "/../.."
  old_cur = os.getcwd()

  work_dir = git_dir + "/server/FileConverter/bin"
  if not base.is_dir(work_dir):
    base.create_dir(work_dir)

  os.chdir(work_dir)

  arch = "x64"
  arch2 = "_64"
  if ("windows" == base.host_platform()) and not base.host_platform_is64():
    arch = "x86"
    arch2 = "_32"

  url = "http://repo-doc-onlyoffice-com.s3.amazonaws.com/" + base.host_platform() + "/core/" + config.option("branch") + "/latest/" + arch + "/core.zip"
  data_url = base.get_file_last_modified_url(url)
  old_data_url = base.readFile("./core.zip.data")

  if (old_data_url != data_url):
    print("-----------------------------------------------------------")
    print("Downloading core last version... --------------------------")
    print("-----------------------------------------------------------")
    if (base.is_file("./core.zip")):
      base.delete_file("./core.zip")
    if (base.is_dir("./core")):
      base.delete_dir("./core")
    if (base.is_dir("./HtmlFileInternal")):
      base.delete_dir("./HtmlFileInternal")
    base.download(url, "./core.zip")

    print("-----------------------------------------------------------")
    print("Extracting core last version... ---------------------------")
    print("-----------------------------------------------------------")

    base.extract("./core.zip", "./core")
    base.writeFile("./core.zip.data", data_url)

    platform = ""
    if ("windows" == base.host_platform()):
      platform = "win" + arch2
    else:
      platform = base.host_platform() + arch2

    base.copy_lib("./core/build/lib/" + platform, "./", "kernel")
    base.copy_lib("./core/build/lib/" + platform, "./", "graphics")
    base.copy_lib("./core/build/lib/" + platform, "./", "doctrenderer")
    base.copy_lib("./core/build/lib/" + platform, "./", "HtmlRenderer")
    base.copy_lib("./core/build/lib/" + platform, "./", "DjVuFile")
    base.copy_lib("./core/build/lib/" + platform, "./", "XpsFile")
    base.copy_lib("./core/build/lib/" + platform, "./", "PdfReader")
    base.copy_lib("./core/build/lib/" + platform, "./", "PdfWriter")
    base.copy_lib("./core/build/lib/" + platform, "./", "HtmlFile")
    base.copy_lib("./core/build/lib/" + platform, "./", "UnicodeConverter")
    base.copy_exe("./core/build/bin/" + platform, "./", "x2t")
    if ("windows" == base.host_platform()):
      base.copy_files("./core/Common/3dParty/icu/" + platform + "/build/*.dll", "./")
      base.copy_files("./core/Common/3dParty/v8/v8/out.gn/" + platform + "/release/icudt*.dat", "./")
    else:
      base.copy_files("./core/Common/3dParty/icu/" + platform + "/build/*", "./")
      base.copy_file(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/icudtl.dat", root_dir + "/converter/icudtl.dat")

    base.copy_exe("./core/build/bin/" + platform, "./", "allfontsgen")
    base.copy_exe("./core/build/bin/" + platform, "./", "allthemesgen")

  base.generate_doctrenderer_config("./DoctRenderer.config", "../../../sdkjs/deploy/", "server", "../../../web-apps/vendor/")

  if base.is_dir(git_dir + "/fonts"):
    base.delete_dir(git_dir + "/fonts")
  base.create_dir(git_dir + "/fonts")

  print("-----------------------------------------------------------")
  print("All fonts generation... -----------------------------------")
  print("-----------------------------------------------------------")
  base.cmd_exe("allfontsgen", ["--input=../../../core-fonts", "--allfonts-web=../../../sdkjs/common/AllFonts.js", "--allfonts=./AllFonts.js",
                               "--images=../../../sdkjs/common/Images", "--selection=./font_selection.bin", 
                               "--use-system=true", "--output-web=../../../fonts"])
  
  print("All presentation themes generation... ---------------------")
  print("-----------------------------------------------------------")
  base.cmd_exe("allthemesgen", ["--converter-dir=\"" + git_dir + "/server/FileConverter/bin\"", "--src=\"" + git_dir + "/sdkjs/slide/themes\"", "--output=\"" + git_dir + "/sdkjs/common/Images\""])

  os.chdir(old_cur)
  return

