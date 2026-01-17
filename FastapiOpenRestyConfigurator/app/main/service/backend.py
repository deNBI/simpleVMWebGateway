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

# format of filename saves information of BackendOut by this schema:
# {id}%{owner}%{location_url}%{template}%{template_version}%{auth_enabled}.conf
filename_regex = r"(\d*)%([a-z0-9\-\@.]*?)%([^%]*)%([^%]*)%([^%]*)%([01])\.conf"



# HELPER FUNCTIONS

def random_with_n_digits(n):
    # used for backend id generation (n=10), never starts with 0
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


# TODO: unlikely but potential error cause, if two users have same randomly generated user_key_url!
async def generate_suffix_number(user_key_url = None) -> str:
    if user_key_url is None:
        return "100"

    # look for backends with same user_key_url
    current_backends: List[BackendOut] = await get_backends()
    same_name_backend_ids = []
    for backend in current_backends:
        if backend.location_url.split("_")[0] == user_key_url:
            same_name_backend_ids.append(int(backend.location_url.split("_")[1]))
    if not same_name_backend_ids:
        return "100"

    # return highest found suffix number + 1 to iterate
    same_name_backend_ids.sort()
    highest_id = same_name_backend_ids[-1]
    if highest_id == 999:
        logger.warning("Reached max index number for requested user_key_url: " + user_key_url)
        raise InternalServerError("Reached max index number for requested user_key_url (limit=999).")
    return str(highest_id + 1)


def generate_backend_filename(backend: BackendOut) -> str:
    filename = f"{backend.id}%{backend.owner}%{backend.location_url}%{backend.template}%{backend.template_version}%{str(int(backend.auth_enabled))}.conf"
    return filename



# CORE GETTER FUNCTIONS

async def get_backends() -> List[BackendOut]:
    if not os.path.exists(settings.FORC_BACKEND_PATH) and not os.access(settings.FORC_BACKEND_PATH, os.W_OK):
        logger.error("Not able to access configured backend path.")
        return []
    if len(os.listdir(settings.FORC_BACKEND_PATH)) == 0:
        return []
    backend_path_filenames = os.listdir(settings.FORC_BACKEND_PATH)
    logger.info(f"Files in backend_path: {backend_path_filenames}")
    valid_backends = []
    for filename in backend_path_filenames:
        match = re.fullmatch(filename_regex, filename)
        if not match:
            if filename == "users" or filename == "scripts":
                continue
            logger.warning("Found a backend file with wrong naming, skipping it: " + str(filename))
            continue
        backend: BackendOut = BackendOut(
            id = match.group(1),
            owner = match.group(2),
            location_url = match.group(3),
            template = match.group(4),
            template_version = match.group(5),
            auth_enabled = bool(int(match.group(6))),
            file_path = os.path.join(settings.FORC_BACKEND_PATH, filename)
        )
        logger.debug(f"Discovered backend: {backend}")
        valid_backends.append(backend)
    return valid_backends


async def get_backend_by_id(backend_id: int) -> BackendOut:
    valid_backends: List[BackendOut] = await get_backends()
    for backend in valid_backends:
        if int(backend.id) == int(backend_id):
            return backend
    raise NotFound(f"Backend with id {backend_id} was not found.")


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


async def get_file_path_by_id(backend_id: int) -> str:
    backends: List[BackendOut] = await get_backends()
    logger.debug(f"Searching file path for backend id: {backend_id} in backends: {backends}")
    for backend in backends:
        if int(backend.id) == int(backend_id):
            logger.debug(f"Returning found file path for backend id: {backend_id}: {backend.file_path}")
            return backend.file_path
    raise NotFound(f"Backend with id {backend_id} not found.")



# FURTHER GETTER FUNCTIONS

def extract_proxy_pass(file_path) -> str | None:
    # proxy_pass consists of upstream_url with potential trailing path, see guacamole template
    with open(file_path, 'r') as file:
        content = file.read()

    match = re.search(r'proxy_pass\s+(http[^\s;]+);', content)

    if match:
        return match.group(1)
    else:
        logger.error(f"Could not extract proxy_pass from {file_path}")
        return None


def get_upstream_url(file_path) -> str | None:
    # extracts upstream_url from proxy_pass by removing trailing path, see guacamole template
    proxy_pass = extract_proxy_pass(file_path)
    if proxy_pass is None:
        return None

    # split and rejoin to remove trailing path to remove potential trailing path, unaffected if no trailing path
    upstream_url = "/".join(proxy_pass.split("/", 3)[:3])
    return upstream_url


def get_basekey_from_backend(backend: BackendOut) ->  str | None:
    try:
        base_key = backend.location_url.rsplit("_", 1)[0]
        logger.debug(f"Backend id: {backend.id}, Base key: {base_key}")
        return base_key
    except ValueError:
        logger.error(f"location_url has no suffix pattern: {backend.location_url}")
        return None



# CORE MUTATOR AND SERVICE FUNCTIONS

async def create_backend(payload: BackendIn, **kwargs) -> BackendTemp:
    logger.debug(f"Creating backend for owner: {payload.owner} with template: {payload.template} version: {payload.template_version}")

    # overwrite payload as BackendTemp for generate_backend_by_template()
    payload: BackendTemp = BackendTemp(**payload.model_dump())

    # generate or reuse backend id and suffix number
    payload, suffix_number = await set_backend_id_and_suffix_for(payload, **kwargs)

    # generate backend and location_url
    backend_file_contents = await generate_backend_by_template(payload, suffix_number)
    if not backend_file_contents:
        raise InternalServerError("Server was not able to template a new backend.")

    payload.location_url = f"{payload.user_key_url}_{suffix_number}"

    # check for duplicates and delete them before creating new backend
    if not await delete_duplicate_backends(payload.upstream_url):
        raise InternalServerError("Server was not able to delete duplicate backends before creating a new one.")

    # save BackendOut info in filename, create backend file in filesystem
    filename = generate_backend_filename(payload)

    with open(f"{settings.FORC_BACKEND_PATH}/{filename}", 'w') as backend_file:
        backend_file.write(backend_file_contents)

    # attempt to reload openresty
    await reload_openresty()
    return payload


async def delete_backend(backend_id) -> bool:
    backend_path_filenames = get_valid_backend_filenames()
    if not backend_path_filenames:
        return False

    matching_backend_filenames = filter_backend_filenames_by_id(backend_path_filenames, backend_id)

    amount_of_files = len(matching_backend_filenames)
    if amount_of_files == 0:
        raise NotFound(f"Backend {backend_id} was not found.")
    if amount_of_files > 1:
        logger.error(f"Found multiple backend files for backend id: {backend_id}, cannot delete.")
        raise InternalServerError("Server found multiple backend files, cannot delete.")

    filename = matching_backend_filenames[0]

    logger.info(f"Attempting to delete backend with id: {backend_id} as file: {settings.FORC_BACKEND_PATH}/{filename}")
    try:
        os.remove(f"{settings.FORC_BACKEND_PATH}/{filename}")
        logger.info(f"Deleted backend with id: {backend_id}")
        await reload_openresty()
        return True
    except OSError as e:
        logger.warning(f"Was not able to delete backend with id: {backend_id} ERROR: {e}")
        raise InternalServerError("Server was not able to delete this backend. Contact the admin.")


async def update_backend_authorization(backend_id: int, auth_enabled: bool) -> BackendOut | None:
    backend = await get_backend_by_id(backend_id)
    if not backend:
        return None

    # build temporary payload as BackendIn for create_backend()
    temp_payload = build_payload_for_auth_update(backend, auth_enabled)
    if not temp_payload:
        return None    

    # generate new backend contents with temp_payload, additional kwargs to persist backend_id and location_url
    new_contents = await create_backend(temp_payload, id=str(backend_id), location_url=backend.location_url)
    logger.debug(f"New contents: {new_contents}") 
    if not new_contents:
        logger.error("Templating returned empty result.")
        return None

    logger.info(f"Updated backend authorization to {temp_payload.auth_enabled} for backend id: {backend_id}")
    
    # convert BackendTemp to BackendOut for returning
    returning_backend = await convert_backend_temp_to_out(new_contents)

    return returning_backend



# HELPER FUNCTIONS FOR MUTATORS

async def set_backend_id_and_suffix_for(payload: BackendTemp, **kwargs) -> tuple[BackendTemp, str]:
    # override id and suffix if provided from update_backend_authorization()
    if 'id' in kwargs and 'location_url' in kwargs:
        payload = payload.model_copy(update={'id': str(kwargs.get('id'))})
        suffix_number = str(kwargs.get('location_url')).split("_")[1]
    else:
        payload.id = str(random_with_n_digits(10)) # TODO: should we refactor id: int? see delete_backend(). maybe it has something to do with int beginning with 0
        suffix_number = await generate_suffix_number(payload.user_key_url)
    logger.debug(f"Set backend id: {payload.id} with suffix number: {suffix_number}")
    return payload, suffix_number


async def delete_duplicate_backends(upstream_url: str) -> bool:
    # check for duplicates in ip and port and delete them 
    upstream_urls: Dict[str, List[BackendOut]] = await get_backends_upstream_urls()
    matching_urls_backends: List[BackendOut] = upstream_urls.get(upstream_url, [])
    success: bool = True
    for backend in matching_urls_backends:
        logger.info(f"Deleting existing Backend with same Upstream Url - {upstream_url}")
        if not await delete_backend(backend.id):
            success = False
    return success


async def convert_backend_temp_to_out(backend_temp: BackendTemp) -> BackendOut | None:
    # needed for returning backends to client
    try:
        backend_out = BackendOut(
            id = backend_temp.id,
            owner = backend_temp.owner,
            location_url = backend_temp.location_url,
            template = backend_temp.template,
            template_version = backend_temp.template_version,
            auth_enabled = backend_temp.auth_enabled,
            file_path = await get_file_path_by_id(backend_temp.id)
        )
        return backend_out
    except Exception as e:
        logger.error(f"Error converting BackendTemp to BackendOut: {e}")
        return None


def check_backend_path_file() -> bool:
    # check if backend path exists, is accessible and has files
    if not os.path.exists(settings.FORC_BACKEND_PATH) and not os.access(settings.FORC_BACKEND_PATH, os.W_OK):
        logger.error("Not able to access configured backend path.")
        return False
    if len(os.listdir(settings.FORC_BACKEND_PATH)) == 0:
        logger.error("No files found in backend path.")
        return False
    return True


def check_backend_path_file_naming(backend_path_filename: str) -> bool | None:
    # check for correct naming
        match = re.fullmatch(filename_regex, backend_path_filename)
        # skip files with wrong naming and log warning
        if not match:
            # exclude expected files from warning
            if backend_path_filename == "users" or backend_path_filename == "scripts":
                return None
            logger.warning(f"Found a backend file with wrong naming, skipping it: {backend_path_filename}")
            return None
        # return backend id of the correctly named file
        return True


def get_backend_path_filenames() -> List[str] | None:
    # get list of filenames in backend path
    if not check_backend_path_file():
        return None

    return os.listdir(settings.FORC_BACKEND_PATH)


def get_valid_backend_filenames() -> List[str] | None:

    # get list of valid backend filenames in backend path
    backend_path_filenames = get_backend_path_filenames()
    if not backend_path_filenames:
        return None

    # check naming, skip invalid filenames
    valid_backend_filenames = []
    for filename in backend_path_filenames:
        if not check_backend_path_file_naming(filename):
            continue

    # add valid filenames to list and return them
        valid_backend_filenames.append(filename)
    return valid_backend_filenames


def filter_backend_filenames_by_id(backend_path_filenames: List[str], backend_id: int) -> List[str]:
    # filter a list of backend filenames for matching backend id
    return [filename for filename in backend_path_filenames if int(filename.split("%")[0]) == int(backend_id)]


def build_payload_for_auth_update(backend: BackendOut, auth_enabled: bool) -> BackendIn | None:
    # fetch necessary info from existing BackendOut and build BackendIn payload for create_backend(), see update_backend_authorization()
    upstream_url = get_upstream_url(backend.file_path)
    base_key = get_basekey_from_backend(backend)
    if not upstream_url or not base_key:
        logger.error(f"Could not extract necessary info (upstream_url and base_key) from backend id: {backend.id} for updating authorization")
        return None

    # build new temporary payload as BackendIn
    try:
        temp_payload = BackendIn(
            owner = backend.owner,
            template = backend.template,
            template_version = backend.template_version,
            user_key_url = base_key, # add fetched fields
            upstream_url = upstream_url,
            auth_enabled = auth_enabled, # set new auth flag
        )
        return temp_payload
    except Exception as e:
        logger.error(f"Error building temp payload for backend update: {e}")
        return None
