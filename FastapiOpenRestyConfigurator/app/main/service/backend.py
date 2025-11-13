"""
Helper/service functions regarding backends.
"""
import logging
import os
import re
from random import randint
from typing import List, Dict

from werkzeug.exceptions import NotFound, InternalServerError

from ..model.serializers import BackendOut, BackendIn, BackendTemp
from ..service.openresty import reload_openresty
from ..util.templating import generate_backend_by_template
from ..config import get_settings

logger = logging.getLogger("service")
settings = get_settings()

file_regex = r"(\d*)%([a-z0-9\-\@.]*?)%([^%]*)%([^%]*)%([^%]*)\.conf"


async def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


async def get_backends() -> List[BackendOut]:
    if not os.path.exists(settings.FORC_BACKEND_PATH) and not os.access(settings.FORC_BACKEND_PATH, os.W_OK):
        logger.error("Not able to access configured backend path.")
        return []
    if len(os.listdir(settings.FORC_BACKEND_PATH)) == 0:
        return []
    backend_path_files = os.listdir(settings.FORC_BACKEND_PATH)
    logger.info(backend_path_files)
    valid_backends = []
    for file in backend_path_files:
        match = re.fullmatch(file_regex, file)
        if not match:
            if file == "users" or file == "scripts":
                continue
            logger.warning("Found a backend file with wrong naming, skipping it: " + str(file))
            continue
        backend: BackendOut = BackendOut(
            id=match.group(1),
            owner=match.group(2),
            location_url=match.group(3),
            template=match.group(4),
            template_version=match.group(5),
            file_path=os.path.join(settings.FORC_BACKEND_PATH, file)
        )
        valid_backends.append(backend)
    return valid_backends


async def get_backend_by_id(backend_id: int) -> BackendOut:
    valid_backends: List[BackendOut] = await get_backends()
    for backend in valid_backends:
        if int(backend.id) == int(backend_id):
            return backend
    raise NotFound(f"Backend {backend_id} was not found.")


async def get_backends_upstream_urls() -> Dict[str, List[BackendOut]]:
    valid_backends: List[BackendOut] = await get_backends()
    upstream_urls = {}

    for backend in valid_backends:
        upstream_url = extract_proxy_pass(backend.file_path)
        if upstream_url:
            if upstream_url not in upstream_urls:
                upstream_urls[upstream_url] = []
            upstream_urls[upstream_url].append(backend)

    return upstream_urls


def extract_proxy_pass(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    match = re.search(r'proxy_pass\s+(http[^\s;]+);', content)

    if match:
        return match.group(1)
    else:
        return None


async def generate_suffix_number(user_key_url):
    current_backends: List[BackendOut] = await get_backends()
    same_name_backend_ids = []

    for backend in current_backends:
        if backend.location_url.split("_")[0] == user_key_url:
            same_name_backend_ids.append(int(backend.location_url.split("_")[1]))

    if not same_name_backend_ids:
        return "100"

    same_name_backend_ids.sort()
    highest_id = same_name_backend_ids[-1]
    if highest_id == 999:
        logger.warning("Reached max index number for requested user_key_url: " + user_key_url)
        raise InternalServerError("Reached max index number for requested user_key_url (limit=999).")

    return str(highest_id + 1)


async def create_backend(payload: BackendIn, **kwargs):
    payload: BackendTemp = BackendTemp(**payload.dict())
    suffix_number = await generate_suffix_number(payload.user_key_url)

    payload.id = str(await random_with_n_digits(10))
    if 'id' in kwargs: # override id and suffix if provided
        payload = payload.copy(update={'id': str(kwargs.get('id'))})
        suffix_number = str(kwargs.get('location_url')).split("_")[1]

    backend_file_contents = await generate_backend_by_template(payload, suffix_number)
    if not backend_file_contents:
        raise InternalServerError("Server was not able to template a new backend.")

    payload.location_url = f"{payload.user_key_url}_{suffix_number}"

    # check for duplicated in ip and port:
    upstream_urls: Dict[str, List[BackendOut]] = await get_backends_upstream_urls()
    matching_urls_backends: List[BackendOut] = upstream_urls.get(payload.upstream_url, [])
    for backend in matching_urls_backends:
        logger.info(f"Deleting existing Backend with same Upstream Url - {payload.upstream_url}")
        await delete_backend(backend.id)

    # create backend file in filesystem
    filename = f"{payload.id}%{payload.owner}%{payload.location_url}%{payload.template}%{payload.template_version}.conf"

    with open(f"{settings.FORC_BACKEND_PATH}/{filename}", 'w') as backend_file:
        backend_file.write(backend_file_contents)

    # attempt to reload openrest
    await reload_openresty()
    return payload


async def delete_backend(backend_id) -> bool:
    if not os.path.exists(settings.FORC_BACKEND_PATH) and not os.access(settings.FORC_BACKEND_PATH, os.W_OK):
        logger.error("Not able to access configured backend path.")
        return False
    if len(os.listdir(settings.FORC_BACKEND_PATH)) == 0:
        return False
    backend_path_files = os.listdir(settings.FORC_BACKEND_PATH)
    for file in backend_path_files:
        match = re.fullmatch(file_regex, file)
        if not match:
            if file == "users" or file == "scripts":
                continue
            logger.warning(f"Found a backend file with wrong naming, skipping it: {file}")
            continue
        if int(match.group(1)) == int(backend_id):
            logger.info(f"Attempting to delete backend with id: {backend_id} as file: {settings.FORC_BACKEND_PATH}/{file}")
            try:
                os.remove(f"{settings.FORC_BACKEND_PATH}/{file}")
                logger.info(f"Deleted backend with id: {backend_id}")
                await reload_openresty()
                return True
            except OSError as e:
                logger.warning(f"Was not able to delete backend with id: {backend_id} ERROR: {e}")
                raise InternalServerError("Server was not able to delete this backend. Contact the admin.")
    raise NotFound(f"Backend {backend_id} was not found.")


async def update_backend_authorization(backend_id: int, auth_enable: bool):
    backend = await get_backend_by_id(backend_id)

    # extract upstream_url from file
    upstream_url = extract_proxy_pass(backend.file_path)
    if not upstream_url:
        logger.error(f"Could not extract proxy_pass from {backend.file_path}")
        return False

    # get existing location_url and user_key_url
    try:
        base_key, suffix = backend.location_url.rsplit("_", 1)
    except ValueError:
        logger.error(f"location_url has no suffix pattern: {backend.location_url}")
        return False
    logger.info(f"Base key: {base_key}, Suffix: {suffix}")

    # build new temp payload
    try:
        temp_payload = BackendIn(
            owner=backend.owner,
            template=backend.template,
            template_version=backend.template_version,
            user_key_url=base_key,
            upstream_url=upstream_url,
            auth_enabled=auth_enable, # set new auth flag
        )
    except Exception as e:
        logger.error(f"Error building temp payload for backend update: {e}")
        return False
    logger.info(f"temp_payload: {temp_payload}") 

    # generate new backend contents with additional kwargs to persist backend_id and location_url
    new_contents = await create_backend(temp_payload, id=str(backend_id), location_url=backend.location_url)
    logger.info(f"New contents: {new_contents}") 
    if not new_contents:
        logger.error("Templating returned empty result.")
        return False
    return new_contents
