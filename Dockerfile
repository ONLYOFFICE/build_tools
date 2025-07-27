FROM ubuntu:20.04

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && \
    apt-get -y install python3 \
                       sudo
RUN ln -s /usr/bin/python3 /usr/bin/python
ADD . /build_tools
WORKDIR /build_tools

CMD ["sh", "-c", "cd tools/linux && python3 ./automate.py"]
