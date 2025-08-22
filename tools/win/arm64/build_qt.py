import sys
import os
sys.path.append('../../../scripts')

import base

def get_vs_path(version = "2019"):
  vs_path = ""
  programFilesDir = base.get_env("ProgramFiles")
  if ("" != base.get_env("ProgramFiles(x86)")):
    programFilesDir = base.get_env("ProgramFiles(x86)")
  if ("2015" == version):
      vs_path = programFilesDir + "/Microsoft Visual Studio 14.0/VC"
  elif ("2019" == version):
    if base.is_dir(programFilesDir + "/Microsoft Visual Studio/2019/Enterprise/VC/Auxiliary/Build"):
      vs_path = programFilesDir + "/Microsoft Visual Studio/2019/Enterprise/VC/Auxiliary/Build"
    elif base.is_dir(programFilesDir + "/Microsoft Visual Studio/2019/Professional/VC/Auxiliary/Build"):
      vs_path = programFilesDir + "/Microsoft Visual Studio/2019/Professional/VC/Auxiliary/Build"
    else:
      vs_path = programFilesDir + "/Microsoft Visual Studio/2019/Community/VC/Auxiliary/Build"
      
  return vs_path

def make():
  qt_build_path = os.path.dirname(os.path.abspath(__file__)) + "/qt_build/Qt-5.15.2/win_arm64"
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
    "-nomake", "examples",
    "-nomake", "tests",
    "-skip", "qtlocation",
    "-skip", "qtserialport",
    "-skip", "qtsensors",
    "-skip", "qtxmlpatterns",
    "-skip", "qt3d",
    "-skip", "qtwebview",
    "-skip", "qtwebengine",
    "-xplatform", "win32-arm64-msvc2017",
    "-mp",
    "-no-pch"]

  qt_params_str = ""
  for param in qt_params:
      qt_params_str += (param + " ")

  qt_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/qt/qt-everywhere-src-5.15.2.tar.xz"
  if not base.is_file("./qt_source_5.15.2.tar.xz"):
    base.download(qt_url, "./qt_source_5.15.2.tar.xz")
  
  if not base.is_dir("./qt-everywhere-src-5.15.2"):
    base.cmd("tar", ["-xf", "./qt_source_5.15.2.tar.xz"])
    
  vs_path = get_vs_path()
  vcvarsall_host_arch = "x64"
  
  qt_build_bat = []
  qt_build_bat.append("call \"" + vs_path + "/vcvarsall.bat\" " + vcvarsall_host_arch) # for nmake
  qt_build_bat.append("cd qt-everywhere-src-5.15.2")
  qt_build_bat.append("call configure " + qt_params_str)
  qt_build_bat.append("call nmake")
  qt_build_bat.append("call nmake install")
  base.run_as_bat(qt_build_bat)
  
if __name__ == "__main__":
  make()