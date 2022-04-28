"""
Helper/service functions regarding templates.
"""
import os
import re
import logging
from typing import List

from ..model.serializers import Template
from ..config import get_settings

logger = logging.getLogger("service")
settings = get_settings()


async def check_path_access():
    return os.path.exists(settings.FORC_TEMPLATE_PATH) and os.access(settings.FORC_TEMPLATE_PATH, os.R_OK)


async def get_templates(template_name=None, template_version=None) -> List[Template]:
    if not await check_path_access():
        return []
    if len(os.listdir(settings.FORC_TEMPLATE_PATH)) == 0:
        return []
    if template_name is None and template_version is None:
        file_regex = f"(.*)%(.*).conf"
    elif template_version is None:
        template_name = re.escape(template_name)
        file_regex = f"({template_name})%(.*).conf"
    else:
        template_name = re.escape(template_name)
        template_version = re.escape(template_version)
        file_regex = f"({template_name})%({template_version}).conf"
    template_path_files = os.listdir(settings.FORC_TEMPLATE_PATH)
    valid_templates = []
    for file in template_path_files:
        match = re.fullmatch(file_regex, file)
        if not match:
            continue
        template: Template = Template(
            name=match.group(1),
            version=match.group(2)
        )
        valid_templates.append(template)
    return valid_templates
