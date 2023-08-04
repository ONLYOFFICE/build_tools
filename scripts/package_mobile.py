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

  zip_file = "build-" + common.version + "-" + common.build + ".zip"

  if common.clean:
    utils.log_h2("mobile clean")
    utils.sh("rm -rfv *.zip", verbose=True)

  utils.log_h2("mobile build")
  ret = utils.sh("zip -r " + zip_file + " ./android* ./js", verbose=True)
  utils.set_summary("mobile build", ret)

  if common.deploy:
    if ret:
      utils.log_h2("mobile deploy")
      key = "mobile/android/" + zip_file
      aws_kwargs = { "acl": "public-read" }
      if hasattr(branding, "s3_endpoint_url"):
        aws_kwargs["endpoint_url"] = branding.s3_endpoint_url
      ret = utils.s3_upload(
        zip_file, "s3://" + branding.s3_bucket + "/" + key, **aws_kwargs)
      if ret:
        utils.add_deploy_data(key)
        utils.log("URL: " + branding.s3_base_url + "/" + key)
    utils.set_summary("mobile deploy", ret)

  utils.set_cwd(common.workspace_dir)
  return
