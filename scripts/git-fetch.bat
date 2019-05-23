setlocal

set REPO_NAME=%1
set REPO_LOCAL_DIR=%~dp0..\..

call %~dp0json_value.bat branch OO_BRANCH master

SET LOCAL_CD=%cd%
cd %REPO_LOCAL_DIR%

if not exist "%REPO_NAME%" (
	call git clone "https://github.com/ONLYOFFICE/%REPO_NAME%.git"
)

cd "%REPO_NAME%"
call git checkout -f %OO_BRANCH%
call git pull

cd "%LOCAL_CD%"

endlocal
