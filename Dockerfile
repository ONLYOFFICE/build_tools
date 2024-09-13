FROM ubuntu:22.04


ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && \
    apt-get -y install python2 \
    python3 \
    sudo \
    apt-transport-https \ 
    autoconf2.13 \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    git \
    glib-2.0-dev \
    libglu1-mesa-dev \
    libgtk-3-dev \
    libpulse-dev \
    libtool \
    p7zip-full \
    subversion \
    gzip \
    libasound2-dev \
    libatspi2.0-dev \
    libcups2-dev \
    libdbus-1-dev \
    libicu-dev \
    libglu1-mesa-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libx11-xcb-dev \
    libxcb* \
    libxi-dev \
    libxrender-dev \
    libxss1 \
    libncurses5 \
    ninja-build \
    libstdc++-10-dev

 RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
 && apt-get install -y nodejs \
 && curl -L https://www.npmjs.com/install.sh | sh 

 RUN apt-get install -y yarn 
 RUN npm install -g grunt-cli 
 RUN npm install -g pkg 
 RUN  ln -s /usr/bin/python2 /usr/bin/python
# RUN rm /usr/bin/python && ln -s /usr/bin/python2 /usr/bin/python
# ADD . /build_tools
# WORKDIR /build_tools

# CMD cd tools/linux && \
#     python3 ./automate.py
