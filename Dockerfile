FROM ubuntu:20.04

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && \
    apt-get -y install tar \
                       sudo

ADD . /build_tools
WORKDIR /build_tools

RUN mkdir -p /opt/python3 && \
    tar -xzf /build_tools/tools/linux/python3.tar.gz -C /opt/python3 --strip-components=1

ENV PATH="/opt/python3/bin:${PATH}"

RUN ln -s /opt/python3/bin/python3.10 /usr/bin/python

CMD ["sh", "-c", "cd tools/linux && python3 ./automate.py"]
