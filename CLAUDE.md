# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- **Install Dependencies**:
  ```bash
  pip install -r FastapiOpenRestyConfigurator/requirements.txt
  ```
- **Run Application (Development)**:
  ```bash
  # From project root
  export PYTHONPATH=$PYTHONPATH:$(pwd)/FastapiOpenRestyConfigurator
  uvicorn FastapiOpenRestyConfigurator.main:app --reload
  ```
- **Run Application (Production)**:
  ```bash
  # Using gunicorn with provided config
  gunicorn -c FastapiOpenRestyConfigurator/gunicorn_conf.py FastapiOpenRestyConfigurator.main:app
  ```

### Testing
- **Run All Tests**:
  ```bash
  # From project root
  export PYTHONPATH=$PYTHONPATH:$(pwd)/FastapiOpenRestyConfigurator
  pytest FastapiOpenRestyConfigurator/tests
  ```
- **Run Single Test File**:
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)/FastapiOpenRestyConfigurator
  pytest FastapiOpenRestyConfigurator/tests/test_specific_file.py
  ```

## Architecture

The project (Flask OpenResty Configurator - FORC) is a FastAPI-based service that dynamically generates NGINX configuration snippets for an OpenResty web server.

### High-Level Flow
1. **Request**: A REST API request is received by a `view`.
2. **Logic**: The `view` calls a `service` to perform business logic (e.g., creating a new backend).
3. **Templating**: The `service` uses Jinja2 templates to generate a configuration snippet.
4. **Persistence**: The snippet is written to the filesystem (`FORC_BACKEND_PATH`).
5. **Activation**: OpenResty is reloaded to apply the new configuration.

### Project Structure (`FastapiOpenRestyConfigurator/`)
- `main.py`: Entry point; initializes the FastAPI app and includes routers.
- `app/main/views/`: API endpoints (Controllers).
- `app/main/service/`: Core business logic.
    - `backend.py`: Manages backend configurations.
    - `openresty.py`: Handles OpenResty interactions (e.g., reloading).
    - `template.py`: Manages Jinja2 template rendering.
    - `user.py`: User management logic.
- `app/main/model/`: Data models and Pydantic serializers.
- `app/main/util/`: Shared utilities for authentication, logging, and templating.
- `tests/`: Integration and unit tests.

### Configuration
The application is configured via environment variables:
- `FORC_SECRET_KEY`: Encryption key for the service.
- `FORC_API_KEY`: API key for `X-API-KEY` authentication.
- `FORC_BACKEND_PATH`: Filesystem path where NGINX config snippets are stored.
- `FORC_TEMPLATE_PATH`: Filesystem path where Jinja2 templates are located.
