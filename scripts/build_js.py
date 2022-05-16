#!/usr/bin/env python

import config
import base
import os

def correct_sdkjs_licence(directory):
  branding = config.option("branding")
  if "" == branding or "onlyoffice" == branding:
    return
  license = base.readFileLicence(directory + "/word/sdk-all-min.js")
  base.replaceFileLicence(directory + "/common/Charts/ChartStyles.js", license)
  base.replaceFileLicence(directory + "/common/hash/hash/engine.js", license)
  base.replaceFileLicence(directory + "/common/hash/hash/engine_ie.js", license)
  base.replaceFileLicence(directory + "/common/Native/native.js", license)
  base.replaceFileLicence(directory + "/common/Native/native_graphics.js", license)
  base.replaceFileLicence(directory + "/common/spell/spell/spell.js", license)
  base.replaceFileLicence(directory + "/common/spell/spell/spell_ie.js", license)
  base.replaceFileLicence(directory + "/pdf/src/engine/drawingfile.js", license)
  base.replaceFileLicence(directory + "/pdf/src/engine/drawingfile_ie.js", license)
  base.replaceInFile(directory + "/word/sdk-all-min.js", "onlyoffice-spellchecker", "r7-spellchecker")
  base.replaceInFile(directory + "/slide/sdk-all-min.js", "onlyoffice-spellchecker", "r7-spellchecker")
  base.replaceInFile(directory + "/cell/sdk-all-min.js", "onlyoffice-spellchecker", "r7-spellchecker")
  return

# make build.pro
def make():
  if ("1" == base.get_env("OO_NO_BUILD_JS")):
    return

  base.set_env('NODE_ENV', 'production')

  base_dir = base.get_script_dir() + "/.."
  out_dir = base_dir + "/out/js/";
  branding = config.option("branding-name")
  if ("" == branding):
    branding = "onlyoffice"
  out_dir += branding
  base.create_dir(out_dir)

  # builder
  build_interface(base_dir + "/../web-apps/build")
  build_sdk_builder(base_dir + "/../sdkjs/build")
  base.create_dir(out_dir + "/builder")
  base.copy_dir(base_dir + "/../web-apps/deploy/web-apps", out_dir + "/builder/web-apps")
  base.copy_dir(base_dir + "/../sdkjs/deploy/sdkjs", out_dir + "/builder/sdkjs")
  correct_sdkjs_licence(out_dir + "/builder/sdkjs")

  # desktop
  if config.check_option("module", "desktop"):
    build_sdk_desktop(base_dir + "/../sdkjs/build")
    base.create_dir(out_dir + "/desktop")
    base.copy_dir(base_dir + "/../sdkjs/deploy/sdkjs", out_dir + "/desktop/sdkjs")
    correct_sdkjs_licence(out_dir + "/desktop/sdkjs")
    base.copy_dir(base_dir + "/../web-apps/deploy/web-apps", out_dir + "/desktop/web-apps")
    if not base.is_file(out_dir + "/desktop/sdkjs/common/AllFonts.js"):
      base.copy_file(base_dir + "/../sdkjs/common/HtmlFileInternal/AllFonts.js", out_dir + "/desktop/sdkjs/common/AllFonts.js")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/documenteditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/documenteditor/mobile")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/presentationeditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/presentationeditor/mobile")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/spreadsheeteditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/spreadsheeteditor/mobile")
    base.copy_file(base_dir + "/../web-apps/apps/api/documents/index.html.desktop", out_dir + "/desktop/web-apps/apps/api/documents/index.html")
    
    build_interface(base_dir + "/../desktop-apps/common/loginpage/build")
    base.copy_file(base_dir + "/../desktop-apps/common/loginpage/deploy/index.html", out_dir + "/desktop/index.html")
  
  # mobile
  if config.check_option("module", "mobile"):
    build_sdk_native(base_dir + "/../sdkjs/build", False)
    base.create_dir(out_dir + "/mobile")
    base.create_dir(out_dir + "/mobile/sdkjs")
    vendor_dir_src = base_dir + "/../web-apps/vendor/"
    sdk_dir_src = base_dir + "/../sdkjs/deploy/sdkjs/"
    
    base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                   vendor_dir_src + "underscore/underscore-min.js",
                   base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                   base_dir + "/../sdkjs/common/Native/native.js",
                   base_dir + "/../sdkjs/common/Native/Wrappers/common.js",
                   base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
                   out_dir + "/mobile/sdkjs/banners_word.js")

    base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                       vendor_dir_src + "underscore/underscore-min.js",
                       base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                       base_dir + "/../sdkjs/common/Native/native.js",
                       base_dir + "/../sdkjs/cell/native/common.js",
                       base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
                       out_dir + "/mobile/sdkjs/banners_cell.js")

    base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                       vendor_dir_src + "underscore/underscore-min.js",
                       base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                       base_dir + "/../sdkjs/common/Native/native.js",
                       base_dir + "/../sdkjs/common/Native/Wrappers/common.js",
                       base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
                       out_dir + "/mobile/sdkjs/banners_slide.js")

    base.create_dir(out_dir + "/mobile/sdkjs/word")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners_word.js", sdk_dir_src + "word/sdk-all-min.js", sdk_dir_src + "word/sdk-all.js"], out_dir + "/mobile/sdkjs/word/script.bin")
    base.create_dir(out_dir + "/mobile/sdkjs/cell")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners_cell.js", sdk_dir_src + "cell/sdk-all-min.js", sdk_dir_src + "cell/sdk-all.js"], out_dir + "/mobile/sdkjs/cell/script.bin")
    base.create_dir(out_dir + "/mobile/sdkjs/slide")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners_slide.js", sdk_dir_src + "slide/sdk-all-min.js", sdk_dir_src + "slide/sdk-all.js"], out_dir + "/mobile/sdkjs/slide/script.bin")

    base.delete_file(out_dir + "/mobile/sdkjs/banners_word.js")
    base.delete_file(out_dir + "/mobile/sdkjs/banners_cell.js")
    base.delete_file(out_dir + "/mobile/sdkjs/banners_slide.js")
  return

# JS build
def _run_npm(directory):
  return base.cmd_in_dir(directory, "npm", ["install"])

def _run_npm_cli(directory):
  return base.cmd_in_dir(directory, "npm", ["install", "-g", "grunt-cli"])

def _run_grunt(directory, params=[]):
  return base.cmd_in_dir(directory, "grunt", params)

def build_interface(directory):
  _run_npm(directory)
  _run_grunt(directory, ["--force"] + base.web_apps_addons_param())
  return

def get_build_param(minimize=True):
  minimize_scripts = minimize
  if config.check_option("jsminimize", "0"):
    minimize_scripts = False
  beta = "true" if config.check_option("beta", "1") else "false"
  params = ["--beta=" + beta]
  return params + (["--level=ADVANCED"] if minimize_scripts else ["--level=WHITESPACE_ONLY", "--formatting=PRETTY_PRINT"])

def build_sdk_desktop(directory):
  #_run_npm_cli(directory)
  _run_npm(directory)  
  _run_grunt(directory, get_build_param() + ["--desktop=true"] + base.sdkjs_addons_param() + base.sdkjs_addons_desktop_param())
  return

def build_sdk_builder(directory):
  #_run_npm_cli(directory)
  _run_npm(directory)
  _run_grunt(directory, get_build_param() + base.sdkjs_addons_param())
  return

def build_sdk_native(directory, minimize=True):
  #_run_npm_cli(directory)
  _run_npm(directory)
  _run_grunt(directory, get_build_param(minimize) + ["--mobile=true"] + base.sdkjs_addons_param())
  return

def build_js_develop(root_dir):
  #_run_npm_cli(root_dir + "/sdkjs/build")
  external_folder = config.option("--external-folder")
  if (external_folder != ""):
    external_folder = "/" + external_folder
    
  _run_npm(root_dir + external_folder + "/sdkjs/build")
  _run_grunt(root_dir + external_folder + "/sdkjs/build", get_build_param(False) + base.sdkjs_addons_param())
  _run_grunt(root_dir + external_folder + "/sdkjs/build", ["develop"] + base.sdkjs_addons_param())
  _run_npm(root_dir + external_folder + "/web-apps/build")
  _run_npm(root_dir + external_folder + "/web-apps/build/sprites")
  _run_grunt(root_dir + external_folder + "/web-apps/build/sprites", [])

  old_cur = os.getcwd()
  old_product_version = base.get_env("PRODUCT_VERSION")
  base.set_env("PRODUCT_VERSION", old_product_version + "d")
  os.chdir(root_dir + external_folder + "/web-apps/vendor/framework7-react")
  base.cmd("npm", ["install"])
  base.cmd("npm", ["run", "deploy-word"])
  base.cmd("npm", ["run", "deploy-cell"])
  base.cmd("npm", ["run", "deploy-slide"])
  base.set_env("PRODUCT_VERSION", old_product_version)
  os.chdir(old_cur)
  return
