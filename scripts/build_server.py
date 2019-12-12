#!/usr/bin/env python

import config
import base


def make():
  server_dir = base.get_script_dir() + "/../../server"

  base.cmd_in_dir(server_dir, "npm", ["install"])
  base.cmd_in_dir(server_dir, "grunt", ["--no-color", "-v"])
