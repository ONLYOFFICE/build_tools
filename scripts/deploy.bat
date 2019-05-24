setlocal

call %~dp0json_value.bat module    OO_MODULE     "desktop builder"
call %~dp0json_value.bat platform  OO_PLATFORM   "native"

cd %~dp0..

set "IS_NEED_NATIVE=true"

if not "%OO_PLATFORM%"=="%OO_PLATFORM:all=%" (

	set "QT_DEPLOY=%OO_QT_DIR%"

	set "OS_DEPLOY=win_64"
	call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	set "OS_DEPLOY=win_32"
	call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	set "IS_NEED_NATIVE=false"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:xp=%" (

	set "QT_DEPLOY=%OO_QT_XP_DIR%"

	set "OS_DEPLOY=win_64"
	call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% xp"

	set "OS_DEPLOY=win_32"
	call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% xp"
	
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:native=%" (

	if "%IS_NEED_NATIVE%"=="true" (

		if exist "%PROGRAMFILES(X86)%" (
			set "OS_DEPLOY=win_64"
		) else (
			set "OS_DEPLOY=win_32"
		)

		set "QT_DEPLOY=%OO_QT_DIR%"
		call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	)

)

endlocal