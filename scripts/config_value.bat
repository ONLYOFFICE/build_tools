@echo off

setlocal enabledelayedexpansion
set key=%~1

set "returnvalue=%~3"
for /f "tokens=1,2 delims==" %%i in (config) do (
	set keyL=%%i
	set valueL=%%j
	
	if "%key%"=="!keyL!" (
		set "returnvalue=!valueL:~1,-1!"
		goto :end
	)
)

:end
endlocal & set "%~2=%returnvalue%"

@echo on
