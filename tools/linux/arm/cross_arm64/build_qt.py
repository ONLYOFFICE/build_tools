#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')

import base

# return data for cross_file (meson)
def get_cross_file_glib_data(arm_toolchain_path) -> str:
  arm_toolchain_bin = arm_toolchain_path + "/bin/"
  arm_toolchain_prefix = "aarch64-linux-gnu-"
  
  cross_file_data = ""
  cross_file_data += "[host_machine]\n"
  cross_file_data += "system = 'linux'\n"
  cross_file_data += "cpu_family = 'aarch64'\n"
  cross_file_data += "cpu = 'aarch64'\n"
  cross_file_data += "endian = 'little'\n"
  cross_file_data += "[properties]\n"
  cross_file_data += "c_args = []\n"
  cross_file_data += "c_link_args = []\n"
  cross_file_data += "[binaries]\n"
  cross_file_data += "c = '" + arm_toolchain_bin + arm_toolchain_prefix + "gcc'\n"
  cross_file_data += "cpp = '" + arm_toolchain_bin + arm_toolchain_prefix +"g++'\n"
  cross_file_data += "ar = '" + arm_toolchain_bin + arm_toolchain_prefix + "ar'\n"
  cross_file_data += "ld = '" + arm_toolchain_bin + arm_toolchain_prefix + "ld'\n"
  cross_file_data += "objcopy = '" + arm_toolchain_bin + arm_toolchain_prefix + "/objcopy'\n"
  cross_file_data += "strip = '" + arm_toolchain_bin + arm_toolchain_prefix + "strip'\n"
  return cross_file_data
  
# return builded glib
def build_glib(arm_toolchain_path) -> str:
  curr_dir = os.path.abspath(os.curdir)
  build_path = os.path.abspath("./glib-build")
  install_path = os.path.abspath("./glib-install")
  glib_path = os.path.abspath("./glib")
  
  if base.is_dir(install_path):
    return install_path
  
  if not base.is_dir("./glib"):
    base.cmd("git clone " + "https://gitlab.gnome.org/GNOME/glib.git")
    
  base.cmd_in_dir("glib", "git checkout 2.82.2")
  
  if not base.is_dir(build_path):
    base.cmd("mkdir " + build_path)
    
  os.chdir(build_path)
  
  cross_filename = "cross_file.txt"
  cross_file_data = get_cross_file_glib_data(arm_toolchain_path)
  base.writeFile(cross_filename, cross_file_data)
  
  base.cmd("pip install meson")
  base.cmd("meson setup " + glib_path + " -Dbuildtype=release --prefix " + install_path + " --cross-file " + cross_filename)
  base.cmd("meson compile")
  base.cmd("meson install")
  
  os.chdir(curr_dir)
  
  return install_path
  
def update_qmake_conf(arm_toolchain_path):
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
  
  base.replaceInFile(replace_file, replace_src, replace_dst)

def make(arm_toolchain_path="", arm_sysroot_path=""):
  arm_toolchain_path = os.path.abspath(arm_toolchain_path)
  arm_sysroot_path = os.path.abspath(arm_sysroot_path)
  
  glib_install_path = build_glib(arm_toolchain_path)
  glib_lib = glib_install_path + "/lib"
  glib_include = glib_install_path + "/include"

  
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
 #   "-xcb",
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
    "-sysroot " + arm_sysroot_path,
    "-L " + glib_lib,
    "-I " + glib_include]
  
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
    
  if arm_toolchain_path != "":
    update_qmake_conf(arm_toolchain_path)

  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "./configure " + qt_params_str)
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make -j4")
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make install")
  
if __name__ == "__main__":
  arm_toolchain_path = "./gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu"
  arm_sysroot_path = "./sysroot-glibc-linaro-2.21-2017.05-aarch64-linux-gnu"

  if len(sys.argv) >= 3:
    arm_toolchain_path = sys.argv[1]
    arm_sysroot_path = sys.argv[2]
    
  make(arm_toolchain_path, arm_sysroot_path)
