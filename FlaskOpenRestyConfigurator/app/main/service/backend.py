import os, re
from ..config import backend_path, templates_path
from werkzeug.exceptions import NotFound, InternalServerError
from .openresty import reloadOpenresty

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
                logger.warning("Found a backend file with wrong naming, skipping it: " + str(file))
                continue
            backendDict["id"] = match.group(1)
            backendDict["owner"] = match.group(2)
            backendDict["location_url"] = match.group(3)
            backendDict["template"] = match.group(4)
            backendDict["template_version"] = match.group(5)
            validBackends.append(backendDict)
        return validBackends


def deleteBackend(backendID):
    if not os.path.exists(backend_path) and not os.access(backend_path, os.W_OK):
        logger.error("Not able to access configured backend path.")
        return None
    if len(os.listdir(backend_path)) == 0:
        return []
    backendPathFiles = os.listdir(backend_path)
    for file in backendPathFiles:
        match = re.fullmatch(fileRegex, file)
        if not match:
            logger.warning("Found a backend file with wrong naming, skipping it: " + str(file))
            continue
        if int(match.group(1)) == int(backendID):
            logger.info("Attempting to delete backend with id: " + str(backendID) + " as file: " + str(backend_path + file))
            try:
                os.remove(backend_path + file)
                logger.info("Deleted backend with id: " + str(backendID))
                reloadOpenresty()
                return
            except OSError as e:
                logger.warning("Was not able to delete backend with id: " + str(backendID) + " ERROR: " + str(e))
                raise InternalServerError("Server was not able to delete this backend. Contact the admin.")
    raise NotFound("Backend was not found.")






