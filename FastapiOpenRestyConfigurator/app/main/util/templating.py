"""
Helper/service functions to generate backends out of templates.
"""
import jinja2
import logging
import os

from ..model.serializers import BackendTemp
from ..config import get_settings

logger = logging.getLogger("util")
settings = get_settings()

logger.info("Loading the templating engine.")

try:
    templateLoader = jinja2.FileSystemLoader(searchpath=settings.FORC_TEMPLATE_PATH)
    templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
except jinja2.exceptions.TemplatesNotFound:
    logger.error("Was not able to load template engine. Adjust the templates_path in the config.")


async def generate_backend_by_template(backend_temp: BackendTemp, suffix_number):
    if not templateLoader or not templateEnv:
        logger.error("The template engine is not loaded. Can't generate backend.")
        return None
    assembled_template_file_name = f"{backend_temp.template}%{backend_temp.template_version}.conf"
    if not os.path.isfile(f"{settings.FORC_TEMPLATE_PATH}/{assembled_template_file_name}"):
        logger.error(f"Not able to find {settings.FORC_TEMPLATE_PATH}/{assembled_template_file_name}")
        return None
    template = templateEnv.get_template(assembled_template_file_name)

    rendered_backend = template.render(
        key_url=f"{backend_temp.user_key_url}_{suffix_number}",
        owner=backend_temp.owner,
        backend_id=backend_temp.id,
        forc_backend_path=settings.FORC_BACKEND_PATH,
        location_url=backend_temp.upstream_url
    )
    return rendered_backend
