#!/usr/bin/env python

import config
import base


def make():
  #check server module to build
  if(not config.check_option("module", "server")):
    return

  server_dir = base.get_script_dir() + "/../../server"

  base.cmd_in_dir(server_dir, "npm", ["install"])
  base.cmd_in_dir(server_dir, "grunt", ["--no-color", "-v"])

  example_dir = base.get_script_dir() + "/../../document-server-integration/web/documentserver-example/nodejs"
  base.cmd_in_dir(example_dir, "npm", ["install"])
