#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make(edition):
  utils.log_h1("SERVER (" + edition.upper() + ")")
  if utils.is_windows():
    make_windows(edition)
  elif utils.is_linux():
    make_linux(edition)
  else:
    utils.log("Unsupported host OS")
  return

def make_windows(edition):
  if edition == "enterprise":
    product_name = "DocumentServer-EE"
  elif edition == "developer":
    product_name = "DocumentServer-DE"
  else:
    product_name = "DocumentServer"
  utils.set_cwd("document-server-package")

  rc = utils.cmd("make", "clean", verbose=True)
  common.summary["server " + edition + " clean"] = rc

  args = ["-e", "PRODUCT_NAME=" + product_name]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  rc = utils.cmd("make", "packages", *args, verbose=True)
  common.summary["server " + edition + " build"] = rc

  utils.set_cwd(common.workspace_dir)
  return

def make_linux(edition):
  if edition == "enterprise":
    product_name = "documentserver-ee"
  elif edition == "developer":
    product_name = "documentserver-de"
  else:
    product_name = "documentserver"
  utils.set_cwd("document-server-package")

  rc = utils.sh("make clean", verbose=True)
  common.summary["server " + edition + " clean"] = rc

  args = ["-e", "PRODUCT_NAME=" + product_name]
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  rc = utils.sh("make packages " + " ".join(args), verbose=True)
  common.summary["server " + edition + " build"] = rc

  utils.set_cwd(common.workspace_dir)
  return