#!/usr/bin/env bash
set -x

BUILD_BINARIES="true"

build_oo_binaries() {

  _OUT_FOLDER=out
  _QT_FOLDER="tools/linux/qt_build"
  _PRODUCT_VERSION=8.1.3
  _BUILD_NUMBER=3
  _TAG_SUFFIX=-raven

  _GIT_CLONE_BRANCH="v${_PRODUCT_VERSION}.${_BUILD_NUMBER}${_TAG_SUFFIX}"
  _GIT_CLONE_BRANCH_OO="v${_PRODUCT_VERSION}.${_BUILD_NUMBER}"

  mkdir ${_OUT_FOLDER}
  docker build --tag onlyoffice-document-editors-builder .
  docker run -e PRODUCT_VERSION=${_PRODUCT_VERSION} \
  -e BUILD_NUMBER=${_BUILD_NUMBER} \
  -e NODE_ENV='production' \
  -v $(pwd)/${_QT_FOLDER}:/build_tools/tools/linux/qt_build \
  -v $(pwd)/${_OUT_FOLDER}:/build_tools/out \
  onlyoffice-document-editors-builder \
  /bin/bash -c 'cd tools/linux && python3 ./built_qt.py && python ./automate.py --branch=tags/'"${_GIT_CLONE_BRANCH}"
  cd ..

}

if [ "${BUILD_BINARIES}" == "true" ] ; then
  build_oo_binaries "out" "${PRODUCT_VERSION}" "${BUILD_NUMBER}"
  build_oo_binaries_exit_value=$?
fi
