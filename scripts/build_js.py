#!/usr/bin/env python

import config
import base

# make build.pro
def make():
  if ("1" == base.get_env("OO_NO_BUILD_JS")):
    return

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

  # desktop
  if config.check_option("module", "desktop"):
    build_sdk_desktop(base_dir + "/../sdkjs/build")
    base.create_dir(out_dir + "/desktop")
    base.copy_dir(base_dir + "/../sdkjs/deploy/sdkjs", out_dir + "/desktop/sdkjs")
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
    build_sdk_native(base_dir + "/../sdkjs/build")
    base.create_dir(out_dir + "/mobile")
    base.create_dir(out_dir + "/mobile/sdkjs")
    vendor_dir_src = base_dir + "/../web-apps/vendor/"
    sdk_dir_src = base_dir + "/../sdkjs/deploy/sdkjs/"
    # banners
    base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                       vendor_dir_src + "underscore/underscore-min.js",
                       base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                       sdk_dir_src + "common/Native/native.js",
                       sdk_dir_src + "../../common/Native/Wrappers/common.js",
                       sdk_dir_src + "common/Native/jquery_native.js"], 
                       out_dir + "/mobile/sdkjs/banners.js")
    base.create_dir(out_dir + "/mobile/sdkjs/word")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners.js", sdk_dir_src + "word/sdk-all-min.js", sdk_dir_src + "word/sdk-all.js"], out_dir + "/mobile/sdkjs/word/script.bin")
    base.create_dir(out_dir + "/mobile/sdkjs/cell")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners.js", sdk_dir_src + "cell/sdk-all-min.js", sdk_dir_src + "cell/sdk-all.js"], out_dir + "/mobile/sdkjs/cell/script.bin")
    base.create_dir(out_dir + "/mobile/sdkjs/slide")
    base.join_scripts([out_dir + "/mobile/sdkjs/banners.js", sdk_dir_src + "slide/sdk-all-min.js", sdk_dir_src + "slide/sdk-all.js"], out_dir + "/mobile/sdkjs/slide/script.bin")
    base.delete_file(out_dir + "/mobile/sdkjs/banners.js")
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
  beta = "true" if config.check_option("beta", "1") else "false"
  params = ["--beta=" + beta]
  return params + (["--level=ADVANCED"] if minimize else ["--level=WHITESPACE_ONLY", "--formatting=PRETTY_PRINT"])

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

def build_sdk_native(directory):
  #_run_npm_cli(directory)
  _run_npm(directory)
  _run_grunt(directory, get_build_param() + ["--mobile=true"] + base.sdkjs_addons_param())
  return

def build_js_develop(root_dir):
  #_run_npm_cli(root_dir + "/sdkjs/build")
  _run_npm(root_dir + "/sdkjs/build")
  _run_grunt(root_dir + "/sdkjs/build", get_build_param(False) + base.sdkjs_addons_param())
  _run_grunt(root_dir + "/sdkjs/build", ["develop"] + base.sdkjs_addons_param())
  _run_npm(root_dir + "/web-apps/build")
  _run_npm(root_dir + "/web-apps/build/sprites")
  _run_grunt(root_dir + "/web-apps/build/sprites", [])
  return
