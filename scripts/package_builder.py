#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("BUILDER")
  if not (utils.is_windows() or utils.is_macos() or utils.is_linux()):
    utils.log("Unsupported host OS")
    return
  if common.deploy:
    make_archive()
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos_linux()
  elif utils.is_linux():
    make_macos_linux()
  return

def s3_upload(files, dst):
  if not files: return False
  ret = True
  for f in files:
    key = dst + utils.get_basename(f) if dst.endswith("/") else dst
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    if upload:
      utils.log("URL: " + branding.s3_base_url + "/" + key)
    ret &= upload
  return ret

def make_archive():
  utils.set_cwd(utils.get_path(
    "build_tools/out/" + common.prefix + "/" + branding.company_name.lower()))

  utils.log_h2("builder archive build")
  utils.delete_file("builder.7z")
  args = ["7z", "a", "-y", "builder.7z", "./documentbuilder/*"]
  if utils.is_windows():
    ret = utils.cmd(*args, verbose=True)
  else:
    ret = utils.sh(" ".join(args), verbose=True)
  utils.set_summary("builder archive build", ret)

  utils.log_h2("builder archive deploy")
  dest = "builder-" + common.prefix.replace("_","-") + ".7z"
  dest_latest = "archive/%s/latest/%s" % (common.branch, dest)
  dest_version = "archive/%s/%s/%s" % (common.branch, common.build, dest)
  ret = utils.s3_upload(
    "builder.7z", "s3://" + branding.s3_bucket + "/" + dest_version)
  utils.set_summary("builder archive deploy", ret)
  if ret:
    utils.log("URL: " + branding.s3_base_url + "/" + dest_version)
    utils.s3_copy(
      "s3://" + branding.s3_bucket + "/" + dest_version,
      "s3://" + branding.s3_bucket + "/" + dest_latest)
    utils.log("URL: " + branding.s3_base_url + "/" + dest_latest)

  utils.set_cwd(common.workspace_dir)
  return

def make_windows():
  global package_version, arch
  utils.set_cwd("document-builder-package")

  package_version = common.version + "." + common.build
  arch = {
    "windows_x64": "x64",
    "windows_x86": "x86"
  }[common.platform]

  if common.clean:
    utils.log_h2("builder clean")
    utils.delete_dir("build")
    utils.delete_dir("zip")

  if make_prepare():
    make_zip()
    make_wheel()
  else:
    utils.set_summary("builder zip build", False)
    utils.set_summary("builder python wheel build", False)

  utils.set_cwd(common.workspace_dir)
  return

def make_prepare():
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  if common.sign:
    args += ["-Sign"]

  utils.log_h2("builder prepare")
  ret = utils.ps1("make.ps1", args, verbose=True)
  utils.set_summary("builder prepare", ret)
  return ret

def make_zip():
  args = [
    "-Version", package_version,
    "-Arch", arch
  ]
  # if common.sign:
  #   args += ["-Sign"]

  utils.log_h2("builder zip build")
  ret = utils.ps1("make_zip.ps1", args, verbose=True)
  utils.set_summary("builder zip build", ret)

  if common.deploy and ret:
    utils.log_h2("builder zip deploy")
    ret = s3_upload(utils.glob_path("zip/*.zip"), "builder/win/generic/")
    utils.set_summary("builder zip deploy", ret)
  return

def make_macos_linux():
  utils.set_cwd("document-builder-package")

  make_tar()
  make_wheel()

  utils.set_cwd(common.workspace_dir)
  return

def make_tar():
  utils.log_h2("builder tar build")
  make_args = ["tar"]
  if common.platform == "darwin_arm64":
    make_args += ["-e", "UNAME_M=arm64"]
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../" + common.branding + "/document-builder-package"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("builder tar build", ret)

  if common.deploy:
    utils.log_h2("builder tar deploy")
    if utils.is_macos():
      s3_dest = "builder/mac/generic/"
    elif utils.is_linux():
      s3_dest = "builder/linux/generic/"
    ret = s3_upload(utils.glob_path("tar/*.tar.xz"), s3_dest)
    utils.set_summary("builder tar deploy", ret)
  return

def make_wheel():
  platform_tags = {
    "windows_x64":   "win_amd64",
    "windows_x86":   "win32",
    "darwin_arm64":  "macosx_11_0_arm64",
    "darwin_x86_64": "macosx_10_9_x86_64",
    "linux_x86_64":  "manylinux_2_23_x86_64",
    "linux_aarch64": "manylinux_2_23_aarch64"
  }

  if not common.platform in platform_tags: return

  utils.log_h2("builder python wheel build")

  builder_dir = "build"
  if utils.is_linux():
    builder_dir = "build/opt/onlyoffice/documentbuilder"

  utils.delete_dir("python")
  utils.copy_dir("../onlyoffice/build_tools/packaging/docbuilder/resources", "python")
  utils.copy_dir(builder_dir, "python/docbuilder/lib")

  desktop_dir = "../desktop-apps/macos/build/ONLYOFFICE.app/Contents/Resources/converter"
  if utils.is_macos() and "desktop" in common.targets and utils.is_exist(desktop_dir):
    for f in utils.glob_path(desktop_dir + "/*.dylib") + [desktop_dir + "/x2t"]:
      utils.copy_file(f, builder_dir + "/" + utils.get_basename(f))

  old_cwd = utils.get_cwd()
  utils.set_cwd("python/docbuilder")

  if not utils.is_file("docbuilder.py"):
    utils.copy_file("lib/docbuilder.py", "docbuilder.py")
    # fix docbuilder.py
    content = ""
    with open("docbuilder.py", "r") as file:
      content = file.read()
    old_line = "builder_path = os.path.dirname(os.path.realpath(__file__))"
    new_line = "builder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), \"lib\")"
    content = content.replace(old_line, new_line)
    with open("docbuilder.py", "w") as file:
      file.write(content)

  # remove unnecessary files
  utils.set_cwd("lib")
  utils.delete_dir("include")
  utils.delete_file("build.date")
  utils.delete_file("docbuilder.jar")
  utils.delete_file("docbuilder.py")
  if utils.is_windows():
    utils.delete_file("doctrenderer.lib")
    utils.delete_file("docbuilder.com.dll")
    utils.delete_file("docbuilder.net.dll")
    utils.delete_file("docbuilder.jni.dll")
  elif utils.is_macos():
    utils.delete_file("libdocbuilder.jni.dylib")
  elif utils.is_linux():
    utils.delete_file("libdocbuilder.jni.so")

  utils.set_env("DOCBUILDER_VERSION", common.version + "." + common.build)
  platform = "linux_64"
  utils.set_cwd("../..")
  plat_name = platform_tags[common.platform]
  ret = utils.sh("python setup.py bdist_wheel --plat-name " + plat_name + " --python-tag py2.py3", verbose=True)
  utils.set_summary("builder python wheel build", ret)

  if common.deploy and ret:
    utils.log_h2("builder python wheel deploy")
    if utils.is_windows():
      s3_dest = "builder/win/python/"
    elif utils.is_macos():
      s3_dest = "builder/mac/python/"
    elif utils.is_linux():
      s3_dest = "builder/linux/python/"
    ret = s3_upload(utils.glob_path("dist/*.whl"), s3_dest)
    utils.set_summary("builder python wheel deploy", ret)

  utils.set_cwd(old_cwd)

  return
