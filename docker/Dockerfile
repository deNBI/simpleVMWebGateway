# --- Build Stage ---
FROM openresty/openresty:1.31-alpine-slim@sha256:f05c593f0afbb916361496a2d21aa22edc5d5e54e15160f88d12b62f3918bf22 AS build-stage

# Install build-time dependencies
RUN apk add --no-cache \
    bash \
    gcc \
    make \
    musl-dev \
    lua5.1-dev \
    git \
    python3 \
    python3-dev \
    py3-pip \
    luarocks5.1

# Install Lua modules into OpenResty lualib directory
RUN luarocks-5.1 install lua-resty-openidc \
    && cp -r /usr/local/share/lua/5.1/* /usr/local/openresty/lualib/

# Prepare Python virtual environment
COPY FastapiOpenRestyConfigurator/requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r /tmp/requirements.txt \
    && /opt/venv/bin/pip install gunicorn uvicorn

# --- Runtime Stage ---
FROM openresty/openresty:1.31-alpine-slim@sha256:f05c593f0afbb916361496a2d21aa22edc5d5e54e15160f88d12b62f3918bf22 AS runtime-stage

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONTAINERIZED=true
ENV FORC_BACKEND_PATH=/var/forc/backend_path/
ENV FORC_TEMPLATE_PATH=/var/forc/template_path/
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime-only dependencies
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    ca-certificates \
    python3

# Path Mapping: Link /etc/openresty to the default OpenResty config directory
# This maintains compatibility with render_nginx.py and scripts
RUN ln -snf /usr/local/openresty/nginx/conf /etc/openresty

# Copy artifacts from build-stage
COPY --from=build-stage /opt/venv /opt/venv
COPY --from=build-stage /usr/local/openresty/lualib /usr/local/openresty/lualib

# Copy application code and configurations
WORKDIR /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator
COPY FastapiOpenRestyConfigurator .
# Copy Docker-specific files (build context is project root)
COPY docker/nginx.conf /etc/openresty/nginx.conf.j2
COPY docker/render_nginx.py .
COPY docker/gunicorn_conf.py .
COPY docker/launch.sh .
COPY docker/generate_ip_blocklists.sh docker/ip_blocklists.txt /opt/scripts/
COPY docker/html /usr/local/openresty/nginx/html

# Setup permissions
RUN mkdir -p ${FORC_BACKEND_PATH} ${FORC_TEMPLATE_PATH} /opt/scripts \
    && chmod +x launch.sh /opt/scripts/generate_ip_blocklists.sh
COPY examples/templates  ${FORC_TEMPLATE_PATH}

EXPOSE 5000
CMD ["./launch.sh"]
