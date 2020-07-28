FROM ubuntu:14.04

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && \
    apt-get -y install python3 \
                       sudo

ADD . /build_tools
WORKDIR /build_tools

CMD cd tools/linux && \
    python3 ./automate.py
