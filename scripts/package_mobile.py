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

def make_mobile():
  utils.set_cwd("build_tools/out")

  if common.clean:
    utils.log_h2("mobile clean")
    utils.sh("rm -rfv *.zip", verbose=True)

  zip_file = "build-" + common.version + "-" + common.build + ".zip"
  s3_key = "mobile/android/%s/%s" % (common.channel, zip_file)

  utils.log_h2("mobile build")
  ret = utils.sh("zip -r " + zip_file + " ./android* ./js", verbose=True)
  utils.set_summary("mobile build", ret)

  if common.deploy:
    utils.log_h2("mobile deploy")
    if ret:
      ret = utils.sh(
          "aws s3 cp --acl public-read --no-progress " \
          + zip_file + " s3://" + branding.s3_bucket + "/" + s3_key,
          verbose=True
      )
    if ret:
      utils.add_deploy_data(
          "mobile", "Android", zip_file, s3_key,
          branding.s3_bucket, branding.s3_region
      )
    utils.set_summary("mobile deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
