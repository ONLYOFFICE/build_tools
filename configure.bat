@echo off

if exist config.json del /F config.json

echo {>> config.json

:loop

set local1=%~1
set local2=%~2

if "%local1%"=="" (
	GOTO :end
)

if not "%local1:~0,2%"=="--" (
	SHIFT
	GOTO :loop
)

if "%local2:~0,2%"=="--" (
	echo ^"%local1%^" : ^"1^",>> config.json
	SHIFT
	GOTO :loop
)

if "%local2%"=="" (
	echo ^"%local1%^" : ^"1^">> config.json
	GOTO :end
)

SHIFT
SHIFT

if "%~2"=="" (
	echo ^"%local1%^" : ^"%local2%^">> config.json
) else (
	echo ^"%local1%^" : ^"%local2%^",>> config.json
)

GOTO :loop

:end

echo }>> config.json

@echo on