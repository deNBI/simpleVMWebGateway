import os
import re
from ..config import templates_path
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def check_path_access():
    return os.path.exists(templates_path) and os.access(templates_path, os.R_OK)


def get_templates(template_name=None, template_version=None):
    if not check_path_access():
        return None
    if len(os.listdir(templates_path)) == 0:
        return []
    if template_name is None and template_version is None:
        file_regex = f"(.*)%(.*).conf"
    elif template_version is None:
        file_regex = f"({template_name})%(.*).conf"
    else:
        file_regex = f"({template_name})%({template_version}).conf"
    template_path_files = os.listdir(templates_path)
    valid_templates = []
    for file in template_path_files:
        template_dict = {}
        match = re.fullmatch(file_regex, file)
        if not match:
            continue
        template_dict["name"] = match.group(1)
        template_dict["version"] = match.group(2)
        valid_templates.append(template_dict)
    return valid_templates
