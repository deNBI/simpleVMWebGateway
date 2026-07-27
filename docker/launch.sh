#!/bin/bash
set -e

echo "Rendering OpenResty configuration..."

python3 /usr/local/bin/render_nginx.py

echo "Starting OpenResty..."
openresty

echo "Starting FastAPI..."
exec gunicorn \
    -c gunicorn_conf.py \
    main:app