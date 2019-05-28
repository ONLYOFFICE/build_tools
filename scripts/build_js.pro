TEMPLATE=aux

CONFIG -= debug_and_release debug_and_release_target
MAKEFILE=$$PWD/../makefiles/build_js.makefile

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

OS_CURRENT=$$(OS_DEPLOY)
QT_CURRENT=$$(QT_DEPLOY)

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out
createDirectory($$DEPLOY_DIR)

PUBLISHER_NAME = $$(OO_BRANDING)
!isEmpty(PUBLISHER_NAME) {
    DEPLOY_DIR=$$DEPLOY_DIR/PUBLISHER_NAME
	createDirectory($$DEPLOY_DIR)
}

createDirectory($$DEPLOY_DIR/js)

CONFIG += min_build

min_build {
	
	CUR_ROOT=$$DEPLOY_DIR/js/desktop
	createDirectory($$CUR_ROOT)

	runNPM($$ROOT_GIT_DIR/web-apps-pro/build)
	gruntInterface($$ROOT_GIT_DIR/web-apps-pro/build)
}

desktop {

	CUR_ROOT=$$DEPLOY_DIR/js/desktop
	createDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT/sdkjs)

	runNPM($$ROOT_GIT_DIR/sdkjs/build)
	gruntDesktop($$ROOT_GIT_DIR/sdkjs/build)

	createDirectory($$CUR_ROOT/sdkjs/common)
	copyDirectory($$ROOT_GIT_DIR/sdkjs/common/Images, $$CUR_ROOT/sdkjs/common/Images)
	#removeFile($$ROOT_GIT_DIR/sdkjs/common/Images/fonts_thumbnail*)
	
	createDirectory($$CUR_ROOT/sdkjs/common/Native)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/Native/native.js, $$CUR_ROOT/sdkjs/common/Native/native.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/Native/jquery_native.js, $$CUR_ROOT/sdkjs/common/Native/jquery_native.js)

	createDirectory($$CUR_ROOT/sdkjs/common/libfont)
	createDirectory($$CUR_ROOT/sdkjs/common/libfont/js)
	createDirectory($$CUR_ROOT/sdkjs/common/libfont/wasm)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/js/fonts.js, $$CUR_ROOT/sdkjs/common/libfont/js/fonts.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/wasm/fonts.js, $$CUR_ROOT/sdkjs/common/libfont/wasm/fonts.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/wasm/fonts.wasm, $$CUR_ROOT/sdkjs/common/libfont/wasm/fonts.wasm)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/HtmlFileInternal/AllFonts.js, $$CUR_ROOT/sdkjs/common/AllFonts.js)

	createDirectory($$CUR_ROOT/sdkjs/cell)
	createDirectory($$CUR_ROOT/sdkjs/cell/css)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/css/main.css, $$CUR_ROOT/sdkjs/cell/css/main.css)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/sdk-all-min.js, $$CUR_ROOT/sdkjs/cell/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/sdk-all.js, $$CUR_ROOT/sdkjs/cell/sdk-all.js)

	createDirectory($$CUR_ROOT/sdkjs/word)
	copyFile($$ROOT_GIT_DIR/sdkjs/word/sdk-all-min.js, $$CUR_ROOT/sdkjs/word/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/word/sdk-all.js, $$CUR_ROOT/sdkjs/word/sdk-all.js)

	createDirectory($$CUR_ROOT/sdkjs/slide)
	copyDirectory($$ROOT_GIT_DIR/sdkjs/slide/themes, $$CUR_ROOT/sdkjs/slide/themes)
	copyFile($$ROOT_GIT_DIR/sdkjs/slide/sdk-all-min.js, $$CUR_ROOT/sdkjs/slide/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/slide/sdk-all.js, $$CUR_ROOT/sdkjs/slide/sdk-all.js)

	copyDirectory($$ROOT_GIT_DIR/web-apps-pro/deploy/web-apps, $$CUR_ROOT/web-apps)
	removeDirectory($$CUR_ROOT/web-apps/apps/documenteditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/documenteditor/mobile)
	removeDirectory($$CUR_ROOT/web-apps/apps/presentationeditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/presentationeditor/mobile)
	removeDirectory($$CUR_ROOT/web-apps/apps/spreadsheeteditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/spreadsheeteditor/mobile)

	removeFile($$CUR_ROOT/web-apps/apps/api/documents/index.html)
	copyFile($$ROOT_GIT_DIR/web-apps-pro/apps/api/documents/index.html.desktop, $$CUR_ROOT/web-apps/apps/api/documents/index.html)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/loginpage/deploy/index.html, $$CUR_ROOT/index.html)

	runNPM2($$ROOT_GIT_DIR/desktop-apps/common/loginpage/build)
	gruntInterface($$ROOT_GIT_DIR/desktop-apps/common/loginpage/build)

}

builder {
	
	CUR_ROOT=$$DEPLOY_DIR/js/builder
	createDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT/sdkjs)

	runNPM($$ROOT_GIT_DIR/sdkjs/build)
	gruntBuilder($$ROOT_GIT_DIR/sdkjs/build)

	createDirectory($$CUR_ROOT/sdkjs/common)
	copyDirectory($$ROOT_GIT_DIR/sdkjs/common/Images, $$CUR_ROOT/sdkjs/common/Images)
	#removeFile($$ROOT_GIT_DIR/sdkjs/common/Images/fonts_thumbnail*)
	
	createDirectory($$CUR_ROOT/sdkjs/common/Native)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/Native/native.js, $$CUR_ROOT/sdkjs/common/Native/native.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/Native/jquery_native.js, $$CUR_ROOT/sdkjs/common/Native/jquery_native.js)

	createDirectory($$CUR_ROOT/sdkjs/common/libfont)
	createDirectory($$CUR_ROOT/sdkjs/common/libfont/js)
	createDirectory($$CUR_ROOT/sdkjs/common/libfont/wasm)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/js/fonts.js, $$CUR_ROOT/sdkjs/common/libfont/js/fonts.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/wasm/fonts.js, $$CUR_ROOT/sdkjs/common/libfont/wasm/fonts.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/libfont/wasm/fonts.wasm, $$CUR_ROOT/sdkjs/common/libfont/wasm/fonts.wasm)

	createDirectory($$CUR_ROOT/sdkjs/cell)
	createDirectory($$CUR_ROOT/sdkjs/cell/css)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/css/main.css, $$CUR_ROOT/sdkjs/cell/css/main.css)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/sdk-all-min.js, $$CUR_ROOT/sdkjs/cell/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/cell/sdk-all.js, $$CUR_ROOT/sdkjs/cell/sdk-all.js)

	createDirectory($$CUR_ROOT/sdkjs/word)
	copyFile($$ROOT_GIT_DIR/sdkjs/word/sdk-all-min.js, $$CUR_ROOT/sdkjs/word/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/word/sdk-all.js, $$CUR_ROOT/sdkjs/word/sdk-all.js)

	createDirectory($$CUR_ROOT/sdkjs/slide)
	copyDirectory($$ROOT_GIT_DIR/sdkjs/slide/themes, $$CUR_ROOT/sdkjs/slide/themes)
	copyFile($$ROOT_GIT_DIR/sdkjs/slide/sdk-all-min.js, $$CUR_ROOT/sdkjs/slide/sdk-all-min.js)
	copyFile($$ROOT_GIT_DIR/sdkjs/slide/sdk-all.js, $$CUR_ROOT/sdkjs/slide/sdk-all.js)

	copyDirectory($$ROOT_GIT_DIR/web-apps-pro/deploy/web-apps, $$CUR_ROOT/web-apps)

}
