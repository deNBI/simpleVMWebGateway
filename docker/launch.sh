#!/bin/bash
set -e

echo "Generating Block IPs for startup.."
## only needed if not present
if [ ! -f /tmp/block_ips_geo.conf ]; then
    /opt/scripts/generate_ip_blocklists.sh
fi

echo "Rendering OpenResty configuration..."
python3 /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/render_nginx.py

echo "Starting OpenResty..."
# Start openresty in background with a writable PID file
openresty -g "pid /tmp/openresty.pid"

echo "Starting Blocklist Updater Loop..."
(
    while true; do
        sleep 7200 # 2 hours
        echo "$(date): Updating blocklists..."
        /opt/scripts/generate_ip_blocklists.sh
        openresty -g "pid /tmp/openresty.pid" -s reload
    done
) &

echo "Starting FastAPI..."
exec gunicorn \
    -c gunicorn_conf.py \
    main:app
