FROM onlyoffice/documentserver:latest
RUN apt-get update -y && \ 
	apt-get install git -y \
			python -y \
			openjdk-11-jdk -y \
			npm -y && \
			npm install -g grunt-cli -y && \
	git clone --depth 1 https://github.com/ONLYOFFICE/build_tools.git var/www/onlyoffice/documentserver/build_tools && \
	sed -i '/documentserver-static-gzip.sh ${ONLYOFFICE_DATA_CONTAINER}/d' /app/ds/run-document-server.sh && \
	rm -rf /var/lib/apt/lists/*
ENTRYPOINT python /var/www/onlyoffice/documentserver/build_tools/develop/run_build_js.py /var/www/onlyoffice/documentserver && /bin/sh -c /app/ds/run-document-server.sh 
