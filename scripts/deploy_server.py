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

    if (-1 != native_platform.find("_xp")):
      print("Server module not supported on Windows XP")
      continue

    if (-1 != native_platform.find("ios")):
      print("Server module not supported on iOS")
      continue

    if (-1 != native_platform.find("android")):
      print("Server module not supported on Android")
      continue

    root_dir = base_dir + ("/" + native_platform + "/" + branding + "/documentserver")
    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    qt_dir = base.qt_setup(native_platform)
    platform = native_platform

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    converter_dir = root_dir + "/server/FileConverter/bin"
    base.create_dir(converter_dir)

    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "doctrenderer")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, converter_dir, "x2t")

    base.generate_doctrenderer_config(converter_dir + "/DoctRenderer.config", "../../../", "server")

    # icu
    if (0 == platform.find("win")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icudt58.dll", converter_dir + "/icudt58.dll")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icuuc58.dll", converter_dir + "/icuuc58.dll")

    if (0 == platform.find("linux")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.so.58", converter_dir + "/libicudata.so.58")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.so.58", converter_dir + "/libicuuc.so.58")

    if (0 == platform.find("mac")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.58.dylib", converter_dir + "/libicudata.58.dylib")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.58.dylib", converter_dir + "/libicuuc.58.dylib")

    if (0 == platform.find("win")):
      base.copy_files(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/release/icudt*.dat", converter_dir + "/")
    else:
      base.copy_file(core_dir + "/Common/3dParty/v8/v8/out.gn/" + platform + "/icudtl.dat", converter_dir + "/icudtl.dat")

    # builder
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, converter_dir, "docbuilder")
    base.copy_dir(git_dir + "/DocumentBuilder/empty", converter_dir + "/empty")

    # html
    base.create_dir(converter_dir + "/HtmlFileInternal")
    base.copy_exe(core_build_dir + "/lib/" + platform_postfix, converter_dir + "/HtmlFileInternal", "HtmlFileInternal")
    base.copy_files(core_dir + "/Common/3dParty/cef/" + platform + "/build/*", converter_dir + "/HtmlFileInternal")
    if (0 == platform.find("win")):
      base.delete_file(root_dir + "/HtmlFileInternal/cef_sandbox.lib")
      base.delete_file(root_dir + "/HtmlFileInternal/libcef.lib")

    # js
    js_dir = root_dir
    base.copy_dir(base_dir + "/js/" + branding + "/builder/sdkjs", js_dir + "/sdkjs")
    base.copy_dir(base_dir + "/js/" + branding + "/builder/web-apps", js_dir + "/web-apps")
    
    # tools
    tools_dir = root_dir + "/server/tools"
    base.create_dir(tools_dir)
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allfontsgen")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allthemesgen")
    
  return

