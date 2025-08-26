#!/usr/bin/env python

import sys
import os

import download_arm_toolchain
import download_arm_sysroot
sys.path.append('../../../../scripts')

import base
  
def update_qmake_conf(arm_toolchain_path, arm_sysroot_path):
  replace_file = "./qt-everywhere-src-5.15.2/qtbase/mkspecs/linux-aarch64-gnu-g++/qmake.conf"
  arm_toolchain_bin = arm_toolchain_path + "/bin"
  
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
  
  lflags = "-Wl,--disable-new-dtags "
  replace_dst += "QMAKE_LFLAGS            = " + lflags + "\n"
  
  base.replaceInFile(replace_file, replace_src, replace_dst)

def make(arm_toolchain_path="", arm_sysroot_path=""):
  arm_toolchain_path = os.path.abspath(arm_toolchain_path)
  arm_sysroot_path = os.path.abspath(arm_sysroot_path)
  
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
    "-glib",
    "-gstreamer", "1.0",
    "-xcb",
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
    "-no-pch",
    "-no-use-gold-linker",
    "-recheck-all",
    "-sysroot", "\"" + arm_sysroot_path + "\"",
    "-R", "\"" + arm_sysroot_path + "/lib/aarch64-linux-gnu" + "\"", 
    "-R", "\"" + arm_sysroot_path + "/usr/lib/aarch64-linux-gnu" + "\"", ]
  
  # test config.qtbase_corelib.libraries.glib FAILED
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
    
  if arm_toolchain_path != "" and arm_sysroot_path != "":
    update_qmake_conf(arm_toolchain_path, arm_sysroot_path)
    
  os.environ["PKG_CONFIG_LIBDIR"] = "\"" + arm_sysroot_path + "/usr/lib/aarch64-linux-gnu/pkgconfig" + "\""
  os.environ["PKG_CONFIG_PATH"] = "\"" + arm_sysroot_path + "/usr/lib/aarch64-linux-gnu/pkgconfig" + "\""

  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "./configure " + qt_params_str)
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make -j4")
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make install")
  
if __name__ == "__main__":
  arm_toolchain_path = "./arm_toolchain/gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu"
  arm_sysroot_path = "./arm_sysroot/sysroot-ubuntu16.04-arm64v8"

  if len(sys.argv) >= 3:
    arm_toolchain_path = sys.argv[1]
    arm_sysroot_path = sys.argv[2]
  else:
    if not base.is_dir(arm_toolchain_path):
      download_arm_toolchain.make()
    
    if not base.is_dir(arm_sysroot_path):
      download_arm_sysroot.make()
    
  make(arm_toolchain_path, arm_sysroot_path)
