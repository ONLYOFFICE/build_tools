echo TODO: DEPLOY SCRIPT

call %~dp0json_value.bat module    OO_MODULE     "desktop builder"

cd %~dp0..

if exist "%PROGRAMFILES(X86)%" (
	set OS_CURRENT=win_64
) else (
	set OS_CURRENT=win_32
)

call "%OO_QT_DIR%\qmake" -nocache %~dp0deploy.pro "CONFIG+=%OO_CONFIG% %OO_MODULE%"