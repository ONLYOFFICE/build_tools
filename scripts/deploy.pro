TEMPLATE=aux

include($$PWD/../../core/Common/base.pri)
include($$PWD/common.pri)

MAKEFILE=$$PWD/../makefiles/deploy.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
build_xp {
	MAKEFILE=$$join(MAKEFILE, MAKEFILE, "", "_xp")
}

OS_CURRENT=$$(OS_DEPLOY)
QT_CURRENT=$$(QT_DEPLOY)

APPS_POSTFIX=$$OS_CURRENT
OS_CURRENT_DEPLOY=$$OS_CURRENT
build_xp {
	APPS_POSTFIX=$$join(APPS_POSTFIX, APPS_POSTFIX, "", "_xp")
	OS_CURRENT_DEPLOY=$$join(OS_CURRENT_DEPLOY, OS_CURRENT_DEPLOY, "", "_xp")
}
core_windows {
	APPS_POSTFIX=$$join(APPS_POSTFIX, APPS_POSTFIX, "", ".exe")
}

ROOT_GIT_DIR=$$PWD/../..
DEPLOY_DIR=$$PWD/../out

PUBLISHER_NAME = $$(OO_BRANDING)
isEmpty(PUBLISHER_NAME) {
	core_windows {
		PUBLISHER_NAME=ONLYOFFICE
	} else {
		PUBLISHER_NAME=onlyoffice
	}
}

createDirectory($$DEPLOY_DIR)
createDirectory($$DEPLOY_DIR/$$OS_CURRENT_DEPLOY)
createDirectory($$DEPLOY_DIR/$$OS_CURRENT_DEPLOY/$$PUBLISHER_NAME)

JS_ROOT=$$DEPLOY_DIR/js/$$PUBLISHER_NAME
DEPLOY_DIR=$$DEPLOY_DIR/$$OS_CURRENT_DEPLOY/$$PUBLISHER_NAME

desktop {
	
	core_windows {
		CUR_ROOT=$$DEPLOY_DIR/DesktopEditors
	} else {
		CUR_ROOT=$$DEPLOY_DIR/desktopeditors
	}
	removeDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT)

	createDirectory($$CUR_ROOT/converter)
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/x2t$$EXE_EXT, $$CUR_ROOT/converter/x2t$$EXE_EXT)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, kernel)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, UnicodeConverter)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, graphics)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, PdfWriter)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, PdfReader)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, DjVuFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, XpsFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, HtmlFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, HtmlRenderer)

	core_windows {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58.dll, $$CUR_ROOT/converter/icudt58.dll)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58.dll, $$CUR_ROOT/converter/icuuc58.dll)
	} 
	core_linux {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicudata.so.58, $$CUR_ROOT/converter/libicudata.so.58)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicuuc.so.58, $$CUR_ROOT/converter/libicuuc.so.58)
	}
	core_mac {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicudata.58.dylib, $$CUR_ROOT/converter/libicudata.58.dylib)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicuuc.58.dylib, $$CUR_ROOT/converter/libicuuc.58.dylib)
	}

	build_xp {
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp, $$CUR_ROOT/converter, doctrenderer)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8_xp/$$OS_CURRENT/release/icudt*.dll, $$CUR_ROOT/converter/)
	} else {
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT/converter, doctrenderer)

		core_windows {
			copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudt*.dat, $$CUR_ROOT/converter/)
		} else {
			copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/icudtl.dat, $$CUR_ROOT/converter/)
		}
	}

	copyFile($$ROOT_GIT_DIR/desktop-apps/common/converter/DoctRenderer.config, $$CUR_ROOT/converter/DoctRenderer.config)
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/converter/empty, $$CUR_ROOT/converter/empty)
	
	!core_mac {
		!build_xp {
			copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal$$EXE_EXT)
		}
	}
	
	copyDirectory($$ROOT_GIT_DIR/dictionaries, $$CUR_ROOT/dictionaries)
	removeDirectory($$CUR_ROOT/dictionaries/.git)
	
	copyDirectory($$ROOT_GIT_DIR/desktop-apps/common/package/fonts, $$CUR_ROOT/fonts)
	copyFile($$ROOT_GIT_DIR/desktop-apps/common/package/license/3dparty/3DPARTYLICENSE, $$CUR_ROOT/3DPARTYLICENSE)
	
	!build_xp {
		copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build/., $$CUR_ROOT/)
	} else {
		core_win_64 {
			copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/winxp_64/build, $$CUR_ROOT/.)
		} else {
			copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/winxp_32/build, $$CUR_ROOT/.)
		}
	}

	core_mac {
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, hunspell)
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, ooxmlsignature)
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, ascdocumentscore)
		copyDirectory("$$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/ONLYOFFICE Helper.app", $$CUR_ROOT/)
	} else {
		copyQtLib(Qt5Core, $$CUR_ROOT)
		copyQtLib(Qt5Gui, $$CUR_ROOT)
		copyQtLib(Qt5PrintSupport, $$CUR_ROOT)
		copyQtLib(Qt5Svg, $$CUR_ROOT)
		copyQtLib(Qt5Widgets, $$CUR_ROOT)
		copyQtLib(Qt5Multimedia, $$CUR_ROOT)
		copyQtLib(Qt5MultimediaWidgets, $$CUR_ROOT)
		copyQtLib(Qt5Network, $$CUR_ROOT)
		copyQtLib(Qt5OpenGL, $$CUR_ROOT)

		core_linux {
			system(cp -f -av "$$QT_CURRENT/../lib/libicui18n*" $$shell_quote($$CUR_ROOT/) $$escape_expand(\\n\\t))
			system(cp -f -av "$$QT_CURRENT/../lib/libicuuc*" $$shell_quote($$CUR_ROOT/) $$escape_expand(\\n\\t))
			system(cp -f -av "$$QT_CURRENT/../lib/libicudata*" $$shell_quote($$CUR_ROOT/) $$escape_expand(\\n\\t))
		}

		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, hunspell)
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, ooxmlsignature)

		build_xp {
			copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp, $$CUR_ROOT, videoplayer)
			copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp, $$CUR_ROOT, ascdocumentscore)
		} else {
			copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, videoplayer)
			copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, ascdocumentscore)
		}
		
		copyQtPlugin($$QT_CURRENT/../plugins/bearer, $$CUR_ROOT/bearer)
		copyQtPlugin($$QT_CURRENT/../plugins/iconengines, $$CUR_ROOT/iconengines)
		copyQtPlugin($$QT_CURRENT/../plugins/imageformats, $$CUR_ROOT/imageformats)
		copyQtPlugin($$QT_CURRENT/../plugins/platforms, $$CUR_ROOT/platforms)
		copyQtPlugin($$QT_CURRENT/../plugins/platforminputcontexts, $$CUR_ROOT/platforminputcontexts)
		copyQtPlugin($$QT_CURRENT/../plugins/printsupport, $$CUR_ROOT/printsupport)	
		copyQtPlugin($$QT_CURRENT/../plugins/mediaservice, $$CUR_ROOT/mediaservice)
		copyQtPlugin($$QT_CURRENT/../plugins/playlistformats, $$CUR_ROOT/playlistformats)
	}
	
	core_linux {
		copyQtLib(Qt5DBus, $$CUR_ROOT)
		copyQtLib(Qt5X11Extras, $$CUR_ROOT)
		copyQtLib(Qt5XcbQpa, $$CUR_ROOT)
		
		copyQtPlugin($$QT_CURRENT/../plugins/platformthemes, $$CUR_ROOT/platformthemes)
		copyQtPlugin($$QT_CURRENT/../plugins/xcbglintegrations, $$CUR_ROOT/xcbglintegrations)
		
		system(cp -f -av "$$QT_CURRENT/../lib/libqgsttools_p.so*" $$shell_quote($$CUR_ROOT/) $$escape_expand(\\n\\t))
	}

	core_windows {
		!build_xp {
			copyQtPlugin($$QT_CURRENT/../plugins/styles, $$CUR_ROOT/styles)
		}
	}
	
	core_windows {	
		copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/extras/projicons/projicons_$$APPS_POSTFIX, $$CUR_ROOT/DesktopEditors.exe)
		copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/DesktopEditors_$$APPS_POSTFIX, $$CUR_ROOT/editors.exe)
		copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/res/icons/desktopeditors.ico, $$CUR_ROOT/app.ico)
	}
	core_linux {
		copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/DesktopEditors_$$APPS_POSTFIX, $$CUR_ROOT/DesktopEditors)
	}

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
	# copyDirectory($$ROOT_GIT_DIR/sdkjs-plugins/clipart, $$CUR_ROOT/editors/sdkjs-plugins/{F5BACB61-64C5-4711-AC8A-D01EC3B2B6F1})

	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/{8D67F3C5-7736-4BAE-A0F2-8C7127DC4BB8}, $$CUR_ROOT/editors/sdkjs-plugins/{8D67F3C5-7736-4BAE-A0F2-8C7127DC4BB8})

	!core_mac {
		copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/{060E6A7D-2766-44E8-A0EE-9A8CB9DB00D1}, $$CUR_ROOT/editors/sdkjs-plugins/{060E6A7D-2766-44E8-A0EE-9A8CB9DB00D1})
		copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/{B509123E-6335-40BD-B965-91EB799346E3}, $$CUR_ROOT/editors/sdkjs-plugins/{B509123E-6335-40BD-B965-91EB799346E3})
		copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/{F7E59EB4-317E-4E0B-AB2C-58E038A59EE2}, $$CUR_ROOT/editors/sdkjs-plugins/{F7E59EB4-317E-4E0B-AB2C-58E038A59EE2})
	}

	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/common/{14A8FC87-8E26-4216-B34E-F27F053B2EC4}, $$CUR_ROOT/editors/sdkjs-plugins/{14A8FC87-8E26-4216-B34E-F27F053B2EC4})
	copyDirectory($$ROOT_GIT_DIR/desktop-sdk/ChromiumBasedEditors/plugins/encrypt/ui/engine/database/{9AB4BBA8-A7E5-48D5-B683-ECE76A020BB1}, $$CUR_ROOT/editors/sdkjs-plugins/{9AB4BBA8-A7E5-48D5-B683-ECE76A020BB1})

	core_windows {
		updmodule {
			copyFile($$ROOT_GIT_DIR/desktop-apps/win-linux/3dparty/WinSparkle/$$OS_CURRENT/WinSparkle$$LIB_EXT, $$CUR_ROOT/WinSparkle$$LIB_EXT)
		}

		removeFile($$CUR_ROOT/cef_sandbox.lib)
		removeFile($$CUR_ROOT/libcef.lib)
	}

	# all themes generate ----
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/allfontsgen$$EXE_EXT, $$CUR_ROOT/converter/allfontsgen$$EXE_EXT)
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/allthemesgen$$EXE_EXT, $$CUR_ROOT/converter/allthemesgen$$EXE_EXT)

	core_mac {
		system(DYLD_LIBRARY_PATH=$$CUR_ROOT/converter $$CUR_ROOT/converter/allfontsgen$$EXE_EXT --use-system="1" --input="$$CUR_ROOT/fonts" --allfonts="$$CUR_ROOT/converter/AllFonts.js" --selection="$$CUR_ROOT/converter/font_selection.bin")
		system(DYLD_LIBRARY_PATH=$$CUR_ROOT/converter $$CUR_ROOT/converter/allthemesgen$$EXE_EXT --converter-dir="$$CUR_ROOT/converter" --src="$$CUR_ROOT/editors/sdkjs/slide/themes" --output="$$CUR_ROOT/editors/sdkjs/common/Images" --allfonts="AllFonts.js")
	} else {
		system($$CUR_ROOT/converter/allfontsgen$$EXE_EXT --use-system="1" --input="$$CUR_ROOT/fonts" --allfonts="$$CUR_ROOT/converter/AllFonts.js" --selection="$$CUR_ROOT/converter/font_selection.bin")
		system($$CUR_ROOT/converter/allthemesgen$$EXE_EXT --converter-dir="$$CUR_ROOT/converter" --src="$$CUR_ROOT/editors/sdkjs/slide/themes" --output="$$CUR_ROOT/editors/sdkjs/common/Images" --allfonts="AllFonts.js")
	}

	removeFile($$CUR_ROOT/converter/allfontsgen$$EXE_EXT)
	removeFile($$CUR_ROOT/converter/allthemesgen$$EXE_EXT)
	removeFile($$CUR_ROOT/converter/AllFonts.js)
	removeFile($$CUR_ROOT/converter/font_selection.bin)
	removeFile($$CUR_ROOT/editors/sdkjs/slide/sdk-all.cache)
	# ----
}

builder {
	
	core_windows {
		CUR_ROOT=$$DEPLOY_DIR/DocumentBuilder
	} else {
		CUR_ROOT=$$DEPLOY_DIR/documentbuilder
	}
	removeDirectory($$CUR_ROOT)
	createDirectory($$CUR_ROOT)
	
	copyFile($$ROOT_GIT_DIR/core/build/bin/$$OS_CURRENT/x2t$$EXE_EXT, $$CUR_ROOT/x2t$$EXE_EXT)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, kernel)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, UnicodeConverter)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, graphics)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, PdfWriter)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, PdfReader)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, DjVuFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, XpsFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, HtmlFile)
	copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, HtmlRenderer)

	core_windows {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icudt58.dll, $$CUR_ROOT/icudt58.dll)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/icuuc58.dll, $$CUR_ROOT/icuuc58.dll)
	} 
	core_linux {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicudata.so.58, $$CUR_ROOT/libicudata.so.58)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicuuc.so.58, $$CUR_ROOT/libicuuc.so.58)
	}
	core_mac {
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicudata.58.dylib, $$CUR_ROOT/libicudata.58.dylib)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/icu/$$OS_CURRENT/build/libicuuc.58.dylib, $$CUR_ROOT/libicuuc.58.dylib)
	}

	build_xp {
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp, $$CUR_ROOT, doctrenderer)
		copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/xp/doctrenderer.lib, $$CUR_ROOT/doctrenderer.lib)
		copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8_xp/$$OS_CURRENT/release/icudt*.dll, $$CUR_ROOT/)
	} else {
		copyLib($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT, $$CUR_ROOT, doctrenderer)

		core_windows {
			copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/doctrenderer.lib, $$CUR_ROOT/doctrenderer.lib)
			copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/release/icudt*.dat, $$CUR_ROOT/)
		} else {
			copyFile($$ROOT_GIT_DIR/core/Common/3dParty/v8/v8/out.gn/$$OS_CURRENT/icudtl.dat, $$CUR_ROOT/)
		}			
	}
	
	!build_xp {

		!core_mac {
			!build_xp {
				createDirectory($$CUR_ROOT/HtmlFileInternal)
				copyFile($$ROOT_GIT_DIR/core/build/lib/$$OS_CURRENT/HtmlFileInternal$$EXE_EXT, $$CUR_ROOT/HtmlFileInternal/HtmlFileInternal$$EXE_EXT)
				copyDirectory($$ROOT_GIT_DIR/core/Common/3dParty/cef/$$OS_CURRENT/build, $$CUR_ROOT/HtmlFileInternal/.)
			}
		}

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

	copyDirectory($$ROOT_GIT_DIR/core/DesktopEditor/doctrenderer/docbuilder.com/include, $$CUR_ROOT/include)

	core_win_32 {
		copyFile($$ROOT_GIT_DIR/core/DesktopEditor/doctrenderer/docbuilder.com/Win32/Release/docbuilder.com.dll, $$CUR_ROOT/docbuilder.com.dll)
	}
	core_win_64 {
		copyFile($$ROOT_GIT_DIR/core/DesktopEditor/doctrenderer/docbuilder.com/x64/Release/docbuilder.com.dll, $$CUR_ROOT/docbuilder.com.dll)
	}

}
