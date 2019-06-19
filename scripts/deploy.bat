setlocal enabledelayedexpansion

call %~dp0config_value.bat module    OO_MODULE     "desktop builder"
call %~dp0config_value.bat platform  OO_PLATFORM   "native"
call %~dp0config_value.bat qt-dir    OO_QT_DIR     "set qt path"
call %~dp0config_value.bat qt-dir-xp OO_QT_XP_DIR  "set qt path (windows xp version)"

SET "OO_VS_DIR=%ProgramFiles%\Microsoft Visual Studio 14.0\VC"
if defined ProgramFiles(x86) (
	SET "OO_VS_DIR=%ProgramFiles(x86)%\Microsoft Visual Studio 14.0\VC"
)

cd %~dp0..

set "IS_NEED_64=0"
set "IS_NEED_32=0"

if not "%OO_PLATFORM%"=="%OO_PLATFORM:all=%" (
	set "IS_NEED_64=1"
	set "IS_NEED_32=1"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:native=%" (
	if exist "%PROGRAMFILES(X86)%" (
		set "IS_NEED_64=1"
	) else (
		set "IS_NEED_32=1"
	)
)

if "%IS_NEED_64%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"
)
if "%IS_NEED_32%"=="1" (
	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"
)

if not "%OO_PLATFORM%"=="%OO_PLATFORM:xp=%" (

	call "%OO_VS_DIR%\vcvarsall.bat" x64
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015_64\bin"
	set "OS_DEPLOY=win_64"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"

	call "%OO_VS_DIR%\vcvarsall.bat" x86
	set "QT_DEPLOY=%OO_QT_XP_DIR%\msvc2015\bin"
	set "OS_DEPLOY=win_32"
	call "!QT_DEPLOY!\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE% build_xp"
	
)

endlocal