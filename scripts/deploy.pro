TEMPLATE=aux

CONFIG -= debug_and_release debug_and_release_target
MAKEFILE=$$PWD/../makefiles/deploy.makefile

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

OS_CURRENT=$$(OS_DEPLOY)
QT_CURRENT=$$(QT_DEPLOY)

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out
createDirectory($$DEPLOY_DIR)
createDirectory($$DEPLOY_DIR/$$OS_CURRENT)

JS_ROOT=$$DEPLOY_DIR/js

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
	removeDirectory($$CUR_ROOT/dictionaries/.git)
	
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/package/fonts, $$CUR_ROOT/fonts)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/package/license/3dparty/3DPARTYLICENSE, $$CUR_ROOT/3DPARTYLICENSE)
	
	copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build, $$CUR_ROOT/.)
		
	copyFile($$QT_CURRENT/Qt5Core$$LIB_EXT, $$CUR_ROOT/Qt5Core$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Gui$$LIB_EXT, $$CUR_ROOT/Qt5Gui$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5PrintSupport$$LIB_EXT, $$CUR_ROOT/Qt5PrintSupport$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Svg$$LIB_EXT, $$CUR_ROOT/Qt5Svg$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Widgets$$LIB_EXT, $$CUR_ROOT/Qt5Widgets$$LIB_EXT)
	
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/hunspell$$LIB_EXT, $$CUR_ROOT/hunspell$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/videoplayer$$LIB_EXT, $$CUR_ROOT/videoplayer$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ooxmlsignature$$LIB_EXT, $$CUR_ROOT/ooxmlsignature$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ascdocumentscore$$LIB_EXT, $$CUR_ROOT/ascdocumentscore$$LIB_EXT)
	
	copyQtPlugin($$QT_CURRENT/../plugins/iconengines, $$CUR_ROOT/iconengines)
	copyQtPlugin($$QT_CURRENT/../plugins/imageformats, $$CUR_ROOT/imageformats)
	copyQtPlugin($$QT_CURRENT/../plugins/platforms, $$CUR_ROOT/platforms)
	copyQtPlugin($$QT_CURRENT/../plugins/printsupport, $$CUR_ROOT/printsupport)	
	copyQtPlugin($$QT_CURRENT/../plugins/styles, $$CUR_ROOT/styles)
	
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/extras/projicons/projicons.exe, $$CUR_ROOT/DesktopEditors.exe)
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/DesktopEditors.exe, $$CUR_ROOT/editors.exe)

	createDirectory($$CUR_ROOT/editors)
	copyDirectory($$JS_ROOT/desktop/sdkjs, $$CUR_ROOT/editors/sdkjs)
	copyDirectory($$JS_ROOT/desktop/web-apps, $$CUR_ROOT/editors/web-apps)
	copyFile($$JS_ROOT/desktop/index.html, $$CUR_ROOT/index.html)

}

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
	copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build, $$CUR_ROOT/HtmlFileInternal/.)
	
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/docbuilder$$EXE_EXT, $$CUR_ROOT/converter/docbuilder$$EXE_EXT)
}
