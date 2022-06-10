#!/usr/bin/env python

import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  if utils.is_windows():
    make_windows()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported builder on host OS")
  return

def make_windows():
  utils.set_cwd("document-builder-package")

  if common.clean:
    utils.log_h1("clean")
    utils.delete_dir("build")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.builder_product_name.replace(" ","").lower()
  source_dir = "%s\\build_tools\\out\\%s\\%s\\%s" % (workspace_dir, prefix, company, product)

  utils.log_h1("copy arifacts")
  utils.create_dir("build\\base")
  utils.copy_dir_content(source_dir, "build\\base\\")

  global innosetup_file, portable_zip_file

  # if "builder-portable" in common.targets:
  #   portable_zip_file = "build/zip/%s_%s_%s.zip" % (package_name, package_version, suffix)
  #   make_portable()

  if "builder-innosetup" in common.targets:
    package_name = "onlyoffice_documentbuilder"
    package_version = common.version + "." + common.build
    suffix = "x64"
    innosetup_file = "build\\exe\\%s_%s_%s.exe" % (package_name, package_version, suffix)
    make_innosetup()

  return

# def make_macos():
#   return

# def make_linux():
#   set_cwd(build_dir)
#   log("Clean")
#   cmd("make", ["clean"])
#   log("Build packages")
#   cmd("make", ["packages"])
#   return

def make_innosetup():
  common.summary["innosetup build"] = 1
  if not common.deploy:
    common.summary["innosetup deploy"] = 1

  utils.log_h1("innosetup build")

  # if utils.is_file(innosetup_file):
  #   utils.log("! file exist, skip")
  #   return

  branding_path = "%s\\%s\\document-builder-package\\exe" % (common.workspace_dir, common.branding)
  args = ["-Version " + common.version, "-Build " + common.build]
  if not onlyoffice:
    args.append("-Branding '%s'" % branding_path)
  if sign:
    args.append("-Sign")
    args.append("-CertName '%s'" % cert_name)

  utils.log(innosetup_file)
  ret = utils.run_ps1("exe\\make.ps1", args, verbose=True)
  common.summary["innosetup build"] = ret

  utils.log_h1("innosetup deploy")
  # ret = s3_copy(innosetup_file,
  #   "s3://repo-doc-onlyoffice-com/onlyoffice/experimental/windows/builder/%s/%s/" % (version, build))
  ret = 1
  common.summary["innosetup deploy"] = ret
  return

# def make_win_portable():
#   log("\n=== Build portable\n")
#   log("--- " + portable_zip_file)
#   if is_file(portable_zip_file):
#     log("! file exist, skip")
#     return
#   cmd("7z", ["a", "-y", portable_zip_file, get_path(base_dir, "*")])
#   return
