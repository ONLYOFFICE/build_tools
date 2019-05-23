@echo off

set key=--%~1

setlocal
set "returnvalue=%~3"

for /f "usebackq tokens=1* delims={}:" %%a in ("config.json") do (
	for %%c in (%%a) do for /f tokens^=1^,2^ delims^=^"^:^} %%d in ("%%c") do (
		if "%key%"=="%%~d" (
			for %%c in (%%b) do for /f tokens^=1^,2^ delims^=^"^:^} %%d in ("%%c") do (
				set "returnvalue=%%~d"
				goto :end
			)
		)
	)
)

:end
endlocal & set "%~2=%returnvalue%"

@echo on