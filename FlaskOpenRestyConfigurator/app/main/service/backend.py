import os, re
from ..config import backend_path, templates_path

import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileRegex = r"(\d*)%([a-z0-9]*)%([^%]*)%([^%]*)%([^%]*)\.conf"


def getBackends():
        if not os.path.exists(backend_path) and not os.access(backend_path, os.W_OK):
            logger.error("Not able to access configured backend path.")
            return None
        if len(os.listdir(backend_path)) == 0:
            return []
        backendPathFiles = os.listdir(backend_path)
        validBackends = []
        for file in backendPathFiles:
            backendDict = {}

            match = re.fullmatch(fileRegex, file)
            if not match:
                logger.warning("Found a backend file with wrong naming: " + str(file))
                continue
            backendDict["id"] = match.group(1)
            backendDict["owner"] = match.group(2)
            backendDict["location_url"] = match.group(3)
            backendDict["template"] = match.group(4)
            backendDict["template_version"] = match.group(5)
            validBackends.append(backendDict)
        return validBackends
