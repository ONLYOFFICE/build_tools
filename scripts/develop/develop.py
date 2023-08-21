import sys
sys.path.append('scripts')
sys.path.append('scripts/develop')
import base
import build_js
import build_server 
import config
import dependence
import config_server as develop_config_server

base_dir = base.get_script_dir(__file__)

def build_docker_server():
  dependence.check__docker_dependencies()
  build_develop_server()

def build_docker_sdk_web_apps(dir):
  dependence.check__docker_dependencies()
  build_js.build_js_develop(dir)

def build_develop_server():
  build_server.build_server_develop()
  build_js.build_js_develop(base_dir + "/../../..")
  develop_config_server.make()
  if ("" != config.option("branding")):
    branding_develop_script_dir = base_dir + "/../../../" + config.option("branding") + "/build_tools/scripts"
    if base.is_file(branding_develop_script_dir + "/develop.py"):
      base.cmd_in_dir(branding_develop_script_dir, "python", ["develop.py"], True)

def make():
  if ("1" != config.option("develop")):
    return
  if not dependence.check_dependencies():
    exit(1)
  build_develop_server()
  exit(0)
  