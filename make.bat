setlocal

call %~dp0scripts\json_value.bat module    OO_MODULE     "desktop builder"
call %~dp0scripts\json_value.bat update    OO_UPDATE     1
call %~dp0scripts\json_value.bat clean     OO_CLEAN      0
call %~dp0scripts\json_value.bat platform  OO_PLATFORM   native
call %~dp0scripts\json_value.bat config    OO_CONFIG     no_vlc
call %~dp0scripts\json_value.bat deploy    OO_DEPLOY     1
call %~dp0scripts\json_value.bat install   OO_INSTALL    1

set "ADDITIONAL_COMMAND="
if %OO_DEPLOY%=="1" ( set "ADDITIONAL_COMMAND=%ADDITIONAL_COMMAND% deploy" )
if %OO_INSTALL%=="1" ( set "ADDITIONAL_COMMAND=%ADDITIONAL_COMMAND% install" )

if "%OO_UPDATE%"=="1" (
	call scripts\git-fetch.bat core
	call scripts\git-fetch.bat desktop-sdk
	call scripts\git-fetch.bat sdkjs
	call scripts\git-fetch.bat web-apps-pro
	call scripts\git-fetch.bat dictionaries
	
	if not "%OO_MODULE%"=="%OO_MODULE:desktop=%" (
		call scripts\git-fetch.bat desktop-apps
		call scripts\git-fetch.bat desktop-apps-ext
		call scripts\git-fetch.bat core-ext
		
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
call nmake -f "makefiles/build.makefile" %ADDITIONAL_COMMAND%

endlocal
