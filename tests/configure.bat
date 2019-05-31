call %~dp0..\configure.bat ^
 --module "desktop builder tests updmodule"^
 --platform native^
 --branding default^
 --update 1^
 --branch release/v5.3.0^
 --clean 1^
 --config no_vlc^
 --deploy^
 --install