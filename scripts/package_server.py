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

def aws_s3_upload(files, key, edition, ptype=None):
  key = "server/" + key
  for file in files:
    args = ["aws"]
    if hasattr(branding, "s3_endpoint_url"):
      args += ["--endpoint-url=" + branding.s3_endpoint_url]
    args += [
      "s3", "cp", "--no-progress", "--acl", "public-read",
      file, "s3://" + branding.s3_bucket + "/" + key
    ]
    if common.os_family == "windows":
      ret = utils.cmd(*args, verbose=True)
    else:
      ret = utils.sh(" ".join(args), verbose=True)
    if ret and ptype is not None:
      full_key = key
      if full_key.endswith("/"): full_key += utils.get_basename(file)
      utils.add_deploy_data(
          "server_" + edition, ptype, file, full_key,
          branding.s3_bucket, branding.s3_region
      )
  return ret

def make_windows(edition):
  if edition == "enterprise":
    product_name = "DocumentServer-EE"
  elif edition == "developer":
    product_name = "DocumentServer-DE"
  else:
    product_name = "DocumentServer"
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " build")
  ret = utils.cmd("make", "clean", verbose=True)
  args = ["-e", "PRODUCT_NAME=" + product_name]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  ret &= utils.cmd("make", "packages", *args, verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  if common.deploy and ret:
    utils.log_h2("server " + edition + " inno deploy")
    ret = aws_s3_upload(
        utils.glob_path("exe/*.exe"),
        "win/inno/%s/" % common.channel,
        edition,
        "Installer"
    )
    utils.set_summary("server " + edition + " inno deploy", ret)

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

  utils.log_h2("server " + edition + " build")
  args = ["-e", "PRODUCT_NAME=" + product_name]
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  ret = utils.sh("make clean && make packages " + " ".join(args), verbose=True)
  utils.set_summary("server " + edition + " build", ret)

  rpm_arch = "x86_64"
  if common.platform == "linux_aarch64": rpm_arch = "aarch64"

  if common.deploy:
    utils.log_h2("server " + edition + " deploy")
    if ret:
      utils.log_h2("server " + edition + " tar deploy")
      ret = aws_s3_upload(
          utils.glob_path("*.tar.gz"),
          "linux/generic/%s/" % common.channel,
          edition,
          "Portable"
      )
      utils.set_summary("server " + edition + " tar deploy", ret)

      utils.log_h2("server " + edition + " deb deploy")
      ret = aws_s3_upload(
          utils.glob_path("deb/*.deb"),
          "linux/debian/%s/" % common.channel,
          edition,
          "Debian"
      )
      utils.set_summary("server " + edition + " deb deploy", ret)

      utils.log_h2("server " + edition + " rpm deploy")
      ret = aws_s3_upload(
          utils.glob_path("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "linux/rhel/%s/" % common.channel,
          edition,
          "CentOS"
      )
      utils.set_summary("server " + edition + " rpm deploy", ret)

      utils.log_h2("server " + edition + " apt-rpm deploy")
      ret = aws_s3_upload(
          utils.glob_path("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "linux/altlinux/%s/" % common.channel,
          edition,
          "ALT Linux"
      )
      utils.set_summary("server " + edition + " apt-rpm deploy", ret)
    else:
      utils.set_summary("server " + edition + " tar deploy", False)
      utils.set_summary("server " + edition + " deb deploy", False)
      utils.set_summary("server " + edition + " rpm deploy", False)
      utils.set_summary("server " + edition + " rpm-alt deploy", False)

  utils.set_cwd(common.workspace_dir)
  return