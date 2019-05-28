TEMPLATE = subdirs

ROOT_DIR=$$PWD/..
DEPLOY_DIR=$$PWD/deploy
CORE_ROOT_DIR=$$ROOT_DIR/core

include($$CORE_ROOT_DIR/Common/base.pri)
include($$PWD/scripts/common.pri)

MAKEFILE=makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
message(makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX)
build_xp {
	MAKEFILE=$$MAKEFILE_xp
}

CONFIG += ordered

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
	
desktop {
message(desktop)

SUBDIRS += \
	hunspell \
	ooxmlsignature \
	documentscore \
	videoplayer \
	\
	projicons \
	desktopapp	
}

CONFIG += ordered

# PROJECTS
cryptopp.file              = $$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/cryptopp.pro
cryptopp.makefile          = $$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/Makefile.cryptopp$$CORE_BUILDS_PLATFORM_PREFIX

kernel.file                = $$CORE_ROOT_DIR/Common/kernel.pro
kernel.makefile            = $$CORE_ROOT_DIR/Common/Makefile.kernel$$CORE_BUILDS_PLATFORM_PREFIX

unicodeconverter.file      = $$CORE_ROOT_DIR/UnicodeConverter/UnicodeConverter.pro
unicodeconverter.makefile  = $$CORE_ROOT_DIR/UnicodeConverter/Makefile.UnicodeConverter$$CORE_BUILDS_PLATFORM_PREFIX

graphics.file              = $$CORE_ROOT_DIR/DesktopEditor/graphics/pro/graphics.pro
graphics.makefile          = $$CORE_ROOT_DIR/DesktopEditor/graphics/pro/Makefile.graphics$$CORE_BUILDS_PLATFORM_PREFIX

pdfwriter.file             = $$CORE_ROOT_DIR/PdfWriter/PdfWriter.pro
pdfwriter.makefile         = $$CORE_ROOT_DIR/PdfWriter/Makefile.PdfWriter$$CORE_BUILDS_PLATFORM_PREFIX

djvufile.file              = $$CORE_ROOT_DIR/DjVuFile/DjVuFile.pro
djvufile.makefile          = $$CORE_ROOT_DIR/DjVuFile/Makefile.DjVuFile$$CORE_BUILDS_PLATFORM_PREFIX

xpsfile.file               = $$CORE_ROOT_DIR/XpsFile/XpsFile.pro
xpsfile.makefile           = $$CORE_ROOT_DIR/XpsFile/Makefile.XpsFile$$CORE_BUILDS_PLATFORM_PREFIX

htmlrenderer.file          = $$CORE_ROOT_DIR/HtmlRenderer/htmlrenderer.pro
htmlrenderer.makefile      = $$CORE_ROOT_DIR/HtmlRenderer/Makefile.htmlrenderer$$CORE_BUILDS_PLATFORM_PREFIX

pdfreader.file             = $$CORE_ROOT_DIR/PdfReader/PdfReader.pro
pdfreader.makefile         = $$CORE_ROOT_DIR/PdfReader/Makefile.PdfReader$$CORE_BUILDS_PLATFORM_PREFIX

htmlfile.file              = $$CORE_ROOT_DIR/HtmlFile/HtmlFile.pro
htmlfile.makefile          = $$CORE_ROOT_DIR/HtmlFile/Makefile.HtmlFile$$CORE_BUILDS_PLATFORM_PREFIX

doctrenderer.file          = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/doctrenderer.pro
doctrenderer.makefile      = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/Makefile.doctrenderer$$CORE_BUILDS_PLATFORM_PREFIX

htmlfileinternal.file      = $$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Internal.pro
htmlfileinternal.makefile  = $$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Makefile.Internal$$CORE_BUILDS_PLATFORM_PREFIX

allfontsgen.file           = $$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/AllFontsGen.pro
allfontsgen.makefile       = $$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/Makefile.AllFontsGen$$CORE_BUILDS_PLATFORM_PREFIX

docbuilder.file            = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/docbuilder.pro
docbuilder.makefile        = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/Makefile.docbuilder$$CORE_BUILDS_PLATFORM_PREFIX

docxformat.file            = $$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/DocxFormatLib.pro
docxformat.makefile        = $$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/Makefile.DocxFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

pptxformat.file            = $$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/PPTXFormatLib.pro
pptxformat.makefile        = $$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/Makefile.PPTXFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

docxfile.file              = $$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/ASCOfficeDocxFile2Lib.pro
docxfile.makefile          = $$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/Makefile.ASCOfficeDocxFile2Lib$$CORE_BUILDS_PLATFORM_PREFIX

txtxmlformat.file          = $$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/TxtXmlFormatLib.pro
txtxmlformat.makefile      = $$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/Makefile.TxtXmlFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

rtfformat.file             = $$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/RtfFormatLib.pro
rtfformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/Makefile.RtfFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

pptformat.file             = $$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/PPTFormatLib.pro
pptformat.makefile         = $$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/Makefile.PPTFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

docformat.file             = $$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/DocFormatLib.pro
docformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/Makefile.DocFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

odffilereader.file         = $$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/OdfFileReaderLib.pro
odffilereader.makefile     = $$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/Makefile.OdfFileReaderLib$$CORE_BUILDS_PLATFORM_PREFIX

odffilewriter.file         = $$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/OdfFileWriterLib.pro
odffilewriter.makefile     = $$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/Makefile.OdfFileWriterLib$$CORE_BUILDS_PLATFORM_PREFIX

xlsformat.file             = $$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/XlsFormatLib.pro
xlsformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/Makefile.XlsFormatLib$$CORE_BUILDS_PLATFORM_PREFIX

x2t.file                   = $$CORE_ROOT_DIR/X2tConverter/build/Qt/X2tConverter.pro
x2t.makefile               = $$CORE_ROOT_DIR/X2tConverter/build/Qt/Makefile.X2tConverter$$CORE_BUILDS_PLATFORM_PREFIX

desktop {
	hunspell.file            = $$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/hunspell.pro
	hunspell.makefile        = $$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/Makefile.hunspell$$CORE_BUILDS_PLATFORM_PREFIX

	ooxmlsignature.file      = $$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/ooxmlsignature.pro
	ooxmlsignature.makefile  = $$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/Makefile.ooxmlsignature$$CORE_BUILDS_PLATFORM_PREFIX

	documentscore.file       = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/AscDocumentsCore_win.pro
	documentscore.makefile   = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.AscDocumentsCore_win$$CORE_BUILDS_PLATFORM_PREFIX

	videoplayer.file         = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro
	videoplayer.makefile     = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/Makefile.videoplayerlib$$CORE_BUILDS_PLATFORM_PREFIX
	
	projicons.file           = $$ROOT_DIR/desktop-apps/win-linux/extras/projicons/ProjIcons.pro
	projicons.makefile       = $$ROOT_DIR/desktop-apps/win-linux/extras/projicons/Makefile.ProjIcons$$CORE_BUILDS_PLATFORM_PREFIX

	desktopapp.file     	 = $$ROOT_DIR/desktop-apps/win-linux/ASCDocumentEditor.pro
	desktopapp.makefile      = $$ROOT_DIR/desktop-apps/win-linux/Makefile.ASCDocumentEditor$$CORE_BUILDS_PLATFORM_PREFIX
}

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

allfontsgen.depends       = kernel unicodeconverter graphics

docbuilder.depends        = kernel unicodeconverter graphics doctrenderer

desktop {
	ooxmlsignature.depends    = kernel unicodeconverter graphics
	documentscore.depends     = kernel unicodeconverter graphics hunspell ooxmlsignature htmlrenderer pdfwriter pdfreader djvufile xpsfile
	videoplayer.depends       = kernel unicodeconverter graphics
	
	projicons.depends 		  = documentscore videoplayer
	desktopapp.depends        = documentscore videoplayer
}

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