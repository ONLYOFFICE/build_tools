TEMPLATE=aux

include($$PWD/../core/Common/base.pri)
include($$PWD/scripts/common.pri)

MAKEFILE=$$PWD/../makefiles/build_clean.makefile_$$CORE_BUILDS_PLATFORM_PREFIX

OO_OS = $$(OS_DEPLOY)
isEmpty(OO_OS) {
	PLATFORMS = \
		win_64 \
		win_32 \
		win_64_xp \
		win_32_xp \
		linux_64 \
		linux_32 \
		mac_64

	OO_BRANDING_SUFFIX = $$(OO_BRANDING)
	!isEmpty(OO_BRANDING_SUFFIX) {
	PLATFORMS += \
		win_64$$OO_BRANDING_SUFFIX \
		win_32$$OO_BRANDING_SUFFIX \
		win_64_xp$$OO_BRANDING_SUFFIX \
		win_32_xp$$OO_BRANDING_SUFFIX \
		linux_64$$OO_BRANDING_SUFFIX \
		linux_32$$OO_BRANDING_SUFFIX \
		mac_64$$OO_BRANDING_SUFFIX
	}
} else {
	PLATFORMS = $$OO_OS

	OO_BRANDING_SUFFIX = $$(OO_BRANDING)
	!isEmpty(OO_BRANDING_SUFFIX) {
	PLATFORMS += \
		$$OO_OS$$OO_BRANDING_SUFFIX
	}
}

ROOT_DIR=$$PWD/..

for(PRO_SUFFIX, PLATFORMS) {
    removeFile($$ROOT_DIR/core/Common/3dParty/cryptopp/project/Makefile.cryptopp$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/Common/Makefile.kernel$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/UnicodeConverter/Makefile.UnicodeConverter$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/DesktopEditor/graphics/pro/Makefile.graphics$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/PdfWriter/Makefile.PdfWriter$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/DjVuFile/Makefile.DjVuFile$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/XpsFile/Makefile.XpsFile$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/HtmlRenderer/Makefile.htmlrenderer$$PRO_SUFFIX)
    removeFile($$ROOT_DIR/core/PdfReader/Makefile.PdfReader$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/HtmlFile/Makefile.HtmlFile$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/DesktopEditor/doctrenderer/Makefile.doctrenderer$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/HtmlFile/Internal/Makefile.Internal$$PRO_SUFFIX)

	removeFile($$ROOT_DIR/core/DesktopEditor/AllFontsGen/Makefile.AllFontsGen$$PRO_SUFFIX)	
	removeFile($$ROOT_DIR/core/DesktopEditor/doctrenderer/app_builder/Makefile.docbuilder$$PRO_SUFFIX)

	removeFile($$ROOT_DIR/core/Common/DocxFormat/DocxFormatLib/Makefile.DocxFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficePPTXFile/PPTXLib/Linux/PPTXFormatLib/Makefile.PPTXFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeDocxFile2/Linux/Makefile.ASCOfficeDocxFile2Lib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeTxtFile/TxtXmlFormatLib/Linux/Makefile.TxtXmlFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeRtfFile/RtfFormatLib/Linux/Makefile.RtfFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficePPTFile/PPTFormatLib/Linux/Makefile.PPTFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeDocFile/DocFormatLib/Linux/Makefile.DocFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeOdfFile/linux/Makefile.OdfFileReaderLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeOdfFileW/linux/Makefile.OdfFileWriterLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/ASCOfficeXlsFile2/source/linux/Makefile.XlsFormatLib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/X2tConverter/build/Qt/Makefile.X2tConverter$$PRO_SUFFIX)

	removeFile($$ROOT_DIR/core/DesktopEditor/hunspell-1.3.3/src/qt/Makefile.hunspell$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/core/DesktopEditor/xmlsec/src/Makefile.ooxmlsignature$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.AscDocumentsCore_win$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/lib/Makefile.AscDocumentsCore_linux$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-sdk/ChromiumBasedEditors/videoplayerlib/Makefile.videoplayerlib$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-apps/win-linux/extras/projicons/Makefile.ProjIcons$$PRO_SUFFIX)
	removeFile($$ROOT_DIR/desktop-apps/win-linux/Makefile.ASCDocumentEditor$$PRO_SUFFIX)
}