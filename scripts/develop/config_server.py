#!/usr/bin/env python

import config
import base
import os
import json

def get_core_url(arch, branch):
  return "http://repo-doc-onlyoffice-com.s3.amazonaws.com/" + base.host_platform() + "/core/" + branch + "/latest/" + arch + "/core.7z"

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

  url = get_core_url(arch, config.option("branch"))
  data_url = base.get_file_last_modified_url(url)
  if (data_url == "" and config.option("branch") != "develop"):
    url = get_core_url(arch, "develop")
    data_url = base.get_file_last_modified_url(url)
  
  old_data_url = base.readFile("./core.7z.data")

  if (data_url != "" and old_data_url != data_url):
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

  if not base.is_dir(git_dir + "/fonts"):
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
  addon_base_path = "../../"
  server_config = {}
  static_content = {}
  sql = {}
  
  server_addons = []
  if (config.option("server-addons") != ""):
    server_addons = config.option("server-addons").rsplit(", ")
  if ("server-lockstorage" in server_addons):
    server_config["editorDataStorage"] = "editorDataRedis"
  
  sdkjs_addons = []
  if (config.option("sdkjs-addons") != ""):
    sdkjs_addons = config.option("sdkjs-addons").rsplit(", ")
  for addon in sdkjs_addons:
    static_content["/" + addon] = {"path": addon_base_path + addon}

  web_apps_addons = []
  if (config.option("web-apps-addons") != ""):
    web_apps_addons = config.option("web-apps-addons").rsplit(", ")
  for addon in web_apps_addons:
    static_content["/" + addon] = {"path": addon_base_path + addon}
    
  if (config.option("external-folder") != ""):
    external_folder = config.option("external-folder")
    static_content["/sdkjs"] = {"path": addon_base_path + external_folder + "/sdkjs"}
    static_content["/web-apps"] = {"path": addon_base_path + external_folder + "/web-apps"}
    
  if (config.option("sql-type") != ""):
    sql["type"] = config.option("sql-type")
  if (config.option("db-port") != ""):
    sql["dbPort"] = config.option("db-port")
  if (config.option("db-user") != ""):
    sql["dbUser"] = config.option("db-user")
  if (config.option("db-pass") != ""):
    sql["dbPass"] = config.option("db-pass")

  server_config["static_content"] = static_content
  
  json_file = git_dir + "/server/Common/config/local-development-" + base.host_platform() + ".json"
  base.writeFile(json_file, json.dumps({"services": {"CoAuthoring": {"server": server_config, "sql": sql}}}, indent=2))

  #site url
  example_config = {}
  example_config["port"] = 80
  example_config["siteUrl"] = "http://" + config.option("siteUrl") + ":8000/"
  example_config["apiUrl"] = "web-apps/apps/api/documents/api.js"
  example_config["preloaderUrl"] = "web-apps/apps/api/documents/cache-scripts.html"
  json_file = git_dir + "/document-server-integration/web/documentserver-example/nodejs/config/local-development-" + base.host_platform() + ".json"
  base.writeFile(json_file, json.dumps({"server": example_config}, indent=2))
  
  os.chdir(old_cur)
  return

