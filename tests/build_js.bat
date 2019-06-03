setlocal

call %~dp0scripts\config_value.bat qt-dir     OO_QT_DIR     "set qt path"
call %~dp0..\scripts\json_value.bat module    OO_MODULE     "desktop builder"
call "%OO_QT_DIR%\msvc2015_64\bin\qmake" -nocache %~dp0..\scripts\build_js.pro "CONFIG+=%OO_MODULE%"

endlocal


