call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build/vcvarsall.bat" x64
if exist .\makefiles\build.makefile_win_64 del /F .\makefiles\build.makefile_win_64
call "E:\Qt\Qt5.9.9\5.9.9/msvc2017_64/bin/qmake" -nocache build.pro "CONFIG+=builder server  "
set CL=/MP
call nmake -f makefiles/build.makefile_win_64