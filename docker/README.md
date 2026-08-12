# Docker Deployment for FORC

This directory contains the configuration and scripts necessary to build and run the FORC (FastAPI OpenResty Configurator) gateway in a Docker container.

## Overview

FORC is a hybrid gateway that leverages **OpenResty** (an extended Nginx) for high-performance request handling and **FastAPI** for dynamic configuration and management. 

The container automates the setup of:
- A dynamically rendered Nginx configuration based on environment variables.
- An automated IP blocklist update system.
- A FastAPI backend running via Gunicorn.

## File Descriptions

| File | Description |
| :--- | :--- |
| `Dockerfile` | Multi-stage build definition based on Ubuntu 24.04. Installs OpenResty, Python, and necessary Lua modules. |
| `docker-compose.yml` | Service orchestration defining ports, volumes, and environment variable sources. |
| `launch.sh` | Container entrypoint. Orchestrates the startup sequence: blocklist generation $\rightarrow$ Nginx rendering $\rightarrow$ OpenResty start $\rightarrow$ Background blocklist loop $\rightarrow$ FastAPI start. |
| `render_nginx.py` | A utility script that renders the Nginx template (`nginx.conf.j2`) using all current environment variables. |
| `generate_ip_blocklists.sh` | Downloads and processes IP blocklists from sources defined in `ip_blocklists.txt` into a format OpenResty can use. |
| `ip_blocklists.txt` | A list of external URLs providing IP blocklists. |
| `gunicorn_conf.py` | Configuration settings for the Gunicorn WSGI server. |
| `nginx.conf` | The Jinja2 template used by `render_nginx.py` to generate the final Nginx configuration. |

## Container Internals

### Architecture
- **OS**: Ubuntu 24.04
- **Web Server**: OpenResty (Nginx + Lua)
- **Application**: FastAPI (Python 3)
- **WSGI Server**: Gunicorn

### Key Directories
- `/opt/simpleVMWebGateway/FastapiOpenRestyConfigurator`: The application root.
- `/etc/openresty/`: Contains the generated `nginx.conf` and `block_ips_geo.conf`.
- `/var/forc/backend_path/`: Used for backend persistence.
- `/var/forc/template_path/`: Stores configuration templates.
- `/opt/scripts/`: Contains the blocklist generation scripts.

### Startup Sequence
1. **Blocklist Generation**: `generate_ip_blocklists.sh` is run to create the initial `/etc/openresty/block_ips_geo.conf`.
2. **Configuration Rendering**: `render_nginx.py` takes all system environment variables and applies them to the Nginx template.
3. **OpenResty Startup**: The OpenResty server is started to handle incoming traffic on ports 80 and 443.
4. **Blocklist Updater**: A background process is spawned that refreshes the IP blocklists every 2 hours and reloads OpenResty.
5. **FastAPI Startup**: The FastAPI application is started via Gunicorn on port 5000.

## Configuration

### Environment Variables (`.env`)

FORC uses a single `.env` file for both the OpenResty configuration and the FastAPI application.

#### 1. OpenResty / Gateway Settings
These variables are used by `render_nginx.py` to generate the final Nginx configuration.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DOMAIN` | The primary domain name for the gateway. | `gateway.example.com` |
| `FORC_SERVICE_PORT` | Port for the internal service. | `443` |
| `FORC_SERVICE_USE_HTTPS` | Whether to use HTTPS for the internal service. | `True` / `False` |
| `FORC_LOCAL_IP` | Local IP to bind to if HTTPS is disabled. | `0.0.0.0` |
| `OPENRESTY_DNS_SERVER` | DNS server for OpenResty resolver. | `8.8.8.8` |
| `OPENRESTY_WORKER_PROCESSES` | Number of Nginx worker processes. | `auto` or `10` |
| `FORC_OIDC_DISCOVERY_URL` | OIDC discovery endpoint. | `https://auth.example.com/...` |
| `FORC_OIDC_CLIENT_ID` | Client ID assigned by OIDC provider. | `my-client-id` |
| `FORC_OIDC_CLIENT_SECRET` | Client secret assigned by OIDC provider. | `secret-string` |
| `FORC_SECRET_KEY` | Secret key for session signing. | `random-long-string` |

#### 2. FastAPI Application Settings
Required for the management API and backend logic.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `FORC_API_KEY` | API key for authenticating with the FORC API. | `secure-api-key` |
| `FORC_SECRET_KEY` | Secret key for session signing. | `random-long-string` |
| `FORC_BACKEND_PATH` | Path for backend persistence. | `/var/forc/backend_path` |
| `FORC_TEMPLATE_PATH` | Path for configuration templates. | `/var/forc/template_path` |
| `DEBUG` | Enable debug mode. | `True` / `False` |
| `LOG_LEVEL` | Logging verbosity. | `INFO`, `DEBUG`, `WARNING` |

### Mounts & Volumes

The following mounts are configured in `docker-compose.yml`:

| Host Path | Container Path | Mode | Purpose |
| :--- | :--- | :--- | :--- |
| `/var/forc/backend_path/` | `/var/forc/backend_path/` | `rw` | Persistence for the backend database/files. |
| `/etc/letsencrypt/` | `/etc/letsencrypt/` | `r` | SSL certificates for HTTPS. |
| `.env` | `/opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/.env` | `rw` | Unified environment configuration. |

## Usage

1. Create a `.env` file containing all required variables from the tables above.
2. Start the gateway:
```bash
docker-compose up -d
```

To view logs:
```bash
docker-compose logs -f
```
