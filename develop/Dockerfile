FROM onlyoffice/documentserver


RUN apt-get update -y
RUN apt-get install git -y
RUN apt-get install openjdk-11-jdk -y
RUN apt-get install npm -y
RUN npm install -g grunt-cli -y
WORKDIR /var/www/onlyoffice/documentserver
RUN git clone https://github.com/ONLYOFFICE/build_tools.git
WORKDIR /var/www/onlyoffice/documentserver/build_tools/scripts
RUN git checkout develop

ENTRYPOINT python run_build_js.py /var/www/onlyoffice/documentserver && /bin/sh -c /app/ds/run-document-server.sh 
