#!/usr/bin/env python

import config
import base
import datetime

def make():
  #check server module to build
  if(not config.check_option("module", "server")):
    return

  server_dir = base.get_script_dir() + "/../../server"

  base.cmd_in_dir(server_dir, "npm", ["install"])
  base.cmd_in_dir(server_dir, "grunt", ["--no-color", "-v"])

    #env variables
  product_version = base.get_env('PRODUCT_VERSION')
  if(not product_version):
    product_version = "0.0.0"

  build_number = base.get_env('BUILD_NUMBER')
  if(not build_number):
    build_number = "0"

  cur_date = datetime.date.today().strftime("%m/%d/%Y")

  server_build_dir = server_dir + "/build/server"

  base.replaceInFileRE(server_build_dir + "/Common/sources/commondefines.js", "const buildNumber = [0-9]*", "const buildNumber = " + build_number)
  base.replaceInFileRE(server_build_dir + "/Common/sources/license.js", "const buildDate = '[0-9-/]*'", "const buildDate = '" + cur_date + "'")
  base.replaceInFileRE(server_build_dir + "/Common/sources/commondefines.js", "const buildVersion = '[0-9.]*'", "const buildVersion = '" + product_version + "'")

  base.cmd_in_dir(server_build_dir + "/DocService", "pkg", [".", "-t", 'node10-linux', "-o", "docservice"])
  base.cmd_in_dir(server_build_dir + "/FileConverter", "pkg", [".", "-t", 'node10-linux', "-o", "converter"])
  base.cmd_in_dir(server_build_dir + "/Metrics", "pkg", [".", "-t", 'node10-linux', "-o", "metrics"])
  base.cmd_in_dir(server_build_dir + "/SpellChecker", "pkg", [".", "-t", 'node10-linux', "-o", "spellchecker"])

  example_dir = base.get_script_dir() + "/../../document-server-integration/web/documentserver-example/nodejs"
  base.cmd_in_dir(example_dir, "npm", ["install"])
