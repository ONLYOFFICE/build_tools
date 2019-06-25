TEMPLATE=aux

CONFIG -= debug_and_release debug_and_release_target
MAKEFILE=$$PWD/../makefiles/build_js.makefile

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out
createDirectory($$DEPLOY_DIR)

PUBLISHER_NAME = $$(OO_BRANDING)
isEmpty(PUBLISHER_NAME) {
	core_windows {
		PUBLISHER_NAME=ONLYOFFICE
	} else {
		PUBLISHER_NAME=onlyoffice
	}
}

createDirectory($$DEPLOY_DIR)
createDirectory($$DEPLOY_DIR/js)
createDirectory($$DEPLOY_DIR/js/$$PUBLISHER_NAME)

DEPLOY_DIR=$$DEPLOY_DIR/js/$$PUBLISHER_NAME

CONFIG += min_build

min_build {
	
	CUR_ROOT=$$DEPLOY_DIR/desktop
	createDirectory($$CUR_ROOT)

	runNPM($$ROOT_GIT_DIR/web-apps-pro/build)
	gruntInterface($$ROOT_GIT_DIR/web-apps-pro/build)
}

desktop {

	CUR_ROOT=$$DEPLOY_DIR/desktop
	removeDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT)

	runNPM($$ROOT_GIT_DIR/sdkjs/build)
	gruntDesktop($$ROOT_GIT_DIR/sdkjs/build)

	copyDirectory($$ROOT_GIT_DIR/sdkjs/deploy/sdkjs, $$CUR_ROOT/sdkjs)
	copyFile($$ROOT_GIT_DIR/sdkjs/common/HtmlFileInternal/AllFonts.js, $$CUR_ROOT/sdkjs/common/AllFonts.js)

	copyDirectory($$ROOT_GIT_DIR/web-apps-pro/deploy/web-apps, $$CUR_ROOT/web-apps)
	removeDirectory($$CUR_ROOT/web-apps/apps/documenteditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/documenteditor/mobile)
	removeDirectory($$CUR_ROOT/web-apps/apps/presentationeditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/presentationeditor/mobile)
	removeDirectory($$CUR_ROOT/web-apps/apps/spreadsheeteditor/embed)
	removeDirectory($$CUR_ROOT/web-apps/apps/spreadsheeteditor/mobile)

	copyFile($$ROOT_GIT_DIR/web-apps-pro/apps/api/documents/index.html.desktop, $$CUR_ROOT/web-apps/apps/api/documents/index.html)
	
	runNPM($$ROOT_GIT_DIR/desktop-apps/common/loginpage/build)
	gruntInterface($$ROOT_GIT_DIR/desktop-apps/common/loginpage/build)

	copyFile($$ROOT_GIT_DIR/desktop-apps/common/loginpage/deploy/index.html, $$CUR_ROOT/index.html)

}

builder {
	
	CUR_ROOT=$$DEPLOY_DIR/builder
	removeDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT)

	runNPM($$ROOT_GIT_DIR/sdkjs/build)
	gruntBuilder($$ROOT_GIT_DIR/sdkjs/build)

	copyDirectory($$ROOT_GIT_DIR/sdkjs/deploy/sdkjs, $$CUR_ROOT/sdkjs)
	copyDirectory($$ROOT_GIT_DIR/web-apps-pro/deploy/web-apps, $$CUR_ROOT/web-apps)

}
