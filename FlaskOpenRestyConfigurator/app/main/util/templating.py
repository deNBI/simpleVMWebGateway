import jinja2
from ..config import templates_path
import logging
import os


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


logger.info("Loading the templating engine.")

try:
    templateLoader = jinja2.FileSystemLoader(searchpath=templates_path)
    templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
except jinja2.exceptions.TemplatesNotFound:
    logger.error("Was not able to load template engine. Adjust the templates_path in the config.")


def generateBackendByTemplate(payload, suffixNumber):
    if not templateLoader or not templateEnv:
        logger.error("The template engine is not loaded. Can't generate backend.")
        return None
    assembledTemplateFileName = payload['template'] + '%' + payload['template_version'] + '.conf'
    if not os.path.isfile(templates_path + assembledTemplateFileName):
        logger.error("Not able to find " + templates_path + assembledTemplateFileName)
        return None
    template = templateEnv.get_template(assembledTemplateFileName)

    renderedBackend = template.render(key_url=payload['user_key_url'] + '_' + suffixNumber,
                                      owner=payload['owner'],
                                      location_url=payload['upstream_url'])
    return renderedBackend