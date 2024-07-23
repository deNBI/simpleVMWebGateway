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


async def get_backends_upstream_urls() -> Dict[str, List[str]]:
    valid_backends: List[BackendOut] = await get_backends()
    upstream_urls = {}

    for backend in valid_backends:
        upstream_url = extract_proxy_pass(backend.file_path)
        if upstream_url:
            if upstream_url not in upstream_urls:
                upstream_urls[upstream_url] = []
            upstream_urls[upstream_url].append(backend.id)

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


async def create_backend(payload: BackendIn):
    payload: BackendTemp = BackendTemp(**payload.dict())
    suffix_number = await generate_suffix_number(payload.user_key_url)

    payload.id = str(await random_with_n_digits(10))

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
    raise NotFound("Backend was not found.")
