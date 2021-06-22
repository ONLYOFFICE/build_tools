#!/bin/bash

LETSENCRYPT_ROOT_DIR="/etc/letsencrypt/live";
ROOT_DIR="/var/www/onlyoffice/documentserver/letsencrypt";
NGINX_CONF_DIR="/etc/onlyoffice/documentserver/nginx";

if [ "$#" -ge "2" ]; then
    LETS_ENCRYPT_MAIL=$1
    LETS_ENCRYPT_DOMAIN=$2

    SSL_CERT="${LETSENCRYPT_ROOT_DIR}/${LETS_ENCRYPT_DOMAIN}/fullchain.pem";
    SSL_KEY="${LETSENCRYPT_ROOT_DIR}/${LETS_ENCRYPT_DOMAIN}/privkey.pem";

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    mkdir -p ${ROOT_DIR}

    echo certbot certonly --expand --webroot -w ${ROOT_DIR} --noninteractive --agree-tos --email $LETS_ENCRYPT_MAIL -d $LETS_ENCRYPT_DOMAIN > /var/log/le-start.log

    certbot certonly --expand --webroot -w ${ROOT_DIR} --noninteractive --agree-tos --email $LETS_ENCRYPT_MAIL -d $LETS_ENCRYPT_DOMAIN > /var/log/le-new.log

    if [ -f ${SSL_CERT} -a -f ${SSL_KEY} ]; then
        if [ -f ${NGINX_CONF_DIR}/ds-ssl.conf.tmpl ]; then
            cp -f ${NGINX_CONF_DIR}/ds-ssl.conf.tmpl ${NGINX_CONF_DIR}/ds.conf
            sed 's,{{SSL_CERTIFICATE_PATH}},'"${SSL_CERT}"',' -i ${NGINX_CONF_DIR}/ds.conf
            sed 's,{{SSL_KEY_PATH}},'"${SSL_KEY}"',' -i ${NGINX_CONF_DIR}/ds.conf
        fi
    fi

    service nginx reload

    cat > ${DIR}/letsencrypt_cron.sh <<END
    certbot renew >> /var/log/le-renew.log
    service nginx reload
END

    chmod a+x ${DIR}/letsencrypt_cron.sh

    cat > /etc/cron.d/letsencrypt <<END
    @weekly root ${DIR}/letsencrypt_cron.sh
END

else
    echo "This script provided to automatically get Let's Encrypt SSL Certificates for Document Server"
    echo "usage:"
    echo "  documentserver-letsencrypt.sh EMAIL DOMAIN"
    echo "      EMAIL       Email used for registration and recovery contact. Use"
    echo "                  comma to register multiple emails, ex:"
    echo "                  u1@example.com,u2@example.com."
    echo "      DOMAIN      Domain name to apply"
fi
