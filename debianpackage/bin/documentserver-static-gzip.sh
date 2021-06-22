#!/bin/bash

DIR="/var/www/onlyoffice/documentserver"
NGINX_ONLYOFFICE_PATH="/etc/onlyoffice/documentserver/nginx"

cd ${DIR}
# Make gziped scripts
find ./sdkjs ./web-apps ./sdkjs-plugins -type f \( -name *.js -o -name *.json -o -name *.htm -o -name *.html -o -name *.css \) -exec gzip -kf9 {} \;

# Make gziped fonts
find ./fonts -type f ! -name "*.*" -exec gzip -kf9 {} \;

# Turn on static gzip for nginx
sed 's/#*\s*\(gzip_static\).*/\1 on;/g' \
  -i ${NGINX_ONLYOFFICE_PATH}/includes/ds-docservice.conf

# Reload nginx config
service nginx reload
