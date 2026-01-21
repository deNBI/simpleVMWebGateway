"""
Helper/service functions to generate backends out of templates.
"""
import jinja2
import logging
import os
from functools import lru_cache

from ..model.serializers import BackendTemp
from ..config import get_settings

logger = logging.getLogger("util")


@lru_cache
def _template_env():
    """
    Lazily initialize and cache the Jinja environment.
    Called only at runtime, never at import time.
    """
    settings = get_settings()

    logger.info("Loading the templating engine.")

    loader = jinja2.FileSystemLoader(
        searchpath=settings.FORC_TEMPLATE_PATH
    )

    env = jinja2.Environment(
        loader=loader,
        autoescape=True
    )

    return env, settings


async def generate_backend_by_template(
    backend_temp: BackendTemp,
    suffix_number: int
) -> str | None:

    env, settings = _template_env()

    assembled_template_filename = (
        f"{backend_temp.template}%{backend_temp.template_version}.conf"
    )

    template_path = os.path.join(
        settings.FORC_TEMPLATE_PATH,
        assembled_template_filename
    )

    if not os.path.isfile(template_path):
        logger.error(f"Template not found: {template_path}")
        return None

    template = env.get_template(assembled_template_filename)

    rendered_backend = template.render(
        key_url=f"{backend_temp.user_key_url}_{suffix_number}",
        owner=backend_temp.owner,
        backend_id=backend_temp.id,
        forc_backend_path=settings.FORC_BACKEND_PATH,
        location_url=backend_temp.upstream_url,
        auth_enabled=backend_temp.auth_enabled,
    )

    return rendered_backend
