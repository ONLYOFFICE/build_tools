setlocal

set REPO_NAME=%1
set REPO_LOCAL_DIR=%~dp0..\..

call %~dp0json_value.bat branch OO_BRANCH master

SET LOCAL_CD=%cd%
cd %REPO_LOCAL_DIR%

if not exist "%REPO_NAME%" (
	call git clone "https://github.com/ONLYOFFICE/%REPO_NAME%.git"
)

call git checkout -f %OO_BRANCH%
call git -C "%REPO_NAME%" pull

cd "%LOCAL_CD%"

endlocal
