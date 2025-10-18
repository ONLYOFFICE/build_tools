setlocal enabledelayedexpansion

set "script_dir=%~dp0"
set "config_file=%script_dir%..\..\..\config"
set "git_dir=%script_dir%..\..\..\..\

set "module_list="
set "branding_value="
set "themesparams="

for /f "delims=" %%a in ('type "%config_file%"') do (
    set "line=%%a"
    if "!line:~0,7!"=="module=" (
        set "module_list=!line:~7!"
        set "module_list=!module_list:"=!"
    )
    if "!line:~0,14!"=="branding-name=" (
        set "branding_value=!line:~14!"
        set "branding_value=!branding_value:"=!"
    )
	if "!line:~0,13!"=="themesparams=" (
        set "themesparams=!line:~13!"
        set "themesparams=!branding_value:"=!"
    )
)

if "!branding_value!"=="" (
    set "branding_value=onlyoffice"
)

set "base_out_dir=%script_dir%..\..\..\out\win_arm64\%branding_value%"

for %%m in (!module_list!) do (
	if "%%m"=="desktop" (
		call %base_out_dir%\DesktopEditors\converter\x2t.exe -create-js-snapshots
		call %base_out_dir%\DesktopEditors\converter\allfontsgen.exe --use-system="1" --input="%base_out_dir%\DesktopEditors\fonts" --input="%git_dir%\core-fonts" --allfonts="%base_out_dir%\DesktopEditors\converter\AllFonts.js" --selection="%base_out_dir%\DesktopEditors\converter\font_selection.bin"
		call %base_out_dir%\DesktopEditors\converter\allthemesgen.exe --converter-dir="%base_out_dir%\DesktopEditors\converter" --src="%base_out_dir%\DesktopEditors\editors\sdkjs\slide\themes" --allfonts="AllFonts.js" --output="%base_out_dir%\DesktopEditors\editors\sdkjs\common\Images" --params="%themesparams%"
		del %base_out_dir%\DesktopEditors\converter\allfontsgen.exe
		del %base_out_dir%\DesktopEditors\converter\allthemesgen.exe

	)
	if "%%m"=="server" (
		call %base_out_dir%\documentserver\server\FileConverter\bin\x2t -create-js-snapshots
	)
	if "%%m"=="builder" (
		call %base_out_dir%\DocumentBuilder\x2t -create-js-snapshots
	)
	if "%%m"=="core" (
		call %base_out_dir%\core\x2t -create-js-snapshots
	)
)
shutdown /s /f /t 10