if not defined OO_VS_DIR (
	SET "OO_VS_DIR=%ProgramFiles(x86)%\Microsoft Visual Studio 14.0\VC"
)

setlocal enabledelayedexpansion

call %~dp0scripts\json_value.bat module    OO_MODULE     "desktop builder"
call %~dp0scripts\json_value.bat update    OO_UPDATE     1
call %~dp0scripts\json_value.bat clean     OO_CLEAN      0
call %~dp0scripts\json_value.bat platform  OO_PLATFORM   native
call %~dp0scripts\json_value.bat config    OO_CONFIG     no_vlc
call %~dp0scripts\json_value.bat deploy    OO_DEPLOY     1
call %~dp0scripts\json_value.bat install   OO_INSTALL    1

if "%OO_UPDATE%"=="1" (
	call scripts\git-fetch.bat core
	call scripts\git-fetch.bat desktop-sdk
	call scripts\git-fetch.bat sdkjs
	call scripts\git-fetch.bat sdkjs-plugins
	call scripts\git-fetch.bat web-apps-pro
	call scripts\git-fetch.bat dictionaries
	call scripts\git-fetch.bat DocumentBuilder
	
	if not "%OO_MODULE%"=="%OO_MODULE:desktop=%" (
		call scripts\git-fetch.bat desktop-apps
		
		set "OO_CONFIG=%OO_CONFIG% desktop"
	)	
)

set "BUILD_PLATFORM=%OO_PLATFORM%"
call ../core/Common/3dParty/make.bat

cd %~dp0

set "CONFIG_ADDON=updmodule"

set "IS_NEED_NATIVE=true"

if not "%OO_PLATFORM%"=="%OO_PLATFORM:all=%" (

	cd %~dp0
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_64"
	)
	call nmake -f "makefiles\build.makefile_win_64"
	del ".qmake.stash"

	cd %~dp0
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_32"
	)
	call nmake -f "makefiles\build.makefile_win_32"
	del ".qmake.stash"

	set "IS_NEED_NATIVE=false"

)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:xp=%" (

	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_64_xp"
	)
	call nmake -f "makefiles\build.makefile_win_64_xp"
	del ".qmake.stash"

	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_32_xp"
	)
	call nmake -f "makefiles\build.makefile_win_32_xp"
	del ".qmake.stash"
	
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:native=%" (

	if "%IS_NEED_NATIVE%"=="true" (

		if exist "%PROGRAMFILES(X86)%" (
			call "%OO_VS_DIR%\vcvarsall.bat" x64
			set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
			set "OS_DEPLOY=win_64"
			call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
			if "%OO_CLEAN%"=="1" (
				call nmake clean -f "makefiles\build.makefile_win_64"
			)
			call nmake -f "makefiles\build.makefile_win_64"
			del ".qmake.stash"
		) else (
			call "%OO_VS_DIR%\vcvarsall.bat" x86
			set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
			set "OS_DEPLOY=win_32"
			call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml
			if "%OO_CLEAN%"=="1" (
				call nmake clean -f "makefiles\build.makefile_win_32"
			)
			call nmake -f "makefiles\build.makefile_win_32"
			del ".qmake.stash"
		)

	)

)

if not "%OO_NO_BUILD_JS%"=="%OO_NO_BUILD_JS:1=%" (
	call "%OO_QT_DIR%\msvc2015_64\bin\qmake" -nocache %~dp0scripts\build_js.pro "CONFIG+=%OO_MODULE%"
)

if "%OO_DEPLOY%"=="1" (
	call scripts\deploy.bat
)

endlocal
