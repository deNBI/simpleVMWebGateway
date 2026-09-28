#!/bin/bash
set -e

# 1. Install dependencies
echo "Installing dependencies..."
pip install jinja2 gixy-next

# 2. Setup temporary directories
echo "Setting up temporary directories..."
rm -rf render_tmp
mkdir -p render_tmp/template render_tmp/backends

# Create dummy files to satisfy Gixy's parser and avoid "File not found" warnings
touch render_tmp/mime.types
sudo mkdir -p /etc/openresty/
sudo touch /etc/openresty/block_ips_geo.conf

# 3. Prepare main configuration
cp docker/nginx.conf render_tmp/template/nginx.conf.j2

# 4. Set environment variables for render_nginx.py
# Use GITHUB_WORKSPACE if available, otherwise use current directory
BASE_DIR="${GITHUB_WORKSPACE:-$(pwd)}"

export RENDER_NGINX_TEMPLATE_DIR="$BASE_DIR/render_tmp/template/"
export RENDER_NGINX_OUTPUT_FILE="$BASE_DIR/render_tmp/nginx.conf"
export OPENRESTY_WORKER_PROCESSES="auto"
export OPENRESTY_WORKER_RLIMIT_NOFILE="65535"
export OPENRESTY_WORKER_CONNECTIONS="1024"
export OPENRESTY_DNS_SERVER="127.0.0.11"
export FORC_SECRET_KEY="dummy-secret"
export DOMAIN="example.com"
export FORC_OIDC_DISCOVERY_URL="https://example.com/.well-known/openid-configuration"
export FORC_OIDC_CLIENT_ID="dummy-id"
export FORC_OIDC_CLIENT_SECRET="dummy-secret"
export FORC_SERVICE_USE_HTTPS="true"
export FORC_SERVICE_PORT="8443"
export FORC_LOCAL_IP="127.0.0.1"
export FORC_BACKEND_PATH="$BASE_DIR/render_tmp/backends"

# 5. Render main config
echo "Rendering main config..."
python3 docker/render_nginx.py

# 6. Render example templates
echo "Rendering example templates..."
for template in examples/templates/*.conf; do
    filename=$(basename "$template")
    python3 docker/render_template_snippet.py "$template" "./render_tmp/backends/$filename"
done

# 7. Run Gixy scan
echo "--------------------------------------------"
echo "Running Gixy-Next Scan..."
echo "--------------------------------------------"
gixy ./render_tmp/nginx.conf
