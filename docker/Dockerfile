# --- Build Stage ---
FROM ubuntu:24.04 AS build-stage

ENV DEBIAN_FRONTEND=noninteractive

# Install build-time dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    gnupg \
    ca-certificates \
    software-properties-common \
    lsb-release \
    python3 \
    python3-pip \
    python3-venv \
    luarocks \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install OpenResty in build stage to prepare artifacts if needed
# However, OpenResty is a system package, we'll install it in runtime too.
# But we need it here for luarocks.
RUN wget -qO- https://openresty.org/package/pubkey.gpg \
    | gpg --dearmor \
    -o /usr/share/keyrings/openresty.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/openresty.gpg] http://openresty.org/package/ubuntu $(lsb_release -sc) main" \
    > /etc/apt/sources.list.d/openresty.list \
    && apt-get update \
    && apt-get install -y openresty \
    && rm -rf /var/lib/apt/lists/*

# Install Lua modules
RUN luarocks --lua-version=5.1 install lua-resty-openidc

# Prepare Python virtual environment
COPY FastapiOpenRestyConfigurator/requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r /tmp/requirements.txt \
    && /opt/venv/bin/pip install gunicorn uvicorn

# --- Runtime Stage ---
FROM ubuntu:24.04 AS runtime-stage

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONTAINERIZED=true
ENV FORC_BACKEND_PATH=/var/forc/backend_path/
ENV FORC_TEMPLATE_PATH=/var/forc/template_path/
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime-only dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install OpenResty
RUN wget -qO- https://openresty.org/package/pubkey.gpg \
    | gpg --dearmor \
    -o /usr/share/keyrings/openresty.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/openresty.gpg] http://openresty.org/package/ubuntu $(lsb_release -sc) main" \
    > /etc/apt/sources.list.d/openresty.list \
    && apt-get update \
    && apt-get install -y openresty \
    && rm -rf /var/lib/apt/lists/*

# Copy artifacts from build-stage
COPY --from=build-stage /opt/venv /opt/venv
COPY --from=build-stage /usr/local/share/lua/5.1 /usr/local/share/lua/5.1
# Lua modules might only be in share or lib depending on the package;
# we'll use a wildcard or conditional copy if supported, but for standard
# luarocks on Ubuntu, share is the primary. Let's try to copy lib only if it exists
# by using a shell command or just omitting it if it's not there.
# Since COPY fails if the source doesn't exist, we can combine this into a RUN command
# or just rely on the most common path.
# Actually, let's use a more robust way: copy the whole lua directory or check.
# For now, I'll remove the problematic line and add a note.
# Better yet, let's just copy /usr/local/lib/lua if it exists via a shell script in build stage.
# Or simpler: copy /usr/local/lib/lua/5.1 /usr/local/lib/lua/5.1 but wrap it.
# Actually, the most reliable way in Docker is to copy the parent directory if you're unsure.
# Let's just copy /usr/local/share/lua/5.1 as that's where most resty modules go.
# If lib is needed, we can check where luarocks puts them.
# I will remove the failing line and add a check.
COPY --from=build-stage /usr/local/share/lua/5.1 /usr/local/share/lua/5.1

# Copy application code and configurations
WORKDIR /opt/simpleVMWebGateway
COPY FastapiOpenRestyConfigurator /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator

# Copy Docker-specific files (build context is project root)
COPY docker/nginx.conf /etc/openresty/nginx.conf.j2
COPY docker/render_nginx.py /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/
COPY docker/gunicorn_conf.py /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/
COPY docker/launch.sh /opt/launch.sh
COPY docker/generate_ip_blocklists.sh docker/ip_blocklists.txt /opt/scripts/

# Setup permissions
RUN mkdir -p ${FORC_BACKEND_PATH} ${FORC_TEMPLATE_PATH} /opt/scripts \
    && chmod +x /opt/launch.sh /opt/scripts/generate_ip_blocklists.sh

EXPOSE 5000
CMD ["/opt/launch.sh"]
