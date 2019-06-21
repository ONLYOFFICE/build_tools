setlocal

set REPO_NAME=%1
set REPO_LOCAL_DIR=%~dp0..\..

call %~dp0config_value.bat branch       OO_BRANCH master
call %~dp0config_value.bat git-protocol OO_GIT_PR https

SET LOCAL_CD=%cd%
cd %REPO_LOCAL_DIR%

SET "OO_REPO_URL=https://github.com/ONLYOFFICE/%REPO_NAME%.git"
if "%OO_GIT_PR%"=="ssh" (
	SET "OO_REPO_URL=git@github.com:ONLYOFFICE/%REPO_NAME%.git"
)

if not exist "%REPO_NAME%" (
	call git clone "%OO_REPO_URL%"
)

cd "%REPO_NAME%"
call git fetch
call git checkout -f %OO_BRANCH%
call git pull

cd "%LOCAL_CD%"

endlocal
