#!/usr/bin/env python

import config
import base
import os
import platform

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  branding = config.branding()

  platforms = config.option("platform").split()
  for native_platform in platforms:
    if not native_platform in config.platforms:
      continue

    root_dir = base_dir + ("/" + native_platform + "/" + branding + ("/DesktopEditors" if base.is_windows() else "/desktopeditors"))
    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    qt_dir = base.qt_setup(native_platform)

    # check platform on xp
    isWindowsXP = False if (-1 == native_platform.find("_xp")) else True
    platform = native_platform[0:-3] if isWindowsXP else native_platform

    apps_postfix = "build" + base.qt_dst_postfix();
    if ("" != config.option("branding")):
      apps_postfix += ("/" + config.option("branding"))
    apps_postfix += "/"
    apps_postfix += platform
    if isWindowsXP:
      apps_postfix += "/xp"

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    # x2t
    base.create_dir(root_dir + "/converter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "kernel_network")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "EpubFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "DocxRenderer")

    if ("ios" == platform):
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "x2t")
    else:
      base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir + "/converter", "x2t")

    # icu
    if (0 == platform.find("win")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icudt58.dll", root_dir + "/converter/icudt58.dll")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/icuuc58.dll", root_dir + "/converter/icuuc58.dll")

    if (0 == platform.find("linux")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.so.58", root_dir + "/converter/libicudata.so.58")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.so.58", root_dir + "/converter/libicuuc.so.58")

    if (0 == platform.find("mac")):
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicudata.58.dylib", root_dir + "/converter/libicudata.58.dylib")
      base.copy_file(core_dir + "/Common/3dParty/icu/" + platform + "/build/libicuuc.58.dylib", root_dir + "/converter/libicuuc.58.dylib")

    # doctrenderer
    if isWindowsXP:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix + "/xp", root_dir + "/converter", "doctrenderer")
    else:
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir + "/converter", "doctrenderer")      
    base.copy_v8_files(core_dir, root_dir + "/converter", platform, isWindowsXP)

    base.generate_doctrenderer_config(root_dir + "/converter/DoctRenderer.config", "../editors/", "desktop")
    base.copy_dir(git_dir + "/document-templates/new", root_dir + "/converter/empty")

    # dictionaries
    base.create_dir(root_dir + "/dictionaries")
    base.copy_dir_content(git_dir + "/dictionaries", root_dir + "/dictionaries", "", ".git")

    base.copy_dir(git_dir + "/desktop-apps/common/package/fonts", root_dir + "/fonts")
    base.copy_file(git_dir + "/desktop-apps/common/package/license/3dparty/3DPARTYLICENSE", root_dir + "/3DPARTYLICENSE")
  
    # cef
    if not isWindowsXP:
      base.copy_files(core_dir + "/Common/3dParty/cef/" + platform + "/build/*", root_dir)
    else:
      base.copy_files(core_dir + "/Common/3dParty/cef/" + native_platform + "/build/*", root_dir)

    isUseQt = True
    if (0 == platform.find("mac")) or (0 == platform.find("ios")):
      isUseQt = False

    # libraries
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, root_dir, "hunspell")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix + ("/xp" if isWindowsXP else ""), root_dir, "ooxmlsignature")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix + ("/xp" if isWindowsXP else ""), root_dir, "ascdocumentscore")
    if (0 != platform.find("mac")):
      base.copy_lib(core_build_dir + "/lib/" + platform_postfix + ("/xp" if isWindowsXP else ""), root_dir, "qtascdocumentscore")
    
    if (0 == platform.find("mac")):
      base.copy_dir(core_build_dir + "/bin/" + platform_postfix + "/editors_helper.app", root_dir + "/editors_helper.app")
    else:
      base.copy_exe(core_build_dir + "/bin/" + platform_postfix + ("/xp" if isWindowsXP else ""), root_dir, "editors_helper")
    
    if isUseQt:
      base.qt_copy_lib("Qt5Core", root_dir)
      base.qt_copy_lib("Qt5Gui", root_dir)
      base.qt_copy_lib("Qt5PrintSupport", root_dir)
      base.qt_copy_lib("Qt5Svg", root_dir)
      base.qt_copy_lib("Qt5Widgets", root_dir)
      base.qt_copy_lib("Qt5Multimedia", root_dir)
      base.qt_copy_lib("Qt5MultimediaWidgets", root_dir)
      base.qt_copy_lib("Qt5Network", root_dir)
      base.qt_copy_lib("Qt5OpenGL", root_dir)

      base.qt_copy_plugin("bearer", root_dir)
      base.qt_copy_plugin("iconengines", root_dir)
      base.qt_copy_plugin("imageformats", root_dir)
      base.qt_copy_plugin("platforms", root_dir)
      base.qt_copy_plugin("platforminputcontexts", root_dir)
      base.qt_copy_plugin("printsupport", root_dir)
      base.qt_copy_plugin("mediaservice", root_dir)
      base.qt_copy_plugin("playlistformats", root_dir)

      base.qt_copy_plugin("platformthemes", root_dir)
      base.qt_copy_plugin("xcbglintegrations", root_dir)

      base.qt_copy_plugin("styles", root_dir)

      if (0 == platform.find("linux")):
        base.qt_copy_lib("Qt5DBus", root_dir)
        base.qt_copy_lib("Qt5X11Extras", root_dir)
        base.qt_copy_lib("Qt5XcbQpa", root_dir)
        base.qt_copy_icu(root_dir)
        base.copy_files(base.get_env("QT_DEPLOY") + "/../lib/libqgsttools_p.so*", root_dir)

      if (0 == platform.find("win")):
        base.copy_file(git_dir + "/desktop-apps/win-linux/extras/projicons/" + apps_postfix + "/projicons.exe", root_dir + "/DesktopEditors.exe")
        base.copy_file(git_dir + "/desktop-apps/win-linux/" + apps_postfix + "/DesktopEditors.exe", root_dir + "/editors.exe")
        base.copy_file(git_dir + "/desktop-apps/win-linux/res/icons/desktopeditors.ico", root_dir + "/app.ico")
      elif (0 == platform.find("linux")):
        base.copy_file(git_dir + "/desktop-apps/win-linux/" + apps_postfix + "/DesktopEditors", root_dir + "/DesktopEditors")

      base.copy_lib(core_build_dir + "/lib/" + platform_postfix + ("/xp" if isWindowsXP else ""), root_dir, "videoplayer")

    base.create_dir(root_dir + "/editors")
    base.copy_dir(base_dir + "/js/" + branding + "/desktop/sdkjs", root_dir + "/editors/sdkjs")
    base.copy_dir(base_dir + "/js/" + branding + "/desktop/web-apps", root_dir + "/editors/web-apps")
    base.copy_dir(git_dir + "/desktop-sdk/ChromiumBasedEditors/resources/local", root_dir + "/editors/sdkjs/common/Images/local")

    base.create_dir(root_dir + "/editors/sdkjs-plugins")
    base.copy_sdkjs_plugins(root_dir + "/editors/sdkjs-plugins", True, True)
    # remove some default plugins
    if base.is_dir(root_dir + "/editors/sdkjs-plugins/speech"):
      base.delete_dir(root_dir + "/editors/sdkjs-plugins/speech")

    # io
    base.create_dir(root_dir + "/editors/sdkjs-plugins/v1")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js", root_dir + "/editors/sdkjs-plugins/v1/plugins.js")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins-ui.js", root_dir + "/editors/sdkjs-plugins/v1/plugins-ui.js")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.css", root_dir + "/editors/sdkjs-plugins/v1/plugins.css")
    base.support_old_versions_plugins(root_dir + "/editors/sdkjs-plugins")

    base.copy_sdkjs_plugin(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins", root_dir + "/editors/sdkjs-plugins", "manager", True)
    base.copy_sdkjs_plugin(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins/encrypt", root_dir + "/editors/sdkjs-plugins", "advanced2", True)
    #base.copy_dir(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/common/{14A8FC87-8E26-4216-B34E-F27F053B2EC4}", root_dir + "/editors/sdkjs-plugins/{14A8FC87-8E26-4216-B34E-F27F053B2EC4}")
    #base.copy_dir(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/engine/database/{9AB4BBA8-A7E5-48D5-B683-ECE76A020BB1}", root_dir + "/editors/sdkjs-plugins/{9AB4BBA8-A7E5-48D5-B683-ECE76A020BB1}")
    base.copy_sdkjs_plugin(git_dir + "/desktop-sdk/ChromiumBasedEditors/plugins", root_dir + "/editors/sdkjs-plugins", "sendto", True)

    base.copy_file(base_dir + "/js/" + branding + "/desktop/index.html", root_dir + "/index.html")
    base.copy_dir(git_dir + "/desktop-apps/common/loginpage/providers", root_dir + "/providers")

    isUseJSC = False
    if (0 == platform.find("mac")):
      file_size_doctrenderer = os.path.getsize(root_dir + "/converter/libdoctrenderer.dylib")
      print("file_size_doctrenderer: " + str(file_size_doctrenderer))
      if (file_size_doctrenderer < 5*1024*1024):
        isUseJSC = True

    if isUseJSC:
      base.delete_file(root_dir + "/converter/icudtl.dat")

    if (0 == platform.find("win")):
      base.copy_lib(git_dir + "/desktop-apps/win-linux/3dparty/WinSparkle/" + platform, root_dir, "WinSparkle")
      base.delete_file(root_dir + "/cef_sandbox.lib")
      base.delete_file(root_dir + "/libcef.lib")

    isMacArmPlaformOnIntel = False
    if (platform == "mac_arm64") and not base.is_os_arm():
      isMacArmPlaformOnIntel = True

    # all themes generate ----
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir + "/converter", "allfontsgen")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, root_dir + "/converter", "allthemesgen")

    if (0 == platform.find("mac")):
      base.mac_correct_rpath_desktop(root_dir)

    if isMacArmPlaformOnIntel:
      sdkjs_dir = root_dir + "/editors/sdkjs"
      end_find_platform = sdkjs_dir.rfind("/mac_arm64/")
      sdkjs_dir_mac64 = sdkjs_dir[0:end_find_platform] + "/mac_64/" + sdkjs_dir[end_find_platform+11:]
      base.delete_dir(sdkjs_dir)
      base.copy_dir(sdkjs_dir_mac64, sdkjs_dir)
    else:
      themes_params = []
      if ("" != config.option("themesparams")):
        themes_params = ["--params=\"" + config.option("themesparams") + "\""]
      base.cmd_exe(root_dir + "/converter/allfontsgen", ["--use-system=\"1\"", "--input=\"" + root_dir + "/fonts\"", "--input=\"" + git_dir + "/core-fonts\"", "--allfonts=\"" + root_dir + "/converter/AllFonts.js\"", "--selection=\"" + root_dir + "/converter/font_selection.bin\""])
      base.cmd_exe(root_dir + "/converter/allthemesgen", ["--converter-dir=\"" + root_dir + "/converter\"", "--src=\"" + root_dir + "/editors/sdkjs/slide/themes\"", "--allfonts=\"AllFonts.js\"", "--output=\"" + root_dir + "/editors/sdkjs/common/Images\""] + themes_params)
      base.delete_file(root_dir + "/converter/AllFonts.js")
      base.delete_file(root_dir + "/converter/font_selection.bin")
      base.delete_file(root_dir + "/converter/fonts.log")

    base.delete_exe(root_dir + "/converter/allfontsgen")
    base.delete_exe(root_dir + "/converter/allthemesgen")

    if not isUseJSC:
      base.delete_file(root_dir + "/editors/sdkjs/slide/sdk-all.cache")

  return

