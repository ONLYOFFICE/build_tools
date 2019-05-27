setlocal

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
	call scripts\git-fetch.bat web-apps-pro
	call scripts\git-fetch.bat dictionaries
	call scripts\git-fetch.bat DocumentBuilder
	
	if not "%OO_MODULE%"=="%OO_MODULE:desktop=%" (
		call scripts\git-fetch.bat desktop-apps
		
		set "OO_CONFIG=%OO_CONFIG% desktop"
	)
)

call ../core/Common/3dParty/make.bat

cd %~dp0

call "%OO_VS_DIR%\vcvarsall.bat" amd64
call "%OO_QT_DIR%\qmake" -nocache build.pro "CONFIG+=%OO_CONFIG%"

if "%OO_CLEAN%"=="1" (
	call nmake clean -f "makefiles/build.makefile"
)
call nmake -f "makefiles/build.makefile"

call "%OO_QT_DIR%\qmake" -nocache scripts\build_js.pro "CONFIG+=%OO_MODULE%"

if %OO_DEPLOY%=="1" (
	call scripts\deploy.bat
)
if %OO_INSTALL%=="1" (
	call scripts\install.bat
)

endlocal
