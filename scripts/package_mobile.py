#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("MOBILE")
  if not utils.is_linux():
    utils.log("Unsupported host OS")
    return
  make_mobile()
  return

def aws_s3_upload(local, key, ptype=None):
  rc = utils.sh("aws s3 cp --acl public-read --no-progress " \
      + local + " s3://" + common.s3_bucket + "/" + key, verbose=True)
  if rc == 0 and ptype is not None:
    utils.add_deploy_data("mobile", ptype, local, key)
  return rc

def make_mobile():
  utils.set_cwd("build_tools/out")

  if common.clean:
    utils.log_h2("mobile clean")
    utils.sh("rm -rfv *.zip", verbose=True)

  zip_file = "android-libs-" + common.version + "-" + common.build + ".zip"
  zip_key = branding.company_name_l + "/" + common.release_branch + "/android/" + zip_file

  utils.log_h2("mobile build")
  rc = utils.sh("zip -r " + zip_file + " ./android* ./js", verbose=True)
  utils.set_summary("mobile build", rc == 0)

  utils.log_h2("mobile deploy")
  if rc == 0:
    rc = aws_s3_upload(zip_file, zip_key, "Android")
  utils.set_summary("mobile deploy", rc == 0)

  utils.set_cwd(common.workspace_dir)
  return
