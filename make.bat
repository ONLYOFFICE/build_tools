setlocal

call %~dp0scripts\json_value.bat module    OO_MODULE     "desktop builder"
call %~dp0scripts\json_value.bat update    OO_UPDATE     1
call %~dp0scripts\json_value.bat clean     OO_CLEAN      0
call %~dp0scripts\json_value.bat platform  OO_PLATFORM   native
call %~dp0scripts\json_value.bat config    OO_CONFIG     no_vlc

if "%OO_UPDATE%"=="1" (
	call scripts\git-fetch.bat core
	call scripts\git-fetch.bat desktop-sdk
	call scripts\git-fetch.bat sdkjs
	call scripts\git-fetch.bat web-apps-pro
	
	if not "%OO_MODULE%"=="%OO_MODULE:desktop=%" (
		call scripts\git-fetch.bat desktop-apps
		call scripts\git-fetch.bat desktop-apps-pro
		call scripts\git-fetch.bat core-ext
		
		set "OO_CONFIG=%OO_CONFIG% desktop"
	)
)

call ../core/Common/3dParty/make.bat

call "%OO_VS_DIR%\vcvarsall.bat" amd64
call "%OO_QT_DIR%\qmake" -nocache build.pro "CONFIG+=%OO_CONFIG%"

if "%OO_CLEAN%"=="1" (
	call nmake clean -f "makefiles/build.makefile"
)
call nmake -f "makefiles/build.makefile"

endlocal
