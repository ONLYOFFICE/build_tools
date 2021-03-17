TEMPLATE = subdirs

ROOT_DIR=$$PWD/..
DEPLOY_DIR=$$PWD/deploy
CORE_ROOT_DIR=$$ROOT_DIR/core

include($$CORE_ROOT_DIR/Common/base.pri)

MAKEFILE=makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
PRO_SUFFIX=$$CORE_BUILDS_PLATFORM_PREFIX

core_debug {
	MAKEFILE=$$join(MAKEFILE, , , "_debug_")
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "_debug_")
}
build_xp {
	MAKEFILE=$$join(MAKEFILE, , , "_xp")
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "_xp")
}
OO_BRANDING_SUFFIX = $$(OO_BRANDING)
!isEmpty(OO_BRANDING_SUFFIX) {
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "$$OO_BRANDING_SUFFIX")
	MAKEFILE=$$join(MAKEFILE, , , "$$OO_BRANDING_SUFFIX")
}

CONFIG += ordered

core_windows {
	CONFIG += core_and_multimedia
}
core_linux {
	CONFIG += core_and_multimedia
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

defineTest(removeFile) {
	file = $$1	
	win32:file ~= s,/,\\,g
	core_windows {
		system(if exist $$shell_quote($$file) $$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	}
}
defineTest(qmakeClear) {
	dir = $$1
	name = $$2
	removeFile($$1/Makefile.$$2$$PRO_SUFFIX)
	removeFile($$1/.qmake.stash)
}

# addSubProject() - adds project to SUBDIRS, creates variables associated with the project(file, makefile, depends)
# Arg1 - Project name
# Arg2 - Qmake file of project
# Arg3(optional) - Project dependencies
defineTest(addSubProject) {
	pro_name = $$1
	pro_file = $$2
	pro_depends = $$3
	isEmpty(pro_name):error(Sub-project name is not defined.)
	isEmpty(pro_file):error(Qmake file of sub-project \'$$pro_name\' is not defined.)
	!exists($$pro_file):error(Sub-project qmake file \'$$pro_file\' is not exists.)
	path = $$section(pro_file, /, 0, -2)
	ext_name = $$section(pro_file, /, -1, -1)
	name = $$section(ext_name, ., 0, 0)
	SUBDIRS += $$pro_name
	export(SUBDIRS)
	$${pro_name}.file = $$pro_file
	export($${pro_name}.file)
	$${pro_name}.makefile = $$path/Makefile.$$name$$PRO_SUFFIX
	export($${pro_name}.makefile)
	!isEmpty(pro_depends) {
		$${pro_name}.depends = $$pro_depends
		export($${pro_name}.depends)
	}
	# remove makefile
	qmakeClear(path, name)
}

addSubProject(cryptopp,		$$CORE_ROOT_DIR/Common/3dParty/cryptopp/project/cryptopp.pro)
addSubProject(kernel,		$$CORE_ROOT_DIR/Common/kernel.pro,\
				cryptopp)
addSubProject(unicodeconverter,	$$CORE_ROOT_DIR/UnicodeConverter/UnicodeConverter.pro,\
				kernel)
addSubProject(graphics,		$$CORE_ROOT_DIR/DesktopEditor/graphics/pro/graphics.pro,\
				kernel unicodeconverter)
addSubProject(pdfwriter,	$$CORE_ROOT_DIR/PdfWriter/PdfWriter.pro,\
				kernel unicodeconverter graphics)
addSubProject(djvufile,		$$CORE_ROOT_DIR/DjVuFile/DjVuFile.pro,\
				kernel unicodeconverter graphics pdfwriter)
addSubProject(xpsfile,		$$CORE_ROOT_DIR/XpsFile/XpsFile.pro,\
				kernel unicodeconverter graphics pdfwriter)
addSubProject(htmlrenderer,	$$CORE_ROOT_DIR/HtmlRenderer/htmlrenderer.pro,\
				kernel unicodeconverter graphics pdfwriter)
addSubProject(pdfreader,	$$CORE_ROOT_DIR/PdfReader/PdfReader.pro,\
				kernel unicodeconverter graphics pdfwriter htmlrenderer)
addSubProject(htmlfile2,	$$CORE_ROOT_DIR/HtmlFile2/HtmlFile2.pro,\
				kernel unicodeconverter graphics)
addSubProject(doctrenderer,	$$CORE_ROOT_DIR/DesktopEditor/doctrenderer/doctrenderer.pro,\
				kernel unicodeconverter graphics)
addSubProject(fb2file,		$$CORE_ROOT_DIR/Fb2File/Fb2File.pro,\
				kernel unicodeconverter graphics)
addSubProject(epubfile,		$$CORE_ROOT_DIR/EpubFile/CEpubFile.pro,\
				kernel unicodeconverter graphics htmlfile2)
!no_x2t {
	addSubProject(docxformat,	$$CORE_ROOT_DIR/Common/DocxFormat/DocxFormatLib/DocxFormatLib.pro)
	addSubProject(pptxformat,	$$CORE_ROOT_DIR/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/PPTXFormatLib.pro)
	addSubProject(docxfile,		$$CORE_ROOT_DIR/ASCOfficeDocxFile2/Linux/ASCOfficeDocxFile2Lib.pro)
	addSubProject(txtxmlformat,	$$CORE_ROOT_DIR/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/TxtXmlFormatLib.pro)
	addSubProject(rtfformat,	$$CORE_ROOT_DIR/ASCOfficeRtfFile/RtfFormatLib/Linux/RtfFormatLib.pro)
	addSubProject(pptformat,	$$CORE_ROOT_DIR/ASCOfficePPTFile/PPTFormatLib/Linux/PPTFormatLib.pro)
	addSubProject(docformat,	$$CORE_ROOT_DIR/ASCOfficeDocFile/DocFormatLib/Linux/DocFormatLib.pro)
	addSubProject(odffilereader,	$$CORE_ROOT_DIR/ASCOfficeOdfFile/linux/OdfFileReaderLib.pro)
	addSubProject(odffilewriter,	$$CORE_ROOT_DIR/ASCOfficeOdfFileW/linux/OdfFileWriterLib.pro)
	addSubProject(xlsformat,	$$CORE_ROOT_DIR/ASCOfficeXlsFile2/source/linux/XlsFormatLib.pro)
	addSubProject(x2t,		$$CORE_ROOT_DIR/X2tConverter/build/Qt/X2tConverter.pro,\
					docxformat pptxformat docxfile txtxmlformat rtfformat pptformat docformat odffilereader odffilewriter xlsformat fb2file epubfile)
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
}

core_and_multimedia {
	addSubProject(videoplayer,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/videoplayerlib.pro,\
					kernel unicodeconverter graphics)
}
desktop {
	message(desktop)
	addSubProject(hunspell,		$$CORE_ROOT_DIR/DesktopEditor/hunspell-1.3.3/src/qt/hunspell.pro)
	addSubProject(ooxmlsignature,	$$CORE_ROOT_DIR/DesktopEditor/xmlsec/src/ooxmlsignature.pro,\
					kernel unicodeconverter graphics)
	addSubProject(documentscore,	$$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore.pro,\
					kernel unicodeconverter graphics hunspell ooxmlsignature htmlrenderer pdfwriter pdfreader djvufile xpsfile)
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

