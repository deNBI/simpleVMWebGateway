import os, re
from ..config import templates_path
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileRegex = r"(.*)%(.*).conf"

def getTemplates():
    if not os.path.exists(templates_path) and not os.access(templates_path, os.R_OK):
        logger.error("Not able to access configured templates path.")
        return None
    if len(os.listdir(templates_path)) == 0:
        return []
    templatePathFiles = os.listdir(templates_path)
    validTemplates = []
    for file in templatePathFiles:
        templateDict = {}
        match = re.fullmatch(fileRegex, file)
        if not match:
            logger.warning("Found a template file with wrong naming, skipping it: " + str(file))
            continue
        templateDict["name"] = match.group(1)
        templateDict["version"] = match.group(2)
        validTemplates.append(templateDict)
    return validTemplates
