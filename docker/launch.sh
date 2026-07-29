#!/bin/bash
set -e

echo "Generating Block IPs for startup.."
## only neede if not present
if [ ! -f /etc/openresty/block_ips_geo.conf ]; then
    /opt/scripts/generate_ip_blocklists.sh
fi
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