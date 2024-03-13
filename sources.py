#!/usr/bin/env python

import config
import base

solution = {
  "core" : {
    "all" : [
      "core/Common/3dParty/cryptopp/project/cryptopp.pro",

      "core/Common/cfcpp/cfcpp.pro",

      "core/UnicodeConverter/UnicodeConverter.pro",
      "core/Common/kernel.pro",
      "core/Common/Network/network.pro",

      "core/DesktopEditor/graphics/pro/graphics.pro",

      "core/PdfFile/PdfFile.pro",
      "core/DjVuFile/DjVuFile.pro",
      "core/XpsFile/XpsFile.pro",

      "core/HtmlRenderer/htmlrenderer.pro",
      "core/DocxRenderer/DocxRenderer.pro",

      "core/HtmlFile2/HtmlFile2.pro",
      "core/Fb2File/Fb2File.pro",
      "core/EpubFile/CEpubFile.pro",

      "core/DesktopEditor/doctrenderer/doctrenderer.pro"
    ],
    "x2t" : [
      "core/OOXML/Projects/Linux/DocxFormatLib/DocxFormatLib.pro",
      "core/OOXML/Projects/Linux/PPTXFormatLib/PPTXFormatLib.pro",
      "core/OOXML/Projects/Linux/XlsbFormatLib/XlsbFormatLib.pro",

      "core/MsBinaryFile/Projects/DocFormatLib/Linux/DocFormatLib.pro",
      "core/MsBinaryFile/Projects/PPTFormatLib/Linux/PPTFormatLib.pro",
      "core/MsBinaryFile/Projects/XlsFormatLib/Linux/XlsFormatLib.pro",
      "core/MsBinaryFile/Projects/VbaFormatLib/Linux/VbaFormatLib.pro",

      "core/TxtFile/Projects/Linux/TxtXmlFormatLib.pro",
      "core/RtfFile/Projects/Linux/RtfFormatLib.pro",
      "core/OdfFile/Projects/Linux/OdfFormatLib.pro",

      "core/OOXML/Projects/Linux/BinDocument/BinDocument.pro",

      "core/X2tConverter/build/Qt/X2tConverter.pro"
    ],
    "utilities" : [
      "core/DesktopEditor/AllFontsGen/AllFontsGen.pro",
      "core/DesktopEditor/allthemesgen/allthemesgen.pro",

      "core/DesktopEditor/doctrenderer/app_builder/docbuilder.pro",

      "core/DesktopEditor/pluginsmanager/pluginsmanager.pro"
    ],
    "utilities_no_linux_arm64" : [
      "core/OfficeCryptReader/ooxml_crypt/ooxml_crypt.pro"
    ],
    "tests" : [
      "core/DesktopEditor/vboxtester/vboxtester.pro",
      "core/Test/Applications/StandardTester/standardtester.pro",
      "core/Test/Applications/x2tTester/x2ttester.pro",
      "core/Test/Applications/MetafileTester/MetafileTester.pro"
    ]
  },
  "multimedia" : {
    "all" : [
      "desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro"
    ]
  },
  "spell" : {
    "all" : [
      "core/Common/3dParty/hunspell/qt/hunspell.pro"
    ]
  },
  "desktop" : {
    "all" : [
      "core/DesktopEditor/xmlsec/src/ooxmlsignature.pro",

      "desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore.pro",
      "desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore_helper.pro"
    ],
    "qt" : [
      "desktop-sdk/ChromiumBasedEditors/lib/qt_wrapper/qtascdocumentscore.pro"
      "desktop-apps/win-linux/ASCDocumentEditor.pro"
    ],
    "qt_win" : [
      "desktop-apps/desktop-apps/win-linux/extras/projicons/ProjIcons.pro"
    ],
    "qt_win_update" : [
      "desktop-apps/desktop-apps/win-linux/extras/update-daemon/UpdateDaemon.pro"
    ]
  },
  "osign" : [
    "core/DesktopEditor/xmlsec/src/osign/lib/osign.pro"
  ]
}

# find name option in value
def check_configure(name, value):
  tmp = " " + value + " "
  if (-1 == tmp.find(" " + name + " ")):
    return False
  return True

def check_configure_array(names, value):
  for item in names:
    if check_configure(item, value):
      return True
  return False

def get_projects(platform):
  configure = base.qt_config(platform)
  projects = []

  is_mobile_platform = False
  if (0 == platform.find("ios")) or (0 == platform.find("android")):
    is_mobile_platform = True

  is_desktop = check_configure("desktop", configure)
  if (is_mobile_platform):
    is_desktop = False

  if check_configure_array(["core", "builder", "desktop", "server", "mobile"], configure):
    is_core = True
    projects += solution["core"]["all"]
    if not check_configure("no_x2t", configure):
      projects += solution["core"]["x2t"]
    if not is_mobile_platform:
      projects += solution["core"]["utilities"]
      if (platform != "linux_arm64"):
        projects += solution["core"]["utilities_no_linux_arm64"]

  if check_configure_array(["mobile", "desktop"], configure):
    projects += solution["spell"]["all"]

  if is_desktop:
    projects += solution["desktop"]["all"]
    if (0 == platform.find("win")) or (0 == platform.find("linux")):
      projects += solution["multimedia"]["all"]
      projects += solution["desktop"]["qt"]
    if (0 == platform.find("win")):
      projects += solution["desktop"]["qt_win"]
      if (-1 == platform.find("_xp")):
        projects += solution["desktop"]["qt_win_update"]

  if check_configure_array(["osign"], configure):
    projects += solution["osign"]

  return projects
