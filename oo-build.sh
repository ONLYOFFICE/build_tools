#!/usr/bin/env bash
set -x

#######################################################################
# OnlyOffice Package Builder

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

  Usage: $0 --binaries-only
  Example: $0 --deb-only


EOF

}

BINARIES_ONLY="false"
DEB_ONLY="false"

# Check the arguments.
for option in "$@"; do
  case "$option" in
    -h | --help)
      usage
      exit 0
    ;;
    --binaries-only)
      BINARIES_ONLY="true"
    ;;
    --deb-only)
      DEB_ONLY="true"
    ;;
  esac
done

BUILD_BINARIES="true"
BUILD_DEB="true"

if [ ${BINARIES_ONLY} == "true" ] ; then
  BUILD_BINARIES="true"
  BUILD_DEB="false"
fi

if [ ${DEB_ONLY} == "true" ] ; then
  BUILD_BINARIES="false"
  BUILD_DEB="true"
fi

  _PRODUCT_VERSION=8.1.3
  _BUILD_NUMBER=3

build_oo_binaries() {

  _OUT_FOLDER=$1
  _TAG_SUFFIX=-raven

  _GIT_CLONE_BRANCH="v${_PRODUCT_VERSION}.${_BUILD_NUMBER}${_TAG_SUFFIX}"
  _GIT_CLONE_BRANCH_OO="v${_PRODUCT_VERSION}.${_BUILD_NUMBER}"

  mkdir ${_OUT_FOLDER}
  docker build --tag onlyoffice-document-editors-builder .
  docker run -e PRODUCT_VERSION=${_PRODUCT_VERSION} \
  -e BUILD_NUMBER=${_BUILD_NUMBER} \
  -e NODE_ENV='production' \
   -v $(pwd)/${_OUT_FOLDER}:/root/build_tools/out \
   -v $(pwd):/root/build_tools \
   -v $(pwd)/../:/root \
  onlyoffice-document-editors-builder \
  /bin/bash -c 'cd /root/build_tools/tools/linux && python3 ./automate.py server --branch=tags/'"${_GIT_CLONE_BRANCH_OO}"
  cd ..

}

if [ "${BUILD_BINARIES}" == "true" ] ; then
  build_oo_binaries "out" "${PRODUCT_VERSION}" "${BUILD_NUMBER}"
  build_oo_binaries_exit_value=$?
fi

# Simulate that binaries build went ok
# when we only want to make the deb
if [ ${DEB_ONLY} == "true" ] ; then
  build_oo_binaries_exit_value=0
fi

if [ "${BUILD_DEB}" == "true" ] ; then
  if [ ${build_oo_binaries_exit_value} -eq 0 ] ; then
    #cd deb_build
    docker build --tag onlyoffice-deb-builder . -f ./deb_build/Dockerfile-deb-builder
    docker run \
      --env PRODUCT_VERSION=${_PRODUCT_VERSION} \
      --env BUILD_NUMBER=${_BUILD_NUMBER} \
      -v $(pwd)/deb_build:/root:rw \
      -v $(pwd)/../build_tools:/root/build_tools:ro \
      onlyoffice-deb-builder /bin/bash -c "/root/onlyoffice-deb-builder.sh --product-version ${_PRODUCT_VERSION} --build-number ${_BUILD_NUMBER}"
    cd ..
  else
    echo "Binaries build failed!"
    echo "Aborting... !"
    exit 1
  fi
fi