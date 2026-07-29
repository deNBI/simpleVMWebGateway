#!/bin/bash
set -e

echo "Generating Block IPs for startup.."
./opt/scripts/generate_ip_blocklists.sh
echo "Starting cron..."
service cron start

echo "Rendering OpenResty configuration..."

python3 /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/render_nginx.py

echo "Starting OpenResty..."
openresty

echo "Starting FastAPI..."
exec gunicorn \
    -c gunicorn_conf.py \
    main:app