import sys
import os
sys.path.append('../../../scripts')

import base

def make():
  qt_build_path = os.path.dirname(os.path.abspath(__file__)) + "/qt_build/Qt-5.15.2"
  qt_binary_url = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/qt/qt_binary_win_arm64.7z"
  
  if not base.is_file("./qt_binary_win_arm64.7z"):
    base.download(qt_binary_url, "./qt_binary_win_arm64.7z")
    
  if not base.is_dir(qt_build_path):
    os.makedirs(qt_build_path)
    base.extract("./qt_binary_win_arm64.7z", qt_build_path)

if __name__ == "__main__":
  base.configure_common_apps()
  make()