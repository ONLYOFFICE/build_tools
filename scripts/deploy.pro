TEMPLATE=aux

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

MAKEFILE=$$PWD/../makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
build_xp {
	MAKEFILE=$$join(MAKEFILE, MAKEFILE, "", "_xp")
}

OS_CURRENT=$$(OS_DEPLOY)
QT_CURRENT=$$(QT_DEPLOY)

APPS_POSTFIX=$$OS_CURRENT
build_xp {
	APPS_POSTFIX=$$join(APPS_POSTFIX, APPS_POSTFIX, "", "_xp")
}
core_windows {
	APPS_POSTFIX=$$join(APPS_POSTFIX, APPS_POSTFIX, "", ".exe")
}

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out
createDirectory($$DEPLOY_DIR)

PUBLISHER_NAME = $$(OO_BRANDING)
!isEmpty(PUBLISHER_NAME) {
    DEPLOY_DIR=$$DEPLOY_DIR/PUBLISHER_NAME
	createDirectory($$DEPLOY_DIR)
}

JS_ROOT=$$DEPLOY_DIR/js

build_xp {
	DEPLOY_DIR=$$DEPLOY_DIR/xp
	createDirectory($$DEPLOY_DIR)
}

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
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58$$LIB_EXT, $$CUR_ROOT/converter/icudt58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58$$LIB_EXT, $$CUR_ROOT/converter/icuuc58$$LIB_EXT)

	build_xp {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp/doctrenderer$$LIB_EXT, $$CUR_ROOT/converter/doctrenderer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8_xp/$$OS_CURRENT/release/icudt*.dll, $$CUR_ROOT/converter/)
	} else {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/doctrenderer$$LIB_EXT, $$CUR_ROOT/converter/doctrenderer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudt*.dat, $$CUR_ROOT/converter/)
	}


	copyFile($$ROOT_GIT_DIR/desktop-apps/common/converter/DoctRenderer.config, $$CUR_ROOT/converter/DoctRenderer.config)
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/converter/empty, $$CUR_ROOT/converter/empty)
	
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal$$EXE_EXT)
	
	copyDirectory($$ROOT_GIT_DIR/dictionaries, $$CUR_ROOT/dictionaries)
	removeDirectory($$CUR_ROOT/dictionaries/.git)
	
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/package/fonts, $$CUR_ROOT/fonts)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/package/license/3dparty/3DPARTYLICENSE, $$CUR_ROOT/3DPARTYLICENSE)
	
	!build_xp {
		copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build, $$CUR_ROOT/.)
	} else {
		core_win_64 {
			copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/winxp_64/build, $$CUR_ROOT/.)
		} else {
			copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/winxp_32/build, $$CUR_ROOT/.)
		}
	}
		
	copyFile($$QT_CURRENT/Qt5Core$$LIB_EXT, $$CUR_ROOT/Qt5Core$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Gui$$LIB_EXT, $$CUR_ROOT/Qt5Gui$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5PrintSupport$$LIB_EXT, $$CUR_ROOT/Qt5PrintSupport$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Svg$$LIB_EXT, $$CUR_ROOT/Qt5Svg$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Widgets$$LIB_EXT, $$CUR_ROOT/Qt5Widgets$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Multimedia$$LIB_EXT, $$CUR_ROOT/Qt5Multimedia$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5MultimediaWidgets$$LIB_EXT, $$CUR_ROOT/Qt5MultimediaWidgets$$LIB_EXT)
	copyFile($$QT_CURRENT/Qt5Network$$LIB_EXT, $$CUR_ROOT/Qt5Network$$LIB_EXT)
	
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/hunspell$$LIB_EXT, $$CUR_ROOT/hunspell$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ooxmlsignature$$LIB_EXT, $$CUR_ROOT/ooxmlsignature$$LIB_EXT)

	build_xp {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp/videoplayer$$LIB_EXT, $$CUR_ROOT/videoplayer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp/ascdocumentscore$$LIB_EXT, $$CUR_ROOT/ascdocumentscore$$LIB_EXT)
	} else {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/videoplayer$$LIB_EXT, $$CUR_ROOT/videoplayer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ascdocumentscore$$LIB_EXT, $$CUR_ROOT/ascdocumentscore$$LIB_EXT)
	}
	
	copyQtPlugin($$QT_CURRENT/../plugins/bearer, $$CUR_ROOT/bearer)
	copyQtPlugin($$QT_CURRENT/../plugins/playlistformats, $$CUR_ROOT/playlistformats)
	copyQtPlugin($$QT_CURRENT/../plugins/iconengines, $$CUR_ROOT/iconengines)
	copyQtPlugin($$QT_CURRENT/../plugins/imageformats, $$CUR_ROOT/imageformats)
	copyQtPlugin($$QT_CURRENT/../plugins/platforms, $$CUR_ROOT/platforms)
	copyQtPlugin($$QT_CURRENT/../plugins/printsupport, $$CUR_ROOT/printsupport)
	copyQtPlugin($$QT_CURRENT/../plugins/mediaservice, $$CUR_ROOT/mediaservice)

	!build_xp {
		copyQtPlugin($$QT_CURRENT/../plugins/styles, $$CUR_ROOT/styles)
	}
	
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/extras/projicons/projicons_$$APPS_POSTFIX, $$CUR_ROOT/DesktopEditors.exe)
	copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/DesktopEditors_$$APPS_POSTFIX, $$CUR_ROOT/editors.exe)

	createDirectory($$CUR_ROOT/editors)
	copyDirectory($$JS_ROOT/desktop/sdkjs, $$CUR_ROOT/editors/sdkjs)
	copyDirectory($$JS_ROOT/desktop/web-apps, $$CUR_ROOT/editors/web-apps)
	copyFile($$JS_ROOT/desktop/index.html, $$CUR_ROOT/index.html)

	copyFile($$ROOT_GIT_DIR/desktop-apps/common/loginpage/addon/externalcloud.json, $$CUR_ROOT/editors/externalcloud.json)

	createDirectory($$CUR_ROOT/editors/sdkjs-plugins)
	copyFile($$ROOT_GIT_DIR/sdkjs-plugins/LICENSE.txt, $$CUR_ROOT/editors/sdkjs-plugins/LICENSE.txt)
	copyFile($$ROOT_GIT_DIR/sdkjs-plugins/README.md, $$CUR_ROOT/editors/sdkjs-plugins/README.md)
	copyFile($$ROOT_GIT_DIR/sdkjs-plugins/plugins.css, $$CUR_ROOT/editors/sdkjs-plugins/plugins.css)
	copyFile($$ROOT_GIT_DIR/sdkjs-plugins/pluginBase.js, $$CUR_ROOT/editors/sdkjs-plugins/pluginBase.js)

	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/symboltable, $$CUR_ROOT/editors/sdkjs-plugins/{03C18A8D-8E01-444A-86EB-EDDFA7773157})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/youtube, $$CUR_ROOT/editors/sdkjs-plugins/{38E022EA-AD92-45FC-B22B-49DF39746DB4})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/ocr, $$CUR_ROOT/editors/sdkjs-plugins/{440EBF13-9B19-4BD8-8621-05200E58140B})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/translate, $$CUR_ROOT/editors/sdkjs-plugins/{7327FC95-16DA-41D9-9AF2-0E7F449F687D})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/synonim, $$CUR_ROOT/editors/sdkjs-plugins/{BE5CBF95-C0AD-4842-B157-AC40FEDD9840})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/code, $$CUR_ROOT/editors/sdkjs-plugins/{BE5CBF95-C0AD-4842-B157-AC40FEDD9841})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/photoeditor, $$CUR_ROOT/editors/sdkjs-plugins/{07FD8DFA-DFE0-4089-AL24-0730933CC80A})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/macros, $$CUR_ROOT/editors/sdkjs-plugins/{E6978D28-0441-4BD7-8346-82FAD68BCA3B})
	copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/clipart, $$CUR_ROOT/editors/sdkjs-plugins/{F5BACB61-64C5-4711-AC8A-D01EC3B2B6F1})

	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/{8D67F3C5-7736-4BAE-A0F2-8C7127DC4BB8}, $$CUR_ROOT/editors/sdkjs-plugins/{8D67F3C5-7736-4BAE-A0F2-8C7127DC4BB8})
	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/common/{14A8FC87-8E26-4216-B34E-F27F053B2EC4}, $$CUR_ROOT/editors/sdkjs-plugins/{14A8FC87-8E26-4216-B34E-F27F053B2EC4})
	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/engine/blockchain/{B17BDC61-59FC-41A7-A471-CD2C415A665E}, $$CUR_ROOT/editors/sdkjs-plugins/{B17BDC61-59FC-41A7-A471-CD2C415A665E})

	core_windows {
		updmodule {
			copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/3dparty/WinSparkle/$$OS_CURRENT/WinSparkle$$LIB_EXT, $$CUR_ROOT/WinSparkle$$LIB_EXT)
		}

		removeFile($$CUR_ROOT/cef_sandbox.lib)
		removeFile($$CUR_ROOT/libcef.lib)
	}

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
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58$$LIB_EXT, $$CUR_ROOT/icudt58$$LIB_EXT)
	copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58$$LIB_EXT, $$CUR_ROOT/icuuc58$$LIB_EXT)

	build_xp {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp/doctrenderer$$LIB_EXT, $$CUR_ROOT/doctrenderer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8_xp/$$OS_CURRENT/release/icudt*.dll, $$CUR_ROOT/)
	} else {
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/doctrenderer$$LIB_EXT, $$CUR_ROOT/doctrenderer$$LIB_EXT)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudt*.dat, $$CUR_ROOT/)
	}
	
	!build_xp {
		createDirectory($$CUR_ROOT/HtmlFileInternal)
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal/HtmlFileInternal$$EXE_EXT)
		copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build, $$CUR_ROOT/HtmlFileInternal/.)

		core_windows {
			removeFile($$CUR_ROOT/HtmlFileInternal/cef_sandbox.lib)
			removeFile($$CUR_ROOT/HtmlFileInternal/libcef.lib)
		}
	}
	
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/docbuilder$$EXE_EXT, $$CUR_ROOT/docbuilder$$EXE_EXT)

	copyFile($$ROOT_GIT_DIR/DocumentBuilder/DoctRenderer.config, $$CUR_ROOT/DoctRenderer.config)
	
	copyDirectory($$JS_ROOT/builder/sdkjs, $$CUR_ROOT/sdkjs)
	createDirectory($$CUR_ROOT/sdkjs/vendor)
	copyDirectory($$JS_ROOT/builder/web-apps/vendor/jquery, $$CUR_ROOT/sdkjs/vendor/jquery)
	copyDirectory($$JS_ROOT/builder/web-apps/vendor/xregexp, $$CUR_ROOT/sdkjs/vendor/xregexp)

	copyDirectory($$ROOT_GIT_DIR/DocumentBuilder/empty, $$CUR_ROOT/empty)
	copyDirectory($$ROOT_GIT_DIR/DocumentBuilder/samples, $$CUR_ROOT/samples)

}
