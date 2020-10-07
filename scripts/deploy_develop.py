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

  url = "http://repo-doc-onlyoffice-com.s3.amazonaws.com/" + base.host_platform() + "/core/" + config.option("branch") + "/latest/" + arch + "/core.7z"
  data_url = base.get_file_last_modified_url(url)
  old_data_url = base.readFile("./core.7z.data")

  if (old_data_url != data_url):
    print("-----------------------------------------------------------")
    print("Downloading core last version... --------------------------")
    print("-----------------------------------------------------------")
    if (base.is_file("./core.7z")):
      base.delete_file("./core.7z")
    if (base.is_dir("./core")):
      base.delete_dir("./core")
    base.download(url, "./core.7z")

    print("-----------------------------------------------------------")
    print("Extracting core last version... ---------------------------")
    print("-----------------------------------------------------------")

    base.extract("./core.7z", "./")
    base.writeFile("./core.7z.data", data_url)

    platform = ""
    if ("windows" == base.host_platform()):
      platform = "win" + arch2
    else:
      platform = base.host_platform() + arch2

    base.copy_files("./core/*", "./")
  else:
    print("-----------------------------------------------------------")
    print("Core is up to date. ---------------------------------------")
    print("-----------------------------------------------------------")

  base.generate_doctrenderer_config("./DoctRenderer.config", "../../../sdkjs/deploy/", "server", "../../../web-apps/vendor/")
  base.support_old_versions_plugins(git_dir + "/sdkjs-plugins")

  if base.is_dir(git_dir + "/fonts"):
    base.delete_dir(git_dir + "/fonts")
  base.create_dir(git_dir + "/fonts")

  if ("mac" == base.host_platform()):
    base.mac_correct_rpath_x2t("./")

  print("-----------------------------------------------------------")
  print("All fonts generation... -----------------------------------")
  print("-----------------------------------------------------------")
  base.cmd_exe("./allfontsgen", ["--input=../../../core-fonts", "--allfonts-web=../../../sdkjs/common/AllFonts.js", "--allfonts=./AllFonts.js",
                               "--images=../../../sdkjs/common/Images", "--selection=./font_selection.bin", 
                               "--use-system=true", "--output-web=../../../fonts"])
  
  print("All presentation themes generation... ---------------------")
  print("-----------------------------------------------------------")
  base.cmd_exe("./allthemesgen", ["--converter-dir=\"" + git_dir + "/server/FileConverter/bin\"", "--src=\"" + git_dir + "/sdkjs/slide/themes\"", "--output=\"" + git_dir + "/sdkjs/common/Images\""])
  
  #print("- allthemesgen (ios) --------------------------------------")
  #base.cmd_exe("./allthemesgen", ["--converter-dir=\"" + git_dir + "/server/FileConverter/bin\"", "--src=\"" + git_dir + "/sdkjs/slide/themes\"", "--output=\"" + git_dir + "/sdkjs/common/Images\"", "--postfix=ios", "--params=280,224"])
  # android
  #print("- allthemesgen (android) ----------------------------------")
  #base.cmd_exe("./allthemesgen", ["--converter-dir=\"" + git_dir + "/server/FileConverter/bin\"", "--src=\"" + git_dir + "/sdkjs/slide/themes\"", "--output=\"" + git_dir + "/sdkjs/common/Images\"", "--postfix=android", "--params=280,224"])

  # add directories to open directories
  data_local_devel = "{\n"
  data_local_devel += "\"services\": {\n"
  data_local_devel += "\"CoAuthoring\": {\n"
  data_local_devel += "\"server\": {\n"
  data_local_devel += "\"static_content\": {\n"
  is_exist_addons = False
  for addon in config.sdkjs_addons:
    data_local_devel += ("\"/" + config.sdkjs_addons[addon] + "\" : { \"path\": \"../../../" + config.sdkjs_addons[addon] + "\" },\n")
    is_exist_addons = True
  for addon in config.web_apps_addons:
    data_local_devel += ("\"/" + config.web_apps_addons[addon] + "\" : { \"path\": \"../../../" + config.web_apps_addons[addon] + "\" },\n")
    is_exist_addons = True
  if is_exist_addons:
    data_local_devel = data_local_devel[:-2]
  data_local_devel += "\n"
  data_local_devel += "}\n"
  data_local_devel += "}\n"
  data_local_devel += "}\n"
  data_local_devel += "}\n"
  data_local_devel += "}\n"
  base.writeFile(git_dir + "/server/Common/config/local-development-" + base.host_platform() + ".json", data_local_devel)

  os.chdir(old_cur)
  return

