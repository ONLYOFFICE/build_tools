sys.path.append('scripts')
import config
import base

# remove all makefiles
def clean():
  suff = config.platforms[:]
  suff_branding = config.option("branding")
  if "" != suff_branding:
    suff2 = []
    for cur in suff:
      suff2.append(cur + suff_branding)
    suff += suff2
  core_dir = base.get_script_dir() + "/../"
  for cur in suff
    base.delete_file(core_dir + "/core/Common/3dParty/cryptopp/project/Makefile.cryptopp" + cur)
    base.delete_file(core_dir + "/core/Common/Makefile.kernel" + cur)
    base.delete_file(core_dir + "/core/UnicodeConverter/Makefile.UnicodeConverter" + cur)
    base.delete_file(core_dir + "/core/DesktopEditor/graphics/pro/Makefile.graphics" + cur)
    base.delete_file(core_dir + "/core/PdfWriter/Makefile.PdfWriter" + cur)
    base.delete_file(core_dir + "/core/DjVuFile/Makefile.DjVuFile" + cur)
    base.delete_file(core_dir + "/core/XpsFile/Makefile.XpsFile" + cur)
    base.delete_file(core_dir + "/core/HtmlRenderer/Makefile.htmlrenderer" + cur)
    base.delete_file(core_dir + "/core/PdfReader/Makefile.PdfReader" + cur)
    base.delete_file(core_dir + "/core/HtmlFile/Makefile.HtmlFile" + cur)
    base.delete_file(core_dir + "/core/DesktopEditor/doctrenderer/Makefile.doctrenderer" + cur)
    base.delete_file(core_dir + "/desktop-sdk/HtmlFile/Internal/Makefile.Internal" + cur)

    base.delete_file(core_dir + "/core/DesktopEditor/AllFontsGen/Makefile.AllFontsGen" + cur)  
    base.delete_file(core_dir + "/core/DesktopEditor/doctrenderer/app_builder/Makefile.docbuilder" + cur)

    base.delete_file(core_dir + "/core/Common/DocxFormat/DocxFormatLib/Makefile.DocxFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/Makefile.PPTXFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeDocxFile2/Linux/Makefile.ASCOfficeDocxFile2Lib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/Makefile.TxtXmlFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeRtfFile/RtfFormatLib/Linux/Makefile.RtfFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficePPTFile/PPTFormatLib/Linux/Makefile.PPTFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeDocFile/DocFormatLib/Linux/Makefile.DocFormatLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeOdfFile/linux/Makefile.OdfFileReaderLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeOdfFileW/linux/Makefile.OdfFileWriterLib" + cur)
    base.delete_file(core_dir + "/core/ASCOfficeXlsFile2/source/linux/Makefile.XlsFormatLib" + cur)
    base.delete_file(core_dir + "/core/X2tConverter/build/Qt/Makefile.X2tConverter" + cur)

    base.delete_file(core_dir + "/core/DesktopEditor/hunspell-1.3.3/src/qt/Makefile.hunspell" + cur)
    base.delete_file(core_dir + "/core/DesktopEditor/xmlsec/src/Makefile.ooxmlsignature" + cur)
    base.delete_file(core_dir + "/desktop-sdk/ChromiumBasedEditors/lib/Makefile.AscDocumentsCore_win" + cur)
    base.delete_file(core_dir + "/desktop-sdk/ChromiumBasedEditors/lib/Makefile.AscDocumentsCore_linux" + cur)
    base.delete_file(core_dir + "/desktop-sdk/ChromiumBasedEditors/videoplayerlib/Makefile.videoplayerlib" + cur)
    base.delete_file(core_dir + "/desktop-apps/win-linux/extras/projicons/Makefile.ProjIcons" + cur)
    base.delete_file(core_dir + "/desktop-apps/win-linux/Makefile.ASCDocumentEditor" + cur)

# make build.pro
def make():
  base_dir = base.get_script_dir()
  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue
    is_platform_32 = False
    if (-1 != platform.find("_32"))
      is_platform_32 = True

    platform_base = platform
    suff = platform + config.option("branding")

    if ("1" == config.option("clean")):
      base.cmd("make", ["clean", "all", "-f", base_dir + "/makefiles/build.makefile_" + suff])
      base.cmd("make", ["distclean", "-f", base_dir + "/makefiles/build.makefile_" + suff])

    clean()

    qt_dir = config.option("qt-dir")
    if (-1 != platform.find("xp")):
      qt-dir = config.option("qt-dir-xp")

    if is_platform_32:
      qt_dir += ("/" + config.options["compiler"])
    else:
      qt_dir += ("/" + config.options["compiler_64"])
 
    config_param = config.option("module") + " " + config.option("config")
    if (-1 != platform.find("xp")):
      config_param += " build_xp"

    base.cmd(qt_dir + "/bin/qmake", ["-nocache", "build.pro", "CONFIG+=" + config_param])
    make_app = "make"
    if (0 == platform.find("win")):
      make_app = "nmake"

    base.set_env("QT_DEPLOY", qt_dir + "/bin")
    base.set_env("OS_DEPLOY", platform_base)

    base.cmd(make_app, ["-f", "makefiles/build.makefile_" + platform])
    base.remove_file(base_dir + ".qmake.stash")

  return

# JS build
def _run_npm( directory ):
  dir = base.get_path(directory)
  return base.cmd("npm", ["--prefix", dir, "install", dir])

def _run_grunt( directory, params=[] ):
  dir = base.get_path(directory)
  return base.cmd("grunt", ["--base", dir] + params)

def build_interface( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--force"])
  return

def build_sdk_desktop( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--level=ADVANCED", "--desktop=true"])
  return

def build_sdk_builder( directory ):
  _run_npm(directory)
  _run_grunt(directory, ["--level=ADVANCED"])
  return