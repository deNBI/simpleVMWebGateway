import os, re
from ..config import backend_path
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest
from .openresty import reloadOpenresty
from ..util.validate import validatePostBackendContent
from ..util import templating
import logging
from random import randint

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileRegex = r"(\d*)%([a-z0-9]*)%([^%]*)%([^%]*)%([^%]*)\.conf"


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)



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


def generateSuffixNumber(user_key_url):
    currentBackends = getBackends()
    sameNameBackendIDs = []

    for backend in currentBackends:
        if backend['location_url'].split('_')[0] == user_key_url:
            sameNameBackendIDs.append(int(backend['location_url'].split('_')[1]))

    if not sameNameBackendIDs:
        return '100'

    sameNameBackendIDs.sort()
    highestID = sameNameBackendIDs[-1]
    if highestID == 999:
        logger.warning("Reached max index number for requested user_key_url: " + user_key_url)
        raise InternalServerError("Reached max index number for requested user_key_url (limit=999).")

    return str(highestID + 1)




def createBackend(payload):
    # field validation happens beforehand by restplus, this checks semantics
    validationStatus = validatePostBackendContent(payload)
    if "error" in validationStatus:
        raise BadRequest("ValidationError: " + str(validationStatus['error']))
    suffixNumber = generateSuffixNumber(payload['user_key_url'])

    backendFileContents = templating.generateBackendByTemplate(payload, suffixNumber)
    if not backendFileContents:
        raise InternalServerError("Server was not able to template a new backend.")

    payload['id'] = str(random_with_N_digits(10))
    payload['location_url'] = payload['user_key_url'] + "_" + suffixNumber

    #check for duplicates in filesystem
    backendPathFiles = os.listdir(backend_path)
    for file in backendPathFiles:
        match = re.fullmatch(fileRegex, file)
        if match.group(1) == payload['id'] or match.group(3) == payload['location_url']:
            logger.error("Tried to create duplicate backend: " + payload['id'] + " and " + payload['location_url'])
            raise InternalServerError("Server tried to create duplicate backend.")


    #create backend file in filesystem
    filename = "{0}%{1}%{2}%{3}%{4}.conf".format(payload['id'],
                                                 payload['owner'],
                                                 payload['location_url'],
                                                 payload['template'],
                                                 payload['template_version'])

    with open(backend_path + filename, 'w') as backendFile:
        backendFile.write(backendFileContents)

    # attempt to reload openrest
    reloadOpenresty()
    return payload



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






