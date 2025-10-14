#!/usr/bin/env python

import config
import base

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  branding = config.branding()

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    root_dir = base_dir + "/" + native_platform + "/" + branding + "/osign"

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
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "osign")

    # correct ios frameworks
    if ("ios" == platform):
      base.for_each_framework(root_dir, "ios", callbacks=[base.generate_plist, base.generate_xcprivacy])

  for native_platform in platforms:
    if native_platform == "android":
      # make full version
      root_dir = base_dir + "/android/" + branding + "/osign"
      if (base.is_dir(root_dir)):
        base.delete_dir(root_dir)
      base.create_dir(root_dir)
      libs_dir = root_dir + "/lib"
      base.create_dir(libs_dir + "/arm64-v8a")
      base.copy_files(base_dir + "/android_arm64_v8a/" + branding + "/osign/*.so", libs_dir + "/arm64-v8a")
      base.create_dir(libs_dir + "/armeabi-v7a")
      base.copy_files(base_dir + "/android_armv7/" + branding + "/osign/*.so", libs_dir + "/armeabi-v7a")
      base.create_dir(libs_dir + "/x86")
      base.copy_files(base_dir + "/android_x86/" + branding + "/osign/*.so", libs_dir + "/x86")
      base.create_dir(libs_dir + "/x86_64")
      base.copy_files(base_dir + "/android_x86_64/" + branding + "/osign/*.so", libs_dir + "/x86_64")
      break

  return
