#!/bin/bash

#######################################################################
# OnlyOffice Deb Builder

# Copyright (C) 2024 BTACTIC, SCCL

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

usage() {
cat <<EOF

  $0
  Copyright BTACTIC, SCCL
  Licensed under the GNU PUBLIC LICENSE 3.0

  Usage: $0 --product-version=PRODUCT_VERSION --build-number=BUILD_NUMBER 
  Example: $0 --product-version=7.4.1 --build-number=36 

EOF

}


# Check the arguments.
for option in "$@"; do
  case "$option" in
    -h | --help)
      usage
      exit 0
    ;;
    --product-version=*)
      PRODUCT_VERSION=`echo "$option" | sed 's/--product-version=//'`
    ;;
    --build-number=*)
      BUILD_NUMBER=`echo "$option" | sed 's/--build-number=//'`
    ;;
  esac
done


if [ "x${PRODUCT_VERSION}" == "x" ] ; then
    cat << EOF
    --product-version option must be informed.
    Aborting...
EOF
    usage
    exit 1
fi

if [ "x${BUILD_NUMBER}" == "x" ] ; then
    cat << EOF
    --build-number option must be informed.
    Aborting...
EOF
    usage
    exit 1
fi

build_deb() {

  build_deb_pre_pwd="$(pwd)"
  DOCUMENT_SERVER_PACKAGE_PATH="$(pwd)/document-server-package"

  _PRODUCT_VERSION=$1 # 7.4.1
  _BUILD_NUMBER=$2 # 36
  _TAG_SUFFIX=-raven
  _DEBIAN_PACKAGE_SUFFIX=-raven

  _GIT_CLONE_BRANCH="v${_PRODUCT_VERSION}.${_BUILD_NUMBER}${_TAG_SUFFIX}"

  # TODO: These requirements should be moved to Dockerfile
  # apt install build-essential m4 npm
  # npm install -g pkg

  git clone https://github.com/jefriabdullah/document-server-package.git -b ${_GIT_CLONE_BRANCH}
  # Ignore DETACHED warnings
  # Workaround for installing dependencies - BEGIN
  cd ${DOCUMENT_SERVER_PACKAGE_PATH}

  cat << EOF >> Makefile

deb_dependencies: \$(DEB_DEPS)

EOF

  PRODUCT_VERSION="${_PRODUCT_VERSION}" BUILD_NUMBER="${_BUILD_NUMBER}${_DEBIAN_PACKAGE_SUFFIX}" make deb_dependencies
  cd ${DOCUMENT_SERVER_PACKAGE_PATH}/deb/build
  apt-get -qq build-dep -y ./
  # Workaround for installing dependencies - END

  cd ${DOCUMENT_SERVER_PACKAGE_PATH}
  PRODUCT_VERSION="${_PRODUCT_VERSION}" BUILD_NUMBER="${_BUILD_NUMBER}${_DEBIAN_PACKAGE_SUFFIX}" make deb

  cd ${build_deb_pre_pwd}

}

build_deb "${PRODUCT_VERSION}" "${BUILD_NUMBER}" "${DEBIAN_PACKAGE_SUFFIX}"
