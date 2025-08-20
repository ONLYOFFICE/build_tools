import sys
import os
sys.path.append('../../../../scripts')

import base

def make():
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
    "-no-qml-debug",
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

  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "./configure " + qt_params_str)
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make -j4")
  base.cmd_in_dir("./qt-everywhere-src-5.15.2", "make install")
  
if __name__ == "__main__":
  make()
