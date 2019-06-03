@echo off

setlocal enabledelayedexpansion

if exist config del /F config

:loop

set local1=%~1
set local2=%~2

if "%local1%"=="" (
	GOTO :end
)

set local1=%~1TEST

if not "%local1:~0,2%"=="--" (
	SHIFT
	GOTO :loop
)

if "%local2:~0,2%"=="--" (
	echo %local1:~2,-4%=^"1^">> config
	SHIFT
	GOTO :loop
)

if "%local2%"=="" (
	echo %local1:~2,-4%=^"1^">> config
	GOTO :end
)

SHIFT
SHIFT

echo %local1:~2,-4%=^"%local2%^">> config

GOTO :loop

:end

endlocal

@echo on