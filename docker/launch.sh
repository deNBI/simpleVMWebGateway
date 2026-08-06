#!/bin/bash
set -e

echo "Generating Block IPs for startup.."
## only needed if not present
if [ ! -f /etc/openresty/block_ips_geo.conf ]; then
    /opt/scripts/generate_ip_blocklists.sh
fi

echo "Rendering OpenResty configuration..."
python3 render_nginx.py

echo "Starting OpenResty..."
openresty

echo "Starting Blocklist Updater Loop..."
(
    while true; do
        sleep 7200 # 2 hours
        echo "$(date): Updating blocklists..."
        /opt/scripts/generate_ip_blocklists.sh
        openresty -s reload
    done
) &

echo "Starting FastAPI..."
exec gunicorn \
    -c gunicorn_conf.py \
    main:app
