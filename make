#!/bin/bash
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

OO_OS=$(uname -s)
OS_DEPLOY_64=""
case "$OO_OS" in
  Linux*)   OS_DEPLOY_64="linux_64" ;;
  Darwin*)  OS_DEPLOY_64="mac_64" ;; 
  *)        exit ;;
esac

source ./scripts/config_value update        OO_UPDATE 1
source ./scripts/config_value branch        OO_BRANCH master
if [ "$OO_UPDATE" == "true" ]
then
   OO_UPDATE=1
fi
############################ BRANDING #############################
source ./scripts/config_value branding      OO_BRANDING_NAME ""
source ./scripts/config_value branding-url  OO_BRANDING_URL ""

if [ "$OO_RUNNING_BRANDING" != "1" ]
then
if [ "$OO_BRANDING_NAME" != "" ]
then
if [ ! -d "./../$OO_BRANDING_NAME" ]
then
echo "clone branding ${OO_BRANDING_NAME}..."
git clone "$OO_BRANDING_URL" "../$OO_BRANDING_NAME"
fi
if [ "$OO_UPDATE" == "1" ]
then
echo "update branding ${OO_BRANDING_NAME}..."
cd "./../$OO_BRANDING_NAME"
git fetch
git checkout -f $OO_BRANCH
git pull
cd ../build_tools
fi
# run branding tools
if [ -f "../$OO_BRANDING_NAME/build_tools/make" ]
then
export OO_RUNNING_BRANDING="1"
export BRANDING_PATH="${SCRIPTPATH}/../${OO_BRANDING_NAME}"
cd "./../$OO_BRANDING_NAME/build_tools"
./make
exit 0
fi
fi
fi
###################################################################

if [[ "${OS_DEPLOY_64}" == "mac_64" ]]
then
  export PATH="${SCRIPTPATH}/tools/mac:${PATH}"
fi

source ./scripts/config_value module        OO_MODULE     "desktop builder"
source ./scripts/config_value clean         OO_CLEAN      0
source ./scripts/config_value platform      OO_PLATFORM   native
source ./scripts/config_value config        OO_CONFIG     no_vlc
source ./scripts/config_value deploy        OO_DEPLOY     1
source ./scripts/config_value qt-dir        OO_QT_DIR     "set qt path"
source ./scripts/config_value compiler      OO_COMPILER   gcc
source ./scripts/config_value no-apps       OO_NO_APPS    0
source ./scripts/config_value themesparams  OO_THEMES_PARAMS ""

if [ "$OO_CLEAN" == "true" ]
then
   OO_CLEAN=1
fi

if [ "$OO_DEPLOY" == "true" ]
then
   OO_DEPLOY=1
fi

OO_COMPILER_X64="${OO_COMPILER}_64"

if [ "$OO_UPDATE" == "1" ]
then
   ./scripts/git-fetch core
   ./scripts/git-fetch desktop-sdk
   ./scripts/git-fetch sdkjs
   ./scripts/git-fetch sdkjs-plugins
   ./scripts/git-fetch web-apps-pro
   ./scripts/git-fetch dictionaries
   ./scripts/git-fetch DocumentBuilder

   if [[ "$OO_MODULE" == *"desktop"* ]]
   then
      ./scripts/git-fetch desktop-apps
      OO_CONFIG="$OO_CONFIG desktop"
   fi
fi

BUILD_PLATFORM=$OO_PLATFORM

./../core/Common/3dParty/make.sh

IS_NEED_64=false
IS_NEED_32=false

if [[ "$OO_PLATFORM" == *"all"* ]]
then
IS_NEED_64=true
IS_NEED_32=true
fi

if [[ "$OO_PLATFORM" == *"x64"* ]] || \
   [[ "$OO_PLATFORM" == *"linux_64"* ]] || \
   [[ "$OO_PLATFORM" == *"mac_64"* ]]
then
IS_NEED_64=true
fi

if [[ "$OO_PLATFORM" == *"x86"* ]] || \
   [[ "$OO_PLATFORM" == *"linux_32"* ]]
then
IS_NEED_32=true
fi

if [[ "${OS_DEPLOY_64}" == "mac_64" ]]
then
  IS_NEED_32=false
fi

if [[ "$OO_PLATFORM" == *"native"* ]]
then
architecture=$(uname -m)
case "$architecture" in
  x86_64*)  IS_NEED_64=true ;;
  *)        IS_NEED_32=true ;;
esac
fi

if [[ "$IS_NEED_64" == true ]]
then
   export QT_DEPLOY="${OO_QT_DIR}/${OO_COMPILER_X64}/bin"
   export OS_DEPLOY="${OS_DEPLOY_64}"
   if [ "$OO_CLEAN" == "1" ]
   then
      make clean all -f "makefiles/build.makefile_${OS_DEPLOY_64}"
      make distclean -f "makefiles/build.makefile_${OS_DEPLOY_64}"
   fi
   "${QT_DEPLOY}/qmake" -nocache build_clean.pro
   "${QT_DEPLOY}/qmake" -nocache build.pro "CONFIG+=$OO_CONFIG $OO_MODULE"
   make -f "makefiles/build.makefile_${OS_DEPLOY_64}"
   rm ".qmake.stash"
fi

if [[ "$IS_NEED_32" == true ]]
then
   export QT_DEPLOY=${OO_QT_DIR}/${OO_COMPILER}/bin
   export OS_DEPLOY=linux_32
   if [ "$OO_CLEAN" == "1" ]
   then
      make clean all -f "makefiles/build.makefile_linux_32"
      make distclean -f "makefiles/build.makefile_linux_32"
   fi
   "${QT_DEPLOY}/qmake" -nocache build_clean.pro
   "${QT_DEPLOY}/qmake" -nocache build.pro "CONFIG+=$OO_CONFIG $OO_MODULE"
   make -f "makefiles/build.makefile_linux_32"
   rm ".qmake.stash"
fi

if [[ "${OS_DEPLOY_64}" == "mac_64" ]]
then
   xcodebuild -project "../desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore/ascdocumentscore.xcodeproj" -target "ascdocumentscore" -configuration Release
   xcodebuild -project "../desktop-sdk/ChromiumBasedEditors/lib/ascdocumentscore Helper/ONLYOFFICE Helper.xcodeproj" -target "ONLYOFFICE Helper" -configuration Release
fi

cd "$SCRIPTPATH"
if [[ "$OO_NO_BUILD_JS" == "1" ]]
then
   echo "no build js!!!"
else
   "${OO_QT_DIR}/${OO_COMPILER_X64}/bin/qmake" -nocache ./scripts/build_js.pro "CONFIG+=$OO_MODULE"
fi

if [[ "$OO_DEPLOY" == "1" ]]
then
   ./scripts/deploy
fi
