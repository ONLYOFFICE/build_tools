TEMPLATE=aux

CONFIG -= debug_and_release debug_and_release_target
MAKEFILE=$$PWD/../makefiles/deploy.makefile

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out
createDirectory($$DEPLOY_DIR)
createDirectory($$DEPLOY_DIR/$$OS_CURRENT)

desktop {
	
	CUR_ROOT=$$DEPLOY_DIR/$$OS_CURRENT/desktop
	createDirectory($$CUR_ROOT)

	createDirectory($$CUR_ROOT/converter)
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/x2t$$EXE_EXT, $$CUR_ROOT/converter/x2t$$EXE_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/kernel$$LIB_EXT, $$CUR_ROOT/converter/kernel$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/UnicodeConverter$$LIB_EXT, $$CUR_ROOT/converter/UnicodeConverter$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/graphics$$LIB_EXT, $$CUR_ROOT/converter/graphics$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/PdfWriter$$LIB_EXT, $$CUR_ROOT/converter/PdfWriter$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/PdfReader$$LIB_EXT, $$CUR_ROOT/converter/PdfReader$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/DjVuFile$$LIB_EXT, $$CUR_ROOT/converter/DjVuFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/XpsFile$$LIB_EXT, $$CUR_ROOT/converter/XpsFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFile$$LIB_EXT, $$CUR_ROOT/converter/HtmlFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlRenderer$$LIB_EXT, $$CUR_ROOT/converter/HtmlRenderer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/doctrenderer$$LIB_EXT, $$CUR_ROOT/converter/doctrenderer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58$$LIB_EXT, $$CUR_ROOT/converter/icudt58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58$$LIB_EXT, $$CUR_ROOT/converter/icuuc58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudtl.dat, $$CUR_ROOT/converter/icudtl.dat)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/converter/DoctRenderer.config, $$CUR_ROOT/converter/DoctRenderer.config)
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/converter/empty, $$CUR_ROOT/converter/empty)
	
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal$$EXE_EXT)
	
	copyDirectory($$ROOT_GIT_DIR/dictionaries, $$CUR_ROOT/dictionaries)
	removeDicrionary($$CUR_ROOT/dictionaries/.git)
	
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/package/fonts, $$CUR_ROOT/fonts)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/package/license/3dparty/3DPARTYLICENSE, $$CUR_ROOT/3DPARTYLICENSE)
	
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build/*, $$CUR_ROOT/.)
		
	copyFile($$OO_QT_DIR/Qt5Core$$LIB_EXT, Qt5Core$$LIB_EXT)
	copyFile($$OO_QT_DIR/Qt5Gui$$LIB_EXT, Qt5Gui$$LIB_EXT)
	copyFile($$OO_QT_DIR/Qt5PrintSupport$$LIB_EXT, Qt5PrintSupport$$LIB_EXT)
	copyFile($$OO_QT_DIR/Qt5Svg$$LIB_EXT, Qt5Svg$$LIB_EXT)
	copyFile($$OO_QT_DIR/Qt5Widgets$$LIB_EXT, Qt5Widgets$$LIB_EXT)
	
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/hunspell$$EXE_EXT, $$CUR_ROOT/hunspell$$EXE_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/videoplayer$$LIB_EXT, $$CUR_ROOT/videoplayer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ooxmlsignature$$LIB_EXT, $$CUR_ROOT/ooxmlsignature$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ascdocumentscore$$LIB_EXT, $$CUR_ROOT/ascdocumentscore$$LIB_EXT)
	
	copyQtPlugin($$OO_QT_DIR/../plugins/iconengines, $$CUR_ROOT/iconengines)
	copyQtPlugin($$OO_QT_DIR/../plugins/imageformats, $$CUR_ROOT/imageformats)
	copyQtPlugin($$OO_QT_DIR/../plugins/platforms, $$CUR_ROOT/platforms)
	copyQtPlugin($$OO_QT_DIR/../plugins/printsupport, $$CUR_ROOT/printsupport)	
	copyQtPlugin($$OO_QT_DIR/../plugins/styles, $$CUR_ROOT/styles)
	
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/extras/projicons/projicons.exe, $$CUR_ROOT/DesktopEditors.exe)
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/DesktopEditors.exe, $$CUR_ROOT/editors.exe)
)

builder {
	
	CUR_ROOT=$$DEPLOY_DIR/$$OS_CURRENT/builder
	createDirectory($$CUR_ROOT)
	
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/x2t$$EXE_EXT, $$CUR_ROOT/x2t$$EXE_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/kernel$$LIB_EXT, $$CUR_ROOT/kernel$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/UnicodeConverter$$LIB_EXT, $$CUR_ROOT/UnicodeConverter$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/graphics$$LIB_EXT, $$CUR_ROOT/graphics$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/PdfWriter$$LIB_EXT, $$CUR_ROOT/PdfWriter$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/PdfReader$$LIB_EXT, $$CUR_ROOT/PdfReader$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/DjVuFile$$LIB_EXT, $$CUR_ROOT/DjVuFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/XpsFile$$LIB_EXT, $$CUR_ROOT/XpsFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFile$$LIB_EXT, $$CUR_ROOT/HtmlFile$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlRenderer$$LIB_EXT, $$CUR_ROOT/HtmlRenderer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/doctrenderer$$LIB_EXT, $$CUR_ROOT/doctrenderer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58$$LIB_EXT, $$CUR_ROOT/icudt58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58$$LIB_EXT, $$CUR_ROOT/icuuc58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudtl.dat, $$CUR_ROOT/icudtl.dat)
	
	createDirectory($$CUR_ROOT/HtmlFileInternal)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal/HtmlFileInternal$$EXE_EXT)
	
}
