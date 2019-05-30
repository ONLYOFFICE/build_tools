set OO_QT_DIR=C:\Qt510\5.10.1

call %~dp0..\scripts\json_value.bat module    OO_MODULE     "desktop builder"

call "%OO_QT_DIR%\msvc2015_64\bin\qmake" -nocache %~dp0..\scripts\build_js.pro "CONFIG+=%OO_MODULE%"


