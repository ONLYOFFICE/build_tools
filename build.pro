TEMPLATE = subdirs

ROOT_DIR=$$PWD/..
DEPLOY_DIR=$$PWD/deploy
CORE_ROOT_DIR=$$ROOT_DIR/core

MAKEFILE=makefiles/build.makefile

include($$CORE_ROOT_DIR/Common/base.pri)

SUBDIRS = \
	cryptopp \
	\
    kernel \
	unicodeconverter \
	graphics \
	pdfwriter \
	djvufile \
	xpsfile \
	htmlrenderer \
	pdfreader \
	htmlfile \
	doctrenderer \
	\
	htmlfileinternal \
	\
	hunspell \
	ooxmlsignature \
	documentscore \
	videoplayer \
	\
	allfontsgen \
	\
	docbuilder \
	\
	docxformat \
    pptxformat \
    docxfile \
    txtxmlformat \
    rtfformat \
    pptformat \
    docformat \
    odffilereader \
    odffilewriter \
    xlsformat \
    x2t

CONFIG += ordered

# PROJECTS
cryptopp.file           = $$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/cryptopp.pro
kernel.file             = $$CORE_ROOT_DIR/Common/kernel.pro
unicodeconverter.file   = $$CORE_ROOT_DIR/UnicodeConverter/UnicodeConverter.pro
graphics.file           = $$CORE_ROOT_DIR/DesktopEditor/graphics/pro/graphics.pro
pdfwriter.file          = $$CORE_ROOT_DIR/PdfWriter/PdfWriter.pro
djvufile.file           = $$CORE_ROOT_DIR/DjVuFile/DjVuFile.pro
xpsfile.file            = $$CORE_ROOT_DIR/XpsFile/XpsFile.pro
htmlrenderer.file       = $$CORE_ROOT_DIR/HtmlRenderer/htmlrenderer.pro
pdfreader.file          = $$CORE_ROOT_DIR/PdfReader/PdfReader.pro
htmlfile.file           = $$CORE_ROOT_DIR/HtmlFile/HtmlFile.pro
doctrenderer.file       = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/doctrenderer.pro

htmlfileinternal.file   = $$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Internal.pro

hunspell.file           = $$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/hunspell.pro
ooxmlsignature.file     = $$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/ooxmlsignature.pro
documentscore.file      = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/AscDocumentsCore_win.pro
videoplayer.file        = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro

allfontsgen.file        = $$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/AllFontsGen.pro

docbuilder.file         = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/docbuilder.pro

docxformat.file         = $$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/DocxFormatLib.pro
pptxformat.file         = $$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/PPTXFormatLib.pro
docxfile.file           = $$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/ASCOfficeDocxFile2Lib.pro
txtxmlformat.file       = $$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/TxtXmlFormatLib.pro
rtfformat.file          = $$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/RtfFormatLib.pro
pptformat.file          = $$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/PPTFormatLib.pro
docformat.file          = $$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/DocFormatLib.pro
odffilereader.file      = $$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/OdfFileReaderLib.pro
odffilewriter.file      = $$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/OdfFileWriterLib.pro
xlsformat.file          = $$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/XlsFormatLib.pro
x2t.file                = $$CORE_ROOT_DIR/X2tConverter/build/Qt/X2tConverter.pro

# DEPENDS
kernel.depends            = cryptopp
graphics.depends          = kernel unicodeconverter
pdfwriter.depends         = kernel unicodeconverter graphics
djvufile.depends          = kernel unicodeconverter graphics pdfwriter
xpsfile.depends           = kernel unicodeconverter graphics pdfwriter
htmlrenderer.depends      = kernel unicodeconverter graphics pdfwriter
pdfreader.depends         = kernel unicodeconverter graphics pdfwriter htmlrenderer
htmlfile.depends          = kernel unicodeconverter graphics
doctrenderer.depends      = kernel unicodeconverter graphics

htmlfileinternal.depends  = kernel unicodeconverter graphics

ooxmlsignature.depends    = kernel unicodeconverter graphics
documentscore.depends     = kernel unicodeconverter graphics hunspell ooxmlsignature htmlrenderer pdfwriter pdfreader djvufile xpsfile
videoplayer.depends       = kernel unicodeconverter graphics

allfontsgen.depends       = kernel unicodeconverter graphics

docbuilder.depends        = kernel unicodeconverter graphics doctrenderer

x2t.depends = \
    docxformat \
    pptxformat \
    docxfile \
    txtxmlformat \
    rtfformat \
    pptformat \
    docformat \
    odffilereader \
    odffilewriter \
    xlsformat
	
target_deploy.target = deploy
target_deploy.commands = scripts/deploy.bat

target_install.target = install
target_install.commands = scripts/install.bat

QMAKE_EXTRA_TARGETS += target_deploy
QMAKE_EXTRA_TARGETS += target_install

#POST_TARGETDEPS += target_deploy
#POST_TARGETDEPS += target_install