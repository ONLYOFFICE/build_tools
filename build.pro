TEMPLATE = subdirs

ROOT_DIR=$$PWD/..
DEPLOY_DIR=$$PWD/deploy
CORE_ROOT_DIR=$$ROOT_DIR/core

include($$PWD/common.pri)

CONFIG += ordered

core_windows {
	desktop:CONFIG += core_and_multimedia
}
core_linux {
	desktop:CONFIG += core_and_multimedia
}
core_mac {
	CONFIG += no_desktop_apps
}
core_ios {
	CONFIG += no_use_common_binary
	CONFIG += no_desktop_apps
	CONFIG += no_tests
}
core_android {
	CONFIG += no_use_common_binary
	CONFIG += no_desktop_apps
	CONFIG += no_tests
}

addSubProject(cryptopp,		$$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/cryptopp.pro)
addSubProject(unicodeconverter,	$$CORE_ROOT_DIR/UnicodeConverter/UnicodeConverter.pro,\
				cryptopp)
addSubProject(kernel,		$$CORE_ROOT_DIR/Common/kernel.pro,\
				unicodeconverter)
addSubProject(network,	$$CORE_ROOT_DIR/Common/Network/network.pro,\
				kernel unicodeconverter)
addSubProject(graphics,		$$CORE_ROOT_DIR/DesktopEditor/graphics/pro/graphics.pro,\
				kernel unicodeconverter)
addSubProject(pdffile,	$$CORE_ROOT_DIR/PdfFile/PdfFile.pro,\
				kernel unicodeconverter graphics)
addSubProject(djvufile,		$$CORE_ROOT_DIR/DjVuFile/DjVuFile.pro,\
				kernel unicodeconverter graphics pdffile)
addSubProject(xpsfile,		$$CORE_ROOT_DIR/XpsFile/XpsFile.pro,\
				kernel unicodeconverter graphics pdffile)
addSubProject(htmlrenderer,	$$CORE_ROOT_DIR/HtmlRenderer/htmlrenderer.pro,\
				kernel unicodeconverter graphics)
addSubProject(docxrenderer,	$$CORE_ROOT_DIR/DocxRenderer/DocxRenderer.pro,\
				kernel unicodeconverter graphics)
addSubProject(htmlfile2,	$$CORE_ROOT_DIR/HtmlFile2/HtmlFile2.pro,\
				kernel unicodeconverter graphics network)
addSubProject(doctrenderer,	$$CORE_ROOT_DIR/DesktopEditor/doctrenderer/doctrenderer.pro,\
				kernel unicodeconverter graphics)
addSubProject(fb2file,		$$CORE_ROOT_DIR/Fb2File/Fb2File.pro,\
				kernel unicodeconverter graphics)
addSubProject(epubfile,		$$CORE_ROOT_DIR/EpubFile/CEpubFile.pro,\
				kernel unicodeconverter graphics htmlfile2)
!no_x2t {
	addSubProject(docxformat,   $$CORE_ROOT_DIR/OOXML/Projects/Linux/DocxFormatLib/DocxFormatLib.pro)
	addSubProject(pptxformat,   $$CORE_ROOT_DIR/OOXML/Projects/Linux/PPTXFormatLib/PPTXFormatLib.pro)
	addSubProject(xlsbformat,   $$CORE_ROOT_DIR/OOXML/Projects/Linux/XlsbFormatLib/XlsbFormatLib.pro)

	addSubProject(docformat,    $$CORE_ROOT_DIR/MsBinaryFile/Projects/DocFormatLib/Linux/DocFormatLib.pro)
	addSubProject(pptformat,    $$CORE_ROOT_DIR/MsBinaryFile/Projects/PPTFormatLib/Linux/PPTFormatLib.pro)
	addSubProject(xlsformat,    $$CORE_ROOT_DIR/MsBinaryFile/Projects/XlsFormatLib/Linux/XlsFormatLib.pro)
	addSubProject(vbaformat,    $$CORE_ROOT_DIR/MsBinaryFile/Projects/VbaFormatLib/Linux/VbaFormatLib.pro)

	addSubProject(txtxmlformat, $$CORE_ROOT_DIR/TxtFile/Projects/Linux/TxtXmlFormatLib.pro)
	addSubProject(rtfformat,    $$CORE_ROOT_DIR/RtfFile/Projects/Linux/RtfFormatLib.pro)
	addSubProject(odffile,      $$CORE_ROOT_DIR/OdfFile/Projects/Linux/OdfFormatLib.pro)
	
	addSubProject(cfcpp,        $$CORE_ROOT_DIR/Common/cfcpp/cfcpp.pro)
	addSubProject(bindocument,  $$CORE_ROOT_DIR/OOXML/Projects/Linux/BinDocument/BinDocument.pro)

	addSubProject(x2t,          $$CORE_ROOT_DIR/X2tConverter/build/Qt/X2tConverter.pro,\
					docxformat pptxformat xlsbformat docformat pptformat xlsformat vbaformat txtxmlformat rtfformat odffile cfcpp bindocument fb2file epubfile docxrenderer)
}

!no_use_common_binary {
	addSubProject(allfontsgen,	$$CORE_ROOT_DIR/DesktopEditor/AllFontsGen/AllFontsGen.pro,\
					kernel unicodeconverter graphics)
	addSubProject(allthemesgen,	$$CORE_ROOT_DIR/DesktopEditor/allthemesgen/allthemesgen.pro,\
					kernel unicodeconverter graphics)
	addSubProject(docbuilder,	$$CORE_ROOT_DIR/DesktopEditor/doctrenderer/app_builder/docbuilder.pro,\
					kernel unicodeconverter graphics doctrenderer)
}

!no_tests {
	addSubProject(standardtester,	$$CORE_ROOT_DIR/Test/Applications/StandardTester/standardtester.pro)
	addSubProject(x2ttester,	$$CORE_ROOT_DIR/Test/Applications/x2tTester/x2ttester.pro)

	#TODO:
	!linux_arm64:addSubProject(ooxml_crypt,	$$CORE_ROOT_DIR/OfficeCryptReader/ooxml_crypt/ooxml_crypt.pro)
}

core_and_multimedia {
	addSubProject(videoplayer,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro,\
					kernel unicodeconverter graphics)
}
desktop {
	message(desktop)
	addSubProject(hunspell,		$$CORE_ROOT_DIR/Common/3dParty/hunspell/qt/hunspell.pro)
	addSubProject(ooxmlsignature,	$$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/ooxmlsignature.pro,\
					kernel unicodeconverter graphics)
	addSubProject(documentscore,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore.pro,\
					kernel unicodeconverter graphics hunspell ooxmlsignature htmlrenderer pdffile djvufile xpsfile)
	addSubProject(documentscore_helper,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore_helper.pro,\
					documentscore)
	!core_mac {
		addSubProject(qtdocumentscore,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/qt_wrapper/qtascdocumentscore.pro,\
						documentscore)
	}

	!no_desktop_apps {
		core_windows:addSubProject(projicons,	$$ROOT_DIR/desktop-apps/win-linux/extras/projicons/ProjIcons.pro,\
							documentscore videoplayer)
		addSubProject(desktopapp,	$$ROOT_DIR/desktop-apps/win-linux/ASCDocumentEditor.pro,\
						documentscore videoplayer)
	}
}

mobile {
	message(mobile)
	!desktop {
		addSubProject(hunspell,		$$CORE_ROOT_DIR/Common/3dParty/hunspell/qt/hunspell.pro)
	}
}
