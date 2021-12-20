#!/usr/bin/env python3

import base
import os

def make(platform, targets):
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  package_dir = os.path.abspath(git_dir + "/document-builder-package")

  if ("windows" == platform) or ("linux" == platform):

    if ("packages" in targets):

      print("Make clean")
      base.cmd_in_dir(package_dir, "make", ["clean"])

      print("Make packages")
      base.cmd_in_dir(package_dir, "make", ["packages"])

  else:

    exit(1)

  return
