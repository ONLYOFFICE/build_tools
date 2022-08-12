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

def aws_s3_upload(local, key, edition, ptype=None):
  if common.os_family == "windows":
    rc = utils.cmd(
        "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
        local, "s3://" + common.s3_bucket + "/" + key,
        verbose=True
    )
  else:
    rc = utils.sh("aws s3 cp --acl public-read --no-progress " \
        + local + " s3://" + common.s3_bucket + "/" + key, verbose=True)
  if rc == 0 and ptype is not None:
    utils.add_deploy_data("server_" + edition, ptype, local, key)
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

  key_prefix = "%s/%s/windows/server/%s/%s" % (branding.company_name_l, \
      common.release_branch, common.version, common.build)
  if rc == 0:
    utils.log_h2("server " + edition + " inno deploy")
    inno_file = utils.glob_file("exe/*.exe")
    inno_key = key_prefix + "/" + utils.get_basename(inno_file)
    rc = aws_s3_upload(inno_file, inno_key, edition, "Installer")
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

  key_prefix = branding.company_name_l + "/" + common.release_branch
  if common.platform == "linux_x86_64":
    rpm_arch = "x86_64"
  elif common.platform == "linux_aarch64":
    rpm_arch = "aarch64"
  if rc == 0:
    utils.log_h2("server " + edition + " tar deploy")
    tar_file = utils.glob_file("*.tar.gz")
    tar_key = key_prefix + "/linux/" + utils.get_basename(tar_file)
    rc = aws_s3_upload(tar_file, tar_key, edition, "Portable")
    utils.set_summary("server " + edition + " tar deploy", rc == 0)

    utils.log_h2("server " + edition + " deb deploy")
    deb_file = utils.glob_file("deb/*.deb")
    deb_key = key_prefix + "/ubuntu/" + utils.get_basename(deb_file)
    rc = aws_s3_upload(deb_file, deb_key, edition, "Ubuntu")
    utils.set_summary("server " + edition + " deb deploy", rc == 0)

    utils.log_h2("server " + edition + " rpm deploy")
    rpm_file = utils.glob_file("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm")
    rpm_key = key_prefix + "/centos/" + utils.get_basename(rpm_file)
    rc = aws_s3_upload(rpm_file, rpm_key, edition, "CentOS")
    utils.set_summary("server " + edition + " rpm deploy", rc == 0)

    utils.log_h2("server " + edition + " apt-rpm deploy")
    alt_rpm_file = utils.glob_file("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm")
    alt_rpm_key = key_prefix + "/altlinux/" + utils.get_basename(alt_rpm_file)
    rc = aws_s3_upload(alt_rpm_file, alt_rpm_key, edition, "AltLinux")
    utils.set_summary("server " + edition + " apt-rpm deploy", rc == 0)

  else:
    utils.set_summary("server " + edition + " tar deploy", False)
    utils.set_summary("server " + edition + " deb deploy", False)
    utils.set_summary("server " + edition + " rpm deploy", False)
    utils.set_summary("server " + edition + " alt-rpm deploy", False)

  utils.set_cwd(common.workspace_dir)
  return