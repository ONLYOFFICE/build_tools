setlocal

call %~dp0json_value.bat module    OO_MODULE     "desktop builder"
call %~dp0json_value.bat platform  OO_PLATFORM   "native"

cd %~dp0..

set "IS_NEED_NATIVE=true"

if not "%OO_PLATFORM%"=="%OO_PLATFORM:all=%" (

	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "%QT_DEPLOY%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "%QT_DEPLOY%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	set "IS_NEED_NATIVE=false"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:xp=%" (

	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "%QT_DEPLOY%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"

	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "%QT_DEPLOY%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"
	
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:native=%" (

	if "%IS_NEED_NATIVE%"=="true" (

		if exist "%PROGRAMFILES(X86)%" (
			set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
			set "OS_DEPLOY=win_64"
		) else (
			set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
			set "OS_DEPLOY=win_32"
		)

		call "%QT_DEPLOY%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"

	)

)

endlocal