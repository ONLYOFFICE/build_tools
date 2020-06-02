TEMPLATE = subdirs

ROOT_DIR=$$PWD/..
DEPLOY_DIR=$$PWD/deploy
CORE_ROOT_DIR=$$ROOT_DIR/core

include($$CORE_ROOT_DIR/Common/base.pri)

MAKEFILE=makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
PRO_SUFFIX=$$CORE_BUILDS_PLATFORM_PREFIX

core_debug {
	MAKEFILE=$$join(MAKEFILE, MAKEFILE, "", "_debug_")
	PRO_SUFFIX=$$join(PRO_SUFFIX, PRO_SUFFIX, "", "_debug_")
}
build_xp {
	MAKEFILE=$$join(MAKEFILE, MAKEFILE, "", "_xp")
	PRO_SUFFIX=$$join(PRO_SUFFIX, PRO_SUFFIX, "", "_xp")
}
OO_BRANDING_SUFFIX = $$(OO_BRANDING)
!isEmpty(OO_BRANDING_SUFFIX) {
	PRO_SUFFIX=$$join(PRO_SUFFIX, PRO_SUFFIX, "", "$$OO_BRANDING_SUFFIX")
	MAKEFILE=$$join(MAKEFILE, MAKEFILE, "", "$$OO_BRANDING_SUFFIX")
}

CONFIG += ordered

core_windows {
	CONFIG += core_and_multimedia
}
core_linux {
	linux-g++:contains(QMAKE_HOST.arch, ppc64le): {
		CONFIG += no_use_htmlfileinternal
		CONFIG += no_desktop_apps
	}
	else {
		CONFIG += core_and_multimedia
	}
}
core_mac {
	CONFIG += no_use_htmlfileinternal
	CONFIG += no_desktop_apps
}
build_xp {
	CONFIG += no_use_htmlfileinternal
}
core_ios {
	CONFIG += no_use_htmlfileinternal
	CONFIG += no_use_common_binary
	CONFIG += no_desktop_apps
}
core_android {
	CONFIG += no_use_htmlfileinternal
	CONFIG += no_use_common_binary
	CONFIG += no_desktop_apps
}

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
	doctrenderer

!no_x2t {
SUBDIRS += \
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
}

!no_use_htmlfileinternal {
	SUBDIRS += htmlfileinternal
}

!no_use_common_binary {
	SUBDIRS += \
		allfontsgen \
		allthemesgen \
		docbuilder
}

core_ios:CONFIG += no_tests
core_android:CONFIG += no_tests
!no_tests {
	SUBDIRS += standardtester
}

core_and_multimedia {
SUBDIRS += \
	videoplayer
}
	
desktop {
message(desktop)

SUBDIRS += \
	hunspell \
	ooxmlsignature \
	documentscore \
	documentscore_helper

!core_mac {
SUBDIRS += qtdocumentscore
}

!no_desktop_apps {
core_windows:SUBDIRS += projicons
SUBDIRS += desktopapp
}

}

ordered {
	# remove all makefiles

	defineTest(removeFile) {
		file = $$1			
		win32:file ~= s,/,\\,g
		core_windows {
			system(if exist $$shell_quote($$file) $$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
		} else {
			system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
		}	
	}

	removeFile($$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/Makefile.cryptopp$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/Common/Makefile.kernel$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/UnicodeConverter/Makefile.UnicodeConverter$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DesktopEditor/graphics/pro/Makefile.graphics$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/PdfWriter/Makefile.PdfWriter$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DjVuFile/Makefile.DjVuFile$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/XpsFile/Makefile.XpsFile$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/HtmlRenderer/Makefile.htmlrenderer$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/PdfReader/Makefile.PdfReader$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/HtmlFile/Makefile.HtmlFile$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DesktopEditor/doctrenderer/Makefile.doctrenderer$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Makefile.Internal$$PRO_SUFFIX)

	removeFile($$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/Makefile.AllFontsGen$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DesktopEditor/allthemesgen/Makefile.allthemesgen$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/Makefile.docbuilder$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/Test/Applications/StandardTester/Makefile.standardtester$$PRO_SUFFIX)

	removeFile($$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/Makefile.DocxFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/Makefile.PPTXFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/Makefile.ASCOfficeDocxFile2Lib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/Makefile.TxtXmlFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/Makefile.RtfFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/Makefile.PPTFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/Makefile.DocFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/Makefile.OdfFileReaderLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/Makefile.OdfFileWriterLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/Makefile.XlsFormatLib$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/X2tConverter/build/Qt/Makefile.X2tConverter$$PRO_SUFFIX)

	removeFile($$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/Makefile.hunspell$$PRO_SUFFIX)
	removeFile($$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/Makefile.ooxmlsignature$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.ascdocumentscore$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.ascdocumentscore_helper$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/qt_wrapper/Makefile.qtascdocumentscore$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/Makefile.videoplayerlib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-apps/win-linux/extras/projicons/Makefile.ProjIcons$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-apps/win-linux/Makefile.ASCDocumentEditor$$PRO_SUFFIX)
}

# PROJECTS
cryptopp.file              = $$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/cryptopp.pro
cryptopp.makefile          = $$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/Makefile.cryptopp$$PRO_SUFFIX

kernel.file                = $$CORE_ROOT_DIR/Common/kernel.pro
kernel.makefile            = $$CORE_ROOT_DIR/Common/Makefile.kernel$$PRO_SUFFIX

unicodeconverter.file      = $$CORE_ROOT_DIR/UnicodeConverter/UnicodeConverter.pro
unicodeconverter.makefile  = $$CORE_ROOT_DIR/UnicodeConverter/Makefile.UnicodeConverter$$PRO_SUFFIX

graphics.file              = $$CORE_ROOT_DIR/DesktopEditor/graphics/pro/graphics.pro
graphics.makefile          = $$CORE_ROOT_DIR/DesktopEditor/graphics/pro/Makefile.graphics$$PRO_SUFFIX

pdfwriter.file             = $$CORE_ROOT_DIR/PdfWriter/PdfWriter.pro
pdfwriter.makefile         = $$CORE_ROOT_DIR/PdfWriter/Makefile.PdfWriter$$PRO_SUFFIX

djvufile.file              = $$CORE_ROOT_DIR/DjVuFile/DjVuFile.pro
djvufile.makefile          = $$CORE_ROOT_DIR/DjVuFile/Makefile.DjVuFile$$PRO_SUFFIX

xpsfile.file               = $$CORE_ROOT_DIR/XpsFile/XpsFile.pro
xpsfile.makefile           = $$CORE_ROOT_DIR/XpsFile/Makefile.XpsFile$$PRO_SUFFIX

htmlrenderer.file          = $$CORE_ROOT_DIR/HtmlRenderer/htmlrenderer.pro
htmlrenderer.makefile      = $$CORE_ROOT_DIR/HtmlRenderer/Makefile.htmlrenderer$$PRO_SUFFIX

pdfreader.file             = $$CORE_ROOT_DIR/PdfReader/PdfReader.pro
pdfreader.makefile         = $$CORE_ROOT_DIR/PdfReader/Makefile.PdfReader$$PRO_SUFFIX

htmlfile.file              = $$CORE_ROOT_DIR/HtmlFile/HtmlFile.pro
htmlfile.makefile          = $$CORE_ROOT_DIR/HtmlFile/Makefile.HtmlFile$$PRO_SUFFIX

doctrenderer.file          = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/doctrenderer.pro
doctrenderer.makefile      = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/Makefile.doctrenderer$$PRO_SUFFIX

!no_use_htmlfileinternal {
	htmlfileinternal.file      = $$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Internal.pro
	htmlfileinternal.makefile  = $$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Makefile.Internal$$PRO_SUFFIX
}

!no_use_common_binary {
	allfontsgen.file           = $$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/AllFontsGen.pro
	allfontsgen.makefile       = $$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/Makefile.AllFontsGen$$PRO_SUFFIX

	allthemesgen.file           = $$CORE_ROOT_DIR/DesktopEditor/allthemesgen/allthemesgen.pro
	allthemesgen.makefile       = $$CORE_ROOT_DIR/DesktopEditor/allthemesgen/Makefile.allthemesgen$$PRO_SUFFIX

	docbuilder.file            = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/docbuilder.pro
	docbuilder.makefile        = $$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/Makefile.docbuilder$$PRO_SUFFIX
}

!no_tests {
	standardtester.file        = $$CORE_ROOT_DIR/Test/Applications/StandardTester/standardtester.pro
	standardtester.makefile    = $$CORE_ROOT_DIR/Test/Applications/StandardTester/Makefile.standardtester$$PRO_SUFFIX
}

!no_x2t {
	docxformat.file            = $$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/DocxFormatLib.pro
	docxformat.makefile        = $$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/Makefile.DocxFormatLib$$PRO_SUFFIX

	pptxformat.file            = $$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/PPTXFormatLib.pro
	pptxformat.makefile        = $$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/Makefile.PPTXFormatLib$$PRO_SUFFIX

	docxfile.file              = $$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/ASCOfficeDocxFile2Lib.pro
	docxfile.makefile          = $$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/Makefile.ASCOfficeDocxFile2Lib$$PRO_SUFFIX

	txtxmlformat.file          = $$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/TxtXmlFormatLib.pro
	txtxmlformat.makefile      = $$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/Makefile.TxtXmlFormatLib$$PRO_SUFFIX

	rtfformat.file             = $$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/RtfFormatLib.pro
	rtfformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/Makefile.RtfFormatLib$$PRO_SUFFIX

	pptformat.file             = $$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/PPTFormatLib.pro
	pptformat.makefile         = $$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/Makefile.PPTFormatLib$$PRO_SUFFIX

	docformat.file             = $$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/DocFormatLib.pro
	docformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/Makefile.DocFormatLib$$PRO_SUFFIX

	odffilereader.file         = $$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/OdfFileReaderLib.pro
	odffilereader.makefile     = $$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/Makefile.OdfFileReaderLib$$PRO_SUFFIX

	odffilewriter.file         = $$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/OdfFileWriterLib.pro
	odffilewriter.makefile     = $$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/Makefile.OdfFileWriterLib$$PRO_SUFFIX

	xlsformat.file             = $$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/XlsFormatLib.pro
	xlsformat.makefile         = $$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/Makefile.XlsFormatLib$$PRO_SUFFIX

	x2t.file                   = $$CORE_ROOT_DIR/X2tConverter/build/Qt/X2tConverter.pro
	x2t.makefile               = $$CORE_ROOT_DIR/X2tConverter/build/Qt/Makefile.X2tConverter$$PRO_SUFFIX
}

desktop {
	hunspell.file            = $$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/hunspell.pro
	hunspell.makefile        = $$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/Makefile.hunspell$$PRO_SUFFIX

	ooxmlsignature.file      = $$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/ooxmlsignature.pro
	ooxmlsignature.makefile  = $$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/Makefile.ooxmlsignature$$PRO_SUFFIX

	documentscore.file          = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore.pro
	documentscore.makefile     	= $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.ascdocumentscore$$PRO_SUFFIX

	documentscore_helper.file     = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore_helper.pro
	documentscore_helper.makefile = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.ascdocumentscore_helper$$PRO_SUFFIX

	!core_mac {
		qtdocumentscore.file     = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/qt_wrapper/qtascdocumentscore.pro
		qtdocumentscore.makefile = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/qt_wrapper/Makefile.qtascdocumentscore$$PRO_SUFFIX
	}
	
	!no_desktop_apps {
		core_windows {
			projicons.file           = $$ROOT_DIR/desktop-apps/win-linux/extras/projicons/ProjIcons.pro
			projicons.makefile       = $$ROOT_DIR/desktop-apps/win-linux/extras/projicons/Makefile.ProjIcons$$PRO_SUFFIX
		}
		desktopapp.file     	 = $$ROOT_DIR/desktop-apps/win-linux/ASCDocumentEditor.pro
		desktopapp.makefile      = $$ROOT_DIR/desktop-apps/win-linux/Makefile.ASCDocumentEditor$$PRO_SUFFIX
	}
}

core_and_multimedia {
	videoplayer.file         = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro
	videoplayer.makefile     = $$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/Makefile.videoplayerlib$$PRO_SUFFIX
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

!no_use_htmlfileinternal {
	htmlfileinternal.depends  = kernel unicodeconverter graphics
}

!no_use_common_binary {
	allfontsgen.depends       = kernel unicodeconverter graphics
	allthemesgen.depends       = kernel unicodeconverter graphics

	docbuilder.depends        = kernel unicodeconverter graphics doctrenderer
}

core_and_multimedia {
	videoplayer.depends       		= kernel unicodeconverter graphics
}

desktop {
	ooxmlsignature.depends    = kernel unicodeconverter graphics
	documentscore.depends     = kernel unicodeconverter graphics hunspell ooxmlsignature htmlrenderer pdfwriter pdfreader djvufile xpsfile
	documentscore_helper.depends    = documentscore	

	!core_mac {
		qtdocumentscore.depends 	= documentscore
	}
	
	!no_desktop_apps {
		core_windows:projicons.depends  = documentscore videoplayer
		desktopapp.depends              = documentscore videoplayer
	}
}

!no_x2t {
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
}
