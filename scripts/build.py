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