#!/usr/bin/env python

import config
import base
import os

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  core_build_dir = core_dir + "/build"
  branding = config.branding()
  if ("" != config.option("branding")):
    core_build_dir += ("/" + config.option("branding"))

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    archive_dir = base_dir + ("/" + native_platform + "/" + branding + "/core")
    if (base.is_dir(archive_dir)):
      base.delete_dir(archive_dir)
    base.create_dir(archive_dir)

    platform = native_platform

    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "doctrenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform, archive_dir, "EpubFile")
    base.copy_exe(core_build_dir + "/bin/" + platform, archive_dir, "x2t")

    base.copy_dir(base_dir + "/js/" + branding + "/builder/sdkjs", archive_dir + "/sdkjs")

    if ("windows" == base.host_platform()):
      base.copy_files(core_dir + "/Common/3dParty/icu/" + platform + "/build/*.dll", archive_dir + "/")
      base.copy_files(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/release/icudt*.dat", archive_dir + "/")
    else:
      base.copy_files(core_dir + "/Common/3dParty/icu/" + platform + "/build/*", archive_dir + "/")
      base.copy_file(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/icudtl.dat", archive_dir + "/")

    base.copy_exe(core_build_dir + "/bin/" + platform, archive_dir, "allfontsgen")
    base.copy_exe(core_build_dir + "/bin/" + platform, archive_dir, "allthemesgen")
    base.copy_exe(core_build_dir + "/bin/" + platform, archive_dir, "standardtester")

    if base.is_file(archive_dir + "/core.7z"):
      base.delete_file(archive_dir + "/core.7z")
    base.archive_folder(archive_dir, archive_dir + "/core.7z")

  return

