FROM onlyoffice/documentserver

RUN rm -rf /var/www/onlyoffice/documentserver/sdkjs/*
RUN rm -rf /var/www/onlyoffice/documentserver/web-apps/*

ENTRYPOINT /bin/sh -c /app/ds/run-document-server.sh
