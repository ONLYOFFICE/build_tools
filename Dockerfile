FROM ubuntu:14.04

RUN apt-get -y update

ADD . /build_tools
WORKDIR /build_tools

CMD cd tools/linux && \
    python3 ./automate.py
