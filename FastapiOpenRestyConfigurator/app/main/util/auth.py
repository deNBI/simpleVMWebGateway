"""
Util functions regarding authentication.
"""
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from ..config import get_settings

API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
settings = get_settings()


async def get_api_key(
    api_key_header_in: str = Security(api_key_header),
):
    if api_key_header_in == settings.FORC_API_KEY.get_secret_value():
        return api_key_header_in
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
