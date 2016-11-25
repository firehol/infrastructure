#!/bin/sh

set -e

mkdir -p /home/web/firehol/ssl

cp certs/firehol.org/fullchain.pem /home/web/firehol/ssl/nginx.crt
cp certs/firehol.org/privkey.pem /home/web/firehol/ssl/nginx.key

sudo chown -R firehol:web /home/web/firehol/ssl
sudo chown firehol:web /home/web/firehol/ssl/nginx.key
sudo chmod 640 /home/web/firehol/ssl/nginx.key


nginx -s reload

exit 0
