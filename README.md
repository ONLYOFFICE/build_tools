# build_tools

## Linux

### Please note, that all instruction tested on Ubuntu 14.04

1. Install QT. Tested on [qt-5.9.8](https://download.qt.io/archive/qt/5.9/5.9.8/single/qt-everywhere-opensource-src-5.9.8.tar.xz)  
QT installer requires GUI.  
If you want to build on server without GUI - compile qt from source.

2. Install dependencies via `bash ./scripts/dependencies`
3. Configure build via `bash ./configure` with additional params, described in help
4. Run build via `bash ./make`
