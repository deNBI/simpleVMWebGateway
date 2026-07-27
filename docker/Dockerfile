FROM ubuntu:24.04

ENV FORC_BACKEND_PATH=/var/forc/backend_path/
ENV FORC_TEMPLATE_PATH=/var/forc/template_path/

RUN mkdir -p ${FORC_BACKEND_PATH} ${FORC_TEMPLATE_PATH}

RUN apt-get update && apt-get install -y \
    git \
    wget \
    gnupg \
    ca-certificates \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
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
RUN opm install zmartzone/lua-resty-openidc
RUN opm get bungle/lua-resty-session 
RUN mkdir -p /opt/simpleVMWebGateway

RUN git clone \
    https://github.com/deNBI/simpleVMWebGateway.git \
    /opt/simpleVMWebGateway/

WORKDIR /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt \
    && /opt/venv/bin/pip install gunicorn uvicorn

ENV PATH="/opt/venv/bin:$PATH"

COPY nginx.conf /etc/openresty/nginx.conf.j2
COPY render_nginx.py /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/
COPY gunicorn_conf.py gunicorn_conf.py
COPY launch.sh launch.sh

RUN chmod +x launch.sh
EXPOSE 5000
CMD ["./launch.sh"]