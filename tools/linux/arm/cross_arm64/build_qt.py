#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')

import base

def update_qmake_conf(arm_toolchain_bin):
  replace_file = "./qt-everywhere-src-5.15.2/qtbase/mkspecs/linux-aarch64-gnu-g++/qmake.conf"
  arm_toolchain_bin = os.path.abspath(arm_toolchain_bin)
  
  replace_src = ""
  replace_src += "# modifications to g++.conf\n"
  replace_src += "QMAKE_CC                = aarch64-linux-gnu-gcc\n"
  replace_src += "QMAKE_CXX               = aarch64-linux-gnu-g++\n"
  replace_src += "QMAKE_LINK              = aarch64-linux-gnu-g++\n"
  replace_src += "QMAKE_LINK_SHLIB        = aarch64-linux-gnu-g++\n"
  replace_src += "\n"
  replace_src += "# modifications to linux.conf\n"
  replace_src += "QMAKE_AR                = aarch64-linux-gnu-ar cqs\n"
  replace_src += "QMAKE_OBJCOPY           = aarch64-linux-gnu-objcopy\n"
  replace_src += "QMAKE_NM                = aarch64-linux-gnu-nm -P\n"
  replace_src += "QMAKE_STRIP             = aarch64-linux-gnu-strip\n"
  
  replace_dst = ""
  replace_dst += "# modifications to g++.conf\n"
  replace_dst += "QMAKE_CC                = " + arm_toolchain_bin + "/aarch64-linux-gnu-gcc\n"
  replace_dst += "QMAKE_CXX               = " + arm_toolchain_bin + "/aarch64-linux-gnu-g++\n"
  replace_dst += "QMAKE_LINK              = " + arm_toolchain_bin + "/aarch64-linux-gnu-g++\n"
  replace_dst += "QMAKE_LINK_SHLIB        = " + arm_toolchain_bin + "/aarch64-linux-gnu-g++\n"
  replace_dst += "\n"
  replace_dst += "# modifications to linux.conf\n"
  replace_dst += "QMAKE_AR                = " + arm_toolchain_bin + "/aarch64-linux-gnu-ar cqs\n"
  replace_dst += "QMAKE_OBJCOPY           = " + arm_toolchain_bin + "/aarch64-linux-gnu-objcopy\n"
  replace_dst += "QMAKE_NM                = " + arm_toolchain_bin + "/aarch64-linux-gnu-nm -P\n"
  replace_dst += "QMAKE_STRIP             = " + arm_toolchain_bin + "/aarch64-linux-gnu-strip\n"
  
  base.replaceInFile(replace_file, replace_src, replace_dst)

def make(arm_toolchain_bin=""):
  qt_build_path = os.path.dirname(os.path.abspath(__file__)) + "/qt_build/Qt-5.15.2/linux_arm64"
  qt_params = ["-opensource",
    "-confirm-license",
    "-release",
    "-shared",
    "-accessibility",
    "-prefix", "\"" + qt_build_path + "\"",
    "-extprefix", "\"" + qt_build_path + "\"",
    "-hostprefix", "\"" + qt_build_path + "\"",
    "-c++std", "c++11",
    "-qt-zlib",
    "-qt-libpng",
    "-qt-libjpeg",
    "-qt-pcre",
    "-no-sql-sqlite",
    "-no-opengl",
    "-nomake", "examples",
    "-nomake", "tests",
    "-skip", "qtlocation",
    "-skip", "qtserialport",
    "-skip", "qtsensors",
    "-skip", "qtxmlpatterns",
    "-skip", "qt3d",
    "-skip", "qtwebview",
    "-skip", "qtwebengine",
    "-skip", "qtdeclarative",
    "-xplatform", "linux-aarch64-gnu-g++", # be sure that aarch64 gnu compiler is installed
    "-no-pch"]

  qt_params_str = ""
  for param in qt_params:
      qt_params_str += (param + " ")

  qt_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/qt/qt-everywhere-src-5.15.2.tar.xz"
  if not base.is_file("./qt_source_5.15.2.tar.xz"):
    base.download(qt_url, "./qt_source_5.15.2.tar.xz")
  
  if not base.is_dir("./qt-everywhere-src-5.15.2"):
    base.cmd("tar", ["-xf", "./qt_source_5.15.2.tar.xz"])
    
  # https://bugreports.qt.io/browse/QTBUG-93452
  # for GCC 11 and Qt5/Qt6
  additional_gcc_11 = "#ifdef __cplusplus\n#include <limits>\n#endif\n"
  chanage_file = "./qt-everywhere-src-5.15.2/qtbase/src/corelib/global/qglobal.h"
  filedata = base.readFile(chanage_file)
  if filedata.find(additional_gcc_11) == -1:
    filedata = additional_gcc_11 + filedata
    base.writeFile(chanage_file, filedata)
    
  if arm_toolchain_bin != "":
    update_qmake_conf(arm_toolchain_bin)

  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "./configure " + qt_params_str)
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make -j4")
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make install")
  
if __name__ == "__main__":
  arm_toolchain_path = "./gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu/bin"
  if len(sys.argv) != 1:
    arm_toolchain_path = sys.argv[1]
    
  make(arm_toolchain_path)
