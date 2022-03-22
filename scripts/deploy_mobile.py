#!/usr/bin/env python

import config
import base

def exclude_arch(directory, frameworks):
  for lib in frameworks:
    base.cmd("lipo", ["-remove", "arm64", directory + "/" + lib + ".framework/" + lib, "-o", directory + "/" + lib + ".framework/" + lib])
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
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "doctrenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "EpubFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DocxRenderer")

    if (0 == platform.find("win") or 0 == platform.find("linux") or 0 == platform.find("mac")):
      base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir, "x2t")
    else:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "x2t")

    if ("ios" == platform) and config.check_option("config", "bundle_dylibs") and config.check_option("config", "simulator"):
      exclude_arch(root_dir, ["kernel", "kernel_network", "UnicodeConverter", "graphics", "PdfWriter", 
        "PdfReader", "DjVuFile", "XpsFile", "HtmlFile2", "HtmlRenderer", "doctrenderer",
        "Fb2File", "EpubFile", "x2t"])


    # icu
    if (0 == platform.find("win")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icudt58.dll", root_dir + "/icudt58.dll")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icuuc58.dll", root_dir + "/icuuc58.dll")

    if (0 == platform.find("linux")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.so.58", root_dir + "/libicudata.so.58")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.so.58", root_dir + "/libicuuc.so.58")

    if (0 == platform.find("mac")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.58.dylib", root_dir + "/libicudata.58.dylib")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.58.dylib", root_dir + "/libicuuc.58.dylib")
    
    if (0 == platform.find("android")):
      #base.copy_file(core_dir + "/Common/3dParty/icu/android/build/" + platform[8:] + "/libicudata.so", root_dir + "/libicudata.so")
      #base.copy_file(core_dir + "/Common/3dParty/icu/android/build/" + platform[8:] + "/libicuuc.so", root_dir + "/libicuuc.so")
      base.copy_file(core_dir + "/Common/3dParty/icu/android/build/" + platform[8:] + "/icudt58l.dat", root_dir + "/icudt58l.dat")

    # js
    base.copy_dir(base_dir + "/js/" + branding + "/mobile/sdkjs", root_dir + "/sdkjs")

    # correct ios frameworks
    if ("ios" == platform):
      base.generate_plist(root_dir)

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
      # app
      base.generate_doctrenderer_config(root_dir + "/DoctRenderer.config", "./", "builder")      
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
