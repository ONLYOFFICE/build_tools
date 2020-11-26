FROM onlyoffice/documentserver
RUN apt-get update -y && apt-get install git -y && apt-get install openjdk-11-jdk -y && apt-get install npm -y && npm install -g grunt-cli -y && rm -rf /var/lib/apt/lists/* && mkdir /var/www/onlyoffice/documentserver/build_tools && git clone --depth 1 https://github.com/ONLYOFFICE/build_tools.git var/www/onlyoffice/documentserver/build_tools 
ENTRYPOINT python /var/www/onlyoffice/documentserver/build_tools/develop/run_build_js.py /var/www/onlyoffice/documentserver && /bin/sh -c /app/ds/run-document-server.sh 
