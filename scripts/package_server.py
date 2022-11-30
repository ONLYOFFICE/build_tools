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
  rc = 0
  for file in files:
    if common.os_family == "windows":
      rc += utils.cmd(
          "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
          file, "s3://" + branding.s3_bucket + "/" + key,
          verbose=True)
    else:
      rc += utils.sh(
          "aws s3 cp --acl public-read --no-progress " \
          + file + " s3://" + branding.s3_bucket + "/" + key,
          verbose=True)
    if rc == 0 and ptype is not None:
      if key.endswith("/"): key += utils.get_basename(file)
      utils.add_deploy_data("server_" + edition, ptype, file, key)
  return rc

def make_windows(edition):
  if edition == "enterprise":
    product_name = "DocumentServer-EE"
  elif edition == "developer":
    product_name = "DocumentServer-DE"
  else:
    product_name = "DocumentServer"
  utils.set_cwd("document-server-package")

  utils.log_h2("server " + edition + " clean")
  rc = utils.cmd("make", "clean", verbose=True)
  utils.set_summary("server " + edition + " clean", rc == 0)

  utils.log_h2("server " + edition + " build")
  args = ["-e", "PRODUCT_NAME=" + product_name]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  rc = utils.cmd("make", "packages", *args, verbose=True)
  utils.set_summary("server " + edition + " build", rc == 0)

  if rc == 0:
    utils.log_h2("server " + edition + " inno deploy")
    rc = aws_s3_upload(
        utils.glob_file("exe/*.exe"),
        "win/inno/%s/" % common.channel,
        edition,
        "Installer")
  utils.set_summary("server " + edition + " inno deploy", rc == 0)

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

  utils.log_h2("server " + edition + " clean")
  rc = utils.sh("make clean", verbose=True)
  utils.set_summary("server " + edition + " clean", rc == 0)

  utils.log_h2("server " + edition + " build")
  args = ["-e", "PRODUCT_NAME=" + product_name]
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-server-package"]
  rc = utils.sh("make packages " + " ".join(args), verbose=True)
  utils.set_summary("server " + edition + " build", rc == 0)

  rpm_arch = "x86_64"
  if common.platform == "linux_aarch64": rpm_arch = "aarch64"

  if rc == 0:
    utils.log_h2("server " + edition + " tar deploy")
    rc = aws_s3_upload(
        utils.glob_file("*.tar.gz"),
        "linux/generic/%s/" % common.channel,
        edition,
        "Portable")
    utils.set_summary("server " + edition + " tar deploy", rc == 0)

    utils.log_h2("server " + edition + " deb deploy")
    rc = aws_s3_upload(
        utils.glob_file("deb/*.deb"),
        "linux/debian/%s/" % common.channel,
        edition,
        "Debian")
    utils.set_summary("server " + edition + " deb deploy", rc == 0)

    utils.log_h2("server " + edition + " rpm deploy")
    rc = aws_s3_upload(
        utils.glob_file("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
        "linux/rhel/%s/" % common.channel,
        edition,
        "CentOS")
    utils.set_summary("server " + edition + " rpm deploy", rc == 0)

    utils.log_h2("server " + edition + " apt-rpm deploy")
    rc = aws_s3_upload(
        utils.glob_file("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
        "linux/altlinux/%s/" % common.channel,
        edition,
        "ALT Linux")
    utils.set_summary("server " + edition + " apt-rpm deploy", rc == 0)

  else:
    utils.set_summary("server " + edition + " tar deploy", False)
    utils.set_summary("server " + edition + " deb deploy", False)
    utils.set_summary("server " + edition + " rpm deploy", False)
    utils.set_summary("server " + edition + " rpm-alt deploy", False)

  utils.set_cwd(common.workspace_dir)
  return