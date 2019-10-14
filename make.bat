
setlocal enabledelayedexpansion

SET "OO_VS_DIR=%ProgramFiles%\Microsoft Visual Studio 14.0\VC"
if defined ProgramFiles(x86) (
	SET "OO_VS_DIR=%ProgramFiles(x86)%\Microsoft Visual Studio 14.0\VC"
)

call %~dp0scripts\config_value.bat update        OO_UPDATE     1
call %~dp0scripts\config_value.bat branch        OO_BRANCH     master
if "%OO_UPDATE%"=="true" (
	set "OO_UPDATE=1"
)

rem ############################ BRANDING #############################
call %~dp0scripts\config_value.bat branding        OO_BRANDING_NAME    ""
call %~dp0scripts\config_value.bat branding-url    OO_BRANDING_URL     ""

if "%OO_RUNNING_BRANDING%" == "1" (
	goto :base
)
if "%OO_BRANDING_NAME%" == "" (
	goto :base
)

if not exist "%OO_BRANDING_NAME%" (
	call git clone "%OO_BRANDING_URL%" "../%OO_BRANDING_NAME%"
)
if "%OO_UPDATE%"=="1" (
	cd "..\%OO_BRANDING_NAME%"
	call git fetch
	call git checkout -f %OO_BRANCH%
	call git pull
	cd "..\build_tools"
)

if exist "..\%OO_BRANDING_NAME%\build_tools\make.bat" (
	set "OO_RUNNING_BRANDING=1"
	set "BRANDING_PATH=%~dp0..\%OO_BRANDING_NAME%"
	cd "..\%OO_BRANDING_NAME%\build_tools"
	call make.bat
	exit /b 0
)

:base
rem ###################################################################

call %~dp0scripts\config_value.bat module        OO_MODULE     "desktop builder"
call %~dp0scripts\config_value.bat update        OO_UPDATE     1
call %~dp0scripts\config_value.bat clean         OO_CLEAN      0
call %~dp0scripts\config_value.bat platform      OO_PLATFORM   native
call %~dp0scripts\config_value.bat config        OO_CONFIG     no_vlc
call %~dp0scripts\config_value.bat deploy        OO_DEPLOY     1
call %~dp0scripts\config_value.bat install       OO_INSTALL    1
call %~dp0scripts\config_value.bat qt-dir        OO_QT_DIR     "set qt path"
call %~dp0scripts\config_value.bat qt-dir-xp     OO_QT_XP_DIR  "set qt path (windows xp version)"
call %~dp0scripts\config_value.bat themesparams  OO_THEMES_PARAMS ""

if "%OO_CLEAN%"=="true" (
	set "OO_CLEAN=1"
)

if "%OO_DEPLOY%"=="true" (
	set "OO_DEPLOY=1"
)

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

set "IS_NEED_64=0"
set "IS_NEED_32=0"
set "IS_NEED_XP_64=0"
set "IS_NEED_XP_32=0"

if not "%OO_PLATFORM%"=="%OO_PLATFORM:win_64_xp=%" (
	set "IS_NEED_XP_64=1"
	set "OO_PLATFORM=%OO_PLATFORM:win_64_xp=%"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:win_32_xp=%" (
	set "IS_NEED_XP_32=1"
	set "OO_PLATFORM=%OO_PLATFORM:win_32_xp=%"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:xp=%" (
	set "IS_NEED_XP_64=1"
	set "IS_NEED_XP_32=1"
	set "OO_PLATFORM=%OO_PLATFORM:xp=%"
)

if "%OO_PLATFORM%"=="" (
	set "OO_PLATFORM=empty"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:all=%" (
	set "IS_NEED_64=1"
	set "IS_NEED_32=1"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:x64=%" (
	set "IS_NEED_64=1"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:win_64=%" (
	set "IS_NEED_64=1"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:x86=%" (
	set "IS_NEED_32=1"
)
if not "%OO_PLATFORM%"=="%OO_PLATFORM:win_32=%" (
	set "IS_NEED_32=1"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:native=%" (
	if exist "%PROGRAMFILES(X86)%" (
		set "IS_NEED_64=1"
	) else (
		set "IS_NEED_32=1"
	)
)

if not exist "%OO_QT_DIR%\msvc2015_64\bin\qmake.exe" (
	set "IS_NEED_64=0"
)
if not exist "%OO_QT_DIR%\msvc2015\bin\qmake.exe" (
	set "IS_NEED_32=0"
)
if not exist "%OO_QT_XP_DIR%\msvc2015_64\bin\qmake.exe" (
	set "IS_NEED_XP_64=0"
)
if not exist "%OO_QT_XP_DIR%\msvc2015\bin\qmake.exe" (
	set "IS_NEED_XP_32=0"
)

set "QMAKE_FOR_SCRIPTS=%OO_QT_DIR%\msvc2015_64\bin\qmake.exe"
if not exist "%QMAKE_FOR_SCRIPTS%" (
	"QMAKE_FOR_SCRIPTS=%OO_QT_DIR%\msvc2015\bin\qmake.exe"
)
if not exist "%QMAKE_FOR_SCRIPTS%" (
	"QMAKE_FOR_SCRIPTS=%OO_QT_XP_DIR%\msvc2015_64\bin\qmake.exe"
)
if not exist "%QMAKE_FOR_SCRIPTS%" (
	"QMAKE_FOR_SCRIPTS=%OO_QT_XP_DIR%\msvc2015\bin\qmake.exe"
)

set "BUILD_PLATFORM=%OO_PLATFORM%"
if "%IS_NEED_64%"=="1" (
	set "BUILD_PLATFORM=all"
) else (
	if "%IS_NEED_32%"=="1" (
		set "BUILD_PLATFORM=all"
	)
)
if "%IS_NEED_XP_64%"=="1" (
	set "BUILD_PLATFORM=%BUILD_PLATFORM% xp"
) else (
	if "%IS_NEED_XP_32%"=="1" (
		set "BUILD_PLATFORM=%BUILD_PLATFORM% xp"
	)
)

call ../core/Common/3dParty/make.bat || goto :error

cd %~dp0

if not "%OO_MODULE%"=="%OO_MODULE:updmodule=%" (
	set "CONFIG_ADDON=updmodule"
	set "QMAKE_ADDON=LINK=https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.xml"

	if not exist tools\WinSparkle-0.7.0.zip (
		call tools\win\curl\curl.exe "https://d2ettrnqo7v976.cloudfront.net/winsparkle/WinSparkle-0.7.0.zip" --output tools\WinSparkle-0.7.0.zip
	)

	if not exist tools\WinSparkle-0.7.0 (
		call tools\win\7z\7z.exe x tools\WinSparkle-0.7.0.zip -otools
	)

	if not exist "..\desktop-apps\win-linux\3dparty" (
		mkdir "..\desktop-apps\win-linux\3dparty"
	)
	if not exist "..\desktop-apps\win-linux\3dparty\WinSparkle" (
		mkdir "..\desktop-apps\win-linux\3dparty\WinSparkle"
	)
	if not exist "..\desktop-apps\win-linux\3dparty\WinSparkle\include" (
		xcopy /s /q /y /i "tools\WinSparkle-0.7.0\include" "..\desktop-apps\win-linux\3dparty\WinSparkle\include"
	)

	xcopy /s /q /y /i "tools\WinSparkle-0.7.0\Release" "..\desktop-apps\win-linux\3dparty\WinSparkle\win_32"
	xcopy /s /q /y /i "tools\WinSparkle-0.7.0\x64\Release" "..\desktop-apps\win-linux\3dparty\WinSparkle\win_64"	
)

cd %~dp0

set "CURRENT_PATH=%PATH%"
cd %~dp0
if "%IS_NEED_64%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"

	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_64"
		call nmake distclean -f "makefiles\build.makefile_win_64"
	)

	call "!QT_DEPLOY!\qmake" -nocache %~dp0build_clean.pro
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" "%QMAKE_ADDON%" || goto :error
	call nmake -f "makefiles\build.makefile_win_64" || goto :error

	del ".qmake.stash"
)

set "PATH=%CURRENT_PATH%"
cd %~dp0
if "%IS_NEED_32%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"

	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_32"
		call nmake distclean -f "makefiles\build.makefile_win_32"
	)

	call "!QT_DEPLOY!\qmake" -nocache %~dp0build_clean.pro
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% %CONFIG_ADDON%" "%QMAKE_ADDON%" || goto :error
	call nmake -f "makefiles\build.makefile_win_32" || goto :error
	
	del ".qmake.stash"
)

set "PATH=%CURRENT_PATH%"
cd %~dp0
if "%IS_NEED_XP_64%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"

	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_64_xp"
		call nmake distclean -f "makefiles\build.makefile_win_64_xp"
	)

	call "!QT_DEPLOY!\qmake" -nocache %~dp0build_clean.pro "CONFIG+=build_xp"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp %CONFIG_ADDON%" "%QMAKE_ADDON%" || goto :error
	call nmake -f "makefiles\build.makefile_win_64_xp" || goto :error
	
	del ".qmake.stash"
)

set "PATH=%CURRENT_PATH%"
cd %~dp0
if "%IS_NEED_XP_32%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"

	if "%OO_CLEAN%"=="1" (
		call nmake clean -f "makefiles\build.makefile_win_32_xp"
		call nmake distclean -f "makefiles\build.makefile_win_32_xp"
	)

	call "!QT_DEPLOY!\qmake" -nocache %~dp0build_clean.pro "CONFIG+=build_xp"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0build.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp %CONFIG_ADDON%" "%QMAKE_ADDON%" || goto :error
	call nmake -f "makefiles\build.makefile_win_32_xp" || goto :error
	
	del ".qmake.stash"
)

if not "%OO_MODULE%"=="%OO_MODULE:builder=%" (
	call ..\core\DesktopEditor\doctrenderer\docbuilder.com\build.bat || goto :error
)

if "%OO_NO_BUILD_JS%"=="" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	call "%QMAKE_FOR_SCRIPTS%" -nocache %~dp0scripts\build_js.pro "CONFIG+=%OO_MODULE%"
)

if not "%OO_DEPLOY%"=="1" (
	GOTO :end
)

set "PATH=%CURRENT_PATH%"
if "%IS_NEED_64%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0scripts\deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"
)
set "PATH=%CURRENT_PATH%"
if "%IS_NEED_32%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0scripts\deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"
)
set "PATH=%CURRENT_PATH%"
if "%IS_NEED_XP_64%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0scripts\deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"
)
set "PATH=%CURRENT_PATH%"
if "%IS_NEED_XP_32%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0scripts\deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"
)

:end
endlocal
exit /b 0

:error
echo "Failed with error #%errorlevel%."
exit /b %errorlevel%
