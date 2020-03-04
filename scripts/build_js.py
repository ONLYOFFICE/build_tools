#!/usr/bin/env python

import config
import base

# make build.pro
def make():
  if ("1" == base.get_env("OO_NO_BUILD_JS")):
    return
  if ("core" == config.option("module")):
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
  build_sdk_desktop(base_dir + "/../sdkjs/build")
  if config.check_option("module", "desktop"):
    build_sdk_desktop(base_dir + "/../sdkjs/build")
    base.create_dir(out_dir + "/desktop")
    base.copy_dir(base_dir + "/../sdkjs/deploy/sdkjs", out_dir + "/desktop/sdkjs")
    base.copy_dir(base_dir + "/../web-apps/deploy/web-apps", out_dir + "/desktop/web-apps")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/documenteditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/documenteditor/mobile")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/presentationeditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/presentationeditor/mobile")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/spreadsheeteditor/embed")
    base.delete_dir(out_dir + "/desktop/web-apps/apps/spreadsheeteditor/mobile")
    base.copy_file(base_dir + "/../web-apps/apps/api/documents/index.html.desktop", out_dir + "/desktop/web-apps/apps/api/documents/index.html")
    
    build_interface(base_dir + "/../desktop-apps/common/loginpage/build")
    base.copy_file(base_dir + "/../desktop-apps/common/loginpage/deploy/index.html", out_dir + "/desktop/index.html")
  return

# JS build
def _run_npm(directory):
  return base.cmd_in_dir(directory, "npm", ["install"])

def _run_grunt(directory, params=[]):
  return base.cmd_in_dir(directory, "grunt", params)

def build_interface(directory):
  _run_npm(directory)
  _run_grunt(directory, ["--force"] + base.web_apps_addons_param())
  return

def build_sdk_desktop(directory):
  _run_npm(directory)  
  _run_grunt(directory, ["--level=ADVANCED", "--desktop=true"] + base.sdkjs_addons_param())
  return

def build_sdk_builder(directory):
  _run_npm(directory)
  _run_grunt(directory, ["--level=ADVANCED"] + base.sdkjs_addons_param())
  return

def build_js_develop(root_dir):
  _run_npm(root_dir + "/sdkjs/build")
  _run_grunt(root_dir + "/sdkjs/build", ["--level=WHITESPACE_ONLY", "--formatting=PRETTY_PRINT"] + base.sdkjs_addons_param())
  _run_grunt(root_dir + "/sdkjs/build", ["develop"] + base.sdkjs_addons_param())
  _run_npm(root_dir + "/web-apps/build")
  _run_npm(root_dir + "/web-apps/build/sprites")
  _run_grunt(root_dir + "/web-apps/build/sprites", [])
  return
