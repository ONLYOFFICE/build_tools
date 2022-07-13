#!/usr/bin/env python

import config
import base

import re
import shutil
from tempfile import mkstemp

def make():
  base_dir = base.get_script_dir() + "/../out"
  git_dir = base.get_script_dir() + "/../.."
  core_dir = git_dir + "/core"
  plugins_dir = git_dir + "/sdkjs-plugins"
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
    root_dir_snap = root_dir + '-snap/var/www/onlyoffice/documentserver'
    root_dir_snap_example = root_dir_snap + '-example'
    if (base.is_dir(root_dir)):
      base.delete_dir(root_dir)
    base.create_dir(root_dir)

    build_server_dir = root_dir + '/server'
    server_dir = base.get_script_dir() + "/../../server"
    bin_server_dir = server_dir + "/build/server"

    base.create_dir(build_server_dir + '/DocService')

    base.copy_dir(bin_server_dir + '/Common/config', build_server_dir + '/Common/config')

    base.create_dir(build_server_dir + '/DocService')
    base.copy_exe(bin_server_dir + "/DocService", build_server_dir + '/DocService', "docservice")

    base.create_dir(build_server_dir + '/FileConverter')
    base.copy_exe(bin_server_dir + "/FileConverter", build_server_dir + '/FileConverter', "converter")

    base.create_dir(build_server_dir + '/Metrics')
    base.copy_exe(bin_server_dir + "/Metrics", build_server_dir + '/Metrics', "metrics")
    base.copy_dir(bin_server_dir + '/Metrics/config', build_server_dir + '/Metrics/config')
    base.create_dir(build_server_dir + '/Metrics/node_modules/modern-syslog/build/Release')
    base.copy_file(bin_server_dir + "/Metrics/node_modules/modern-syslog/build/Release/core.node", build_server_dir + "/Metrics/node_modules/modern-syslog/build/Release/core.node")


    qt_dir = base.qt_setup(native_platform)
    platform = native_platform

    core_build_dir = core_dir + "/build"
    if ("" != config.option("branding")):
      core_build_dir += ("/" + config.option("branding"))

    platform_postfix = platform + base.qt_dst_postfix()

    converter_dir = root_dir + "/server/FileConverter/bin"
    base.create_dir(converter_dir)

    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "kernel")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "kernel_network")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "UnicodeConverter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "graphics")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfWriter")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "PdfReader")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "DjVuFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "XpsFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlFile2")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "HtmlRenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "doctrenderer")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "Fb2File")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "EpubFile")
    base.copy_lib(core_build_dir + "/lib/" + platform_postfix, converter_dir, "DocxRenderer")
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
    
    base.copy_v8_files(core_dir, converter_dir, platform)

    # builder
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, converter_dir, "docbuilder")
    base.copy_dir(git_dir + "/DocumentBuilder/empty", converter_dir + "/empty")

    # js
    js_dir = root_dir
    base.copy_dir(base_dir + "/js/" + branding + "/builder/sdkjs", js_dir + "/sdkjs")
    base.copy_dir(base_dir + "/js/" + branding + "/builder/web-apps", js_dir + "/web-apps")
    
    # plugins
    base.create_dir(js_dir + "/sdkjs-plugins")
    base.copy_sdkjs_plugins(js_dir + "/sdkjs-plugins", False, True)
    base.copy_sdkjs_plugins_server(js_dir + "/sdkjs-plugins", False, True)
    base.create_dir(js_dir + "/sdkjs-plugins/v1")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js", js_dir + "/sdkjs-plugins/v1/plugins.js")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins-ui.js", js_dir + "/sdkjs-plugins/v1/plugins-ui.js")
    base.download("https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.css", js_dir + "/sdkjs-plugins/v1/plugins.css")
    base.support_old_versions_plugins(js_dir + "/sdkjs-plugins")
    
    # tools
    tools_dir = root_dir + "/server/tools"
    base.create_dir(tools_dir)
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allfontsgen")
    base.copy_exe(core_build_dir + "/bin/" + platform_postfix, tools_dir, "allthemesgen")

    branding_dir = server_dir + "/branding"
    if("" != config.option("branding") and "onlyoffice" != config.option("branding")):
      branding_dir = git_dir + '/' + config.option("branding") + '/server'

    #dictionaries
    spellchecker_dictionaries = root_dir + '/dictionaries'
    spellchecker_dictionaries_files = server_dir + '/../dictionaries/*_*'
    base.create_dir(spellchecker_dictionaries)
    base.copy_files(spellchecker_dictionaries_files, spellchecker_dictionaries)

    if (0 == platform.find("win")):
      exec_ext = '.exe'
    else:
      exec_ext = ''

    #schema
    schema_files = server_dir + '/schema'
    schema = build_server_dir + '/schema'
    base.create_dir(schema)
    base.copy_dir(schema_files, schema)

    #core-fonts
    core_fonts_files = server_dir + '/../core-fonts'
    core_fonts = build_server_dir + '/../core-fonts'
    base.create_dir(core_fonts)
    base.copy_dir_content(core_fonts_files, core_fonts, "", ".git")

    #document-templates
    document_templates_files = server_dir + '/../document-templates'
    document_templates = build_server_dir + '/../document-templates'
    base.create_dir(document_templates)
    base.copy_dir_content(document_templates_files, document_templates, "", ".git")

    #license
    license_file1 = server_dir + '/LICENSE.txt'
    license_file2 = server_dir + '/3rd-Party.txt'
    license_dir = server_dir + '/license'
    license = build_server_dir + '/license'
    base.copy_file(license_file1, build_server_dir)
    base.copy_file(license_file2, build_server_dir)
    base.copy_dir(license_dir, license)

    #branding
    welcome_files = branding_dir + '/welcome'
    welcome = build_server_dir + '/welcome'
    base.create_dir(welcome)
    base.copy_dir(welcome_files, welcome)

    info_files = branding_dir + '/info'
    info = build_server_dir + '/info'
    base.create_dir(info)
    base.copy_dir(info_files, info)

    # example
    build_example_dir = root_dir + '-example'
    bin_example_dir = base.get_script_dir() + "/../../document-server-integration/web/documentserver-example/nodejs"

    base.create_dir(build_example_dir)
    base.copy_exe(bin_example_dir, build_example_dir, "example")
    base.copy_dir(bin_example_dir + "/config", build_example_dir + "/config")

    # snap
    if (0 == platform.find("linux")):
      if (base.is_dir(root_dir_snap)):
        base.delete_dir(root_dir_snap)
      base.create_dir(root_dir_snap)
      base.copy_dir(root_dir, root_dir_snap)
      base.copy_dir(bin_server_dir + '/DocService/node_modules', root_dir_snap + '/server/DocService/node_modules')
      base.copy_dir(bin_server_dir + '/DocService/sources', root_dir_snap + '/server/DocService/sources')
      base.copy_dir(bin_server_dir + '/DocService/public', root_dir_snap + '/server/DocService/public')
      base.delete_file(root_dir_snap + '/server/DocService/docservice')
      base.copy_dir(bin_server_dir + '/FileConverter/node_modules', root_dir_snap + '/server/FileConverter/node_modules')
      base.copy_dir(bin_server_dir + '/FileConverter/sources', root_dir_snap + '/server/FileConverter/sources')
      base.delete_file(root_dir_snap + '/server/FileConverter/converter')
      base.copy_dir(bin_server_dir + '/Common/node_modules', root_dir_snap + '/server/Common/node_modules')
      base.copy_dir(bin_server_dir + '/Common/sources', root_dir_snap + '/server/Common/sources')
      if (base.is_dir(root_dir_snap_example)):
        base.delete_dir(root_dir_snap_example)
      base.create_dir(root_dir_snap_example)
      base.copy_dir(bin_example_dir + '/..', root_dir_snap_example)
      base.delete_file(root_dir_snap + '/example/nodejs/example')

  return

