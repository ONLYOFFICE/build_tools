#!/usr/bin/env python

import config
import base

def exclude_arch(directory, frameworks):
  for lib in frameworks:
    base.cmd("lipo", ["-remove", "arm64", directory + "/" + lib + ".framework/" + lib, "-o", directory + "/" + lib + ".framework/" + lib])
  return

def deploy_fonts(git_dir, root_dir, platform=""):
  base.create_dir(root_dir + "/fonts")
  base.copy_file(git_dir + "/core-fonts/ASC.ttf", root_dir + "/fonts/ASC.ttf")
  base.copy_dir(git_dir + "/core-fonts/asana", root_dir + "/fonts/asana")
  base.copy_dir(git_dir + "/core-fonts/caladea", root_dir + "/fonts/caladea")
  base.copy_dir(git_dir + "/core-fonts/crosextra", root_dir + "/fonts/crosextra")
  base.copy_dir(git_dir + "/core-fonts/openoffice", root_dir + "/fonts/openoffice")
  if (platform == "android"):
    base.copy_dir(git_dir + "/core-fonts/dejavu", root_dir + "/fonts/dejavu")
    base.copy_dir(git_dir + "/core-fonts/liberation", root_dir + "/fonts/liberation")
  return

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  branding = config.branding()

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    root_dir = base_dir + "/" + native_platform + "/" + branding + "/mobile"

    if base.get_env("DESTDIR_BUILD_OVERRIDE") != "":
      return

    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    qt_dir = base.qt_setup(native_platform)
    platform = native_platform

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    # x2t
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "kernel_network")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "PdfFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "OFDFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "doctrenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "EpubFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "IWorkFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HWPFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DocxRenderer")
    base.copy_file(git_dir + "/sdkjs/pdf/src/engine/cmap.bin", root_dir + "/cmap.bin")

    if (0 == platform.find("win") or 0 == platform.find("linux") or 0 == platform.find("mac")):
      base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir, "x2t")
    else:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "x2t")

    # icu
    base.deploy_icu(core_dir, root_dir, platform)

    # js
    base.copy_dir(base_dir + "/js/" + branding + "/mobile/sdkjs", root_dir + "/sdkjs")

    # correct ios frameworks
    if ("ios" == platform):
      base.for_each_framework(root_dir, "ios", callbacks=[base.generate_plist, base.generate_xcprivacy])
      deploy_fonts(git_dir, root_dir)
      base.copy_dictionaries(git_dir + "/dictionaries", root_dir + "/dictionaries", True, False)

    if (0 == platform.find("mac")):
      base.mac_correct_rpath_x2t(root_dir)

  for native_platform in platforms:
    if native_platform == "android":
      # make full version
      root_dir = base_dir + "/android/" + branding + "/mobile"
      if (base.is_dir(root_dir)):
        base.delete_dir(root_dir)
      base.create_dir(root_dir)
      # js
      base.copy_dir(base_dir + "/js/" + branding + "/mobile/sdkjs", root_dir + "/sdkjs")
      # fonts
      deploy_fonts(git_dir, root_dir, "android")
      base.copy_dictionaries(git_dir + "/dictionaries", root_dir + "/dictionaries", True, False)
      # app
      base.generate_doctrenderer_config(root_dir + "/DoctRenderer.config", "./", "builder", "", "./dictionaries")
      libs_dir = root_dir + "/lib"
      base.create_dir(libs_dir + "/arm64-v8a")
      base.copy_files(base_dir + "/android_arm64_v8a/" + branding + "/mobile/*.so", libs_dir + "/arm64-v8a")
      base.copy_files(base_dir + "/android_arm64_v8a/" + branding + "/mobile/*.so.*", libs_dir + "/arm64-v8a")
      base.copy_files(base_dir + "/android_arm64_v8a/" + branding + "/mobile/*.dat", libs_dir + "/arm64-v8a")
      base.create_dir(libs_dir + "/armeabi-v7a")
      base.copy_files(base_dir + "/android_armv7/" + branding + "/mobile/*.so", libs_dir + "/armeabi-v7a")
      base.copy_files(base_dir + "/android_armv7/" + branding + "/mobile/*.so.*", libs_dir + "/armeabi-v7a")
      base.copy_files(base_dir + "/android_armv7/" + branding + "/mobile/*.dat", libs_dir + "/armeabi-v7a")
      base.create_dir(libs_dir + "/x86")
      base.copy_files(base_dir + "/android_x86/" + branding + "/mobile/*.so", libs_dir + "/x86")
      base.copy_files(base_dir + "/android_x86/" + branding + "/mobile/*.so.*", libs_dir + "/x86")
      base.copy_files(base_dir + "/android_x86/" + branding + "/mobile/*.dat", libs_dir + "/x86")
      base.create_dir(libs_dir + "/x86_64")
      base.copy_files(base_dir + "/android_x86_64/" + branding + "/mobile/*.so", libs_dir + "/x86_64")
      base.copy_files(base_dir + "/android_x86_64/" + branding + "/mobile/*.so.*", libs_dir + "/x86_64")
      base.copy_files(base_dir + "/android_x86_64/" + branding + "/mobile/*.dat", libs_dir + "/x86_64")
      break

  return
