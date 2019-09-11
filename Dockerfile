FROM ubuntu:14.04

RUN apt-get -y update && apt-get -y install wget
WORKDIR /tmp

RUN wget https://download.qt.io/archive/qt/5.9/5.9.8/single/qt-everywhere-opensource-src-5.9.8.tar.xz
RUN apt-get -y update && apt-get -y install xz-utils
RUN tar -xf qt-everywhere-opensource-src-5.9.8.tar.xz

WORKDIR /tmp/qt-everywhere-opensource-src-5.9.8
RUN apt-get -y install g++ \
                       libglu1-mesa-dev \
                       libgstreamer-plugins-base1.0-dev \
                       make
RUN ./configure -opensource -confirm-license -release -shared -accessibility -prefix /usr/local/Qt-5.9.8/gcc_64 -qt-zlib -qt-libpng -qt-libjpeg -qt-xcb -qt-pcre -no-sql-sqlite -no-qml-debug -gstreamer 1.0 -nomake examples -nomake tests -skip qtenginio -skip qtlocation -skip qtserialport -skip qtsensors -skip qtxmlpatterns -skip qt3d -skip qtwebview -skip qtwebengine
RUN make
RUN make install

ADD . /build_tools
WORKDIR /build_tools
RUN /build_tools/scripts/dependencies
RUN bash ./configure --module "desktop builder" --platform native --update 1 --branch develop --clean 0  --qt-dir "/usr/local/Qt-5.9.8"
RUN bash ./make
