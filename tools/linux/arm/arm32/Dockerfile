FROM arm32v7/ubuntu:16.04

# basic dependencies
RUN apt-get -y update && \
    apt-get -y install wget xz-utils

# qt source
RUN mkdir /source && cd /source && \
    wget -q https://download.qt.io/new_archive/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz && \
    tar -xf qt-everywhere-opensource-src-5.9.9.tar.xz

# build dependencies
RUN apt-get -y install \
    build-essential \
    glib-2.0-dev \
    libglu1-mesa-dev \
    libgtk-3-dev \
    libpulse-dev \
    libasound2-dev \
    libatspi2.0-dev \
    libcups2-dev \
    libdbus-1-dev \
    libicu-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libx11-xcb-dev \
    libxcb* \
    libxi-dev \
    libxrender-dev \
    libxss-dev

# increase or decrease CORES value to change the number of parallel jobs while building qt
ENV CORES=4

CMD cd /source/qt-everywhere-opensource-src-5.9.9 && \
    ./configure -opensource -confirm-license -release -shared -accessibility -prefix /build -qt-zlib -qt-libpng -qt-libjpeg -qt-xcb -qt-pcre -no-sql-sqlite -no-qml-debug -gstreamer 1.0 -nomake examples -nomake tests -skip qtenginio -skip qtlocation -skip qtserialport -skip qtsensors -skip qtxmlpatterns -skip qt3d -skip qtwebview -skip qtwebengine && \
    make -j$CORES && \
    make install
