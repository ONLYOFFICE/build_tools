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

    root_dir = base_dir + ("/" + native_platform + "/" + branding + ("/DocumentBuilder" if base.is_windows() else "/documentbuilder"))
    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    qt_dir = base.qt_setup(native_platform)

    # check platform on xp
    isWindowsXP = False if (-1 == native_platform.find("_xp")) else True
    platform = native_platform[0:-3] if isWindowsXP else native_platform

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    # x2t
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "kernel_network")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "PdfFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "EpubFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "DocxRenderer")
    base.copy_file(git_dir + "/sdkjs/pdf/src/engine/cmap.bin", root_dir + "/cmap.bin")

    if ("ios" == platform):
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "x2t")
    else:
      base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir, "x2t")

    #if (native_platform == "linux_64"):
    #  base.generate_check_linux_system(git_dir + "/build_tools", root_dir)

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

    # doctrenderer
    if isWindowsXP:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix + "/xp", root_dir, "doctrenderer")
      base.copy_file(core_build_dir + "/lib/" + platform_postfix + "/xp/doctrenderer.lib", root_dir + "/doctrenderer.lib")
    else:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "doctrenderer")
      if (0 == platform.find("win")):
        base.copy_file(core_build_dir + "/lib/" + platform_postfix + "/doctrenderer.lib", root_dir + "/doctrenderer.lib")
    base.copy_v8_files(core_dir, root_dir, platform, isWindowsXP)
    # python wrapper
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "docbuilder.c")
    base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.python/src/docbuilder.py", root_dir + "/docbuilder.py")
    # java wrapper
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "docbuilder.jni")
    base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.java/build/libs/docbuilder.jar", root_dir + "/docbuilder.jar")

    # app
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir, "docbuilder")
    base.generate_doctrenderer_config(root_dir + "/DoctRenderer.config", "./", "builder", "", "./dictionaries")
    base.copy_dir(git_dir + "/document-templates/new/en-US", root_dir + "/empty")

    # dictionaries
    base.copy_dictionaries(git_dir + "/dictionaries", root_dir + "/dictionaries", True, False)

    # js
    base.copy_dir(base_dir + "/js/" + branding + "/builder/sdkjs", root_dir + "/sdkjs")
    base.create_dir(root_dir + "/sdkjs/vendor")
    base.copy_dir(base_dir + "/js/" + branding + "/builder/web-apps/vendor/jquery", root_dir + "/sdkjs/vendor/jquery")
    base.copy_dir(base_dir + "/js/" + branding + "/builder/web-apps/vendor/xregexp", root_dir + "/sdkjs/vendor/xregexp")

    # include
    base.create_dir(root_dir + "/include")
    base.copy_file(core_dir + "/DesktopEditor/doctrenderer/common_deploy.h", root_dir + "/include/common.h")
    base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.h", root_dir + "/include/docbuilder.h")
    if (0 == platform.find("win")):
      base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.com/src/docbuilder_midl.h", root_dir + "/include/docbuilder_midl.h")
    base.replaceInFile(root_dir + "/include/docbuilder.h", "Q_DECL_EXPORT", "BUILDING_DOCBUILDER")
    
    if ("win_64" == platform):
      base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.com/deploy/win_64/docbuilder.com.dll", root_dir + "/docbuilder.com.dll")
      base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.net/deploy/win_64/docbuilder.net.dll", root_dir + "/docbuilder.net.dll")
      
    elif ("win_32" == platform):
      base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.com/deploy/win_32/docbuilder.com.dll", root_dir + "/docbuilder.com.dll")
      base.copy_file(core_dir + "/DesktopEditor/doctrenderer/docbuilder.net/deploy/win_32/docbuilder.net.dll", root_dir + "/docbuilder.net.dll")

    # correct ios frameworks
    if ("ios" == platform):
      base.generate_plist(root_dir)

    if (0 == platform.find("linux")):
      base.linux_correct_rpath_docbuilder(root_dir)

    if (0 == platform.find("mac")):
      base.mac_correct_rpath_x2t(root_dir)
      base.mac_correct_rpath_docbuilder(root_dir)

    base.create_x2t_js_cache(root_dir, "builder")
  
  return

