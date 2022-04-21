"""
Helper/service functions regarding users of backends.
"""
import logging
import os
import shutil

from ..config import get_settings

logger = logging.getLogger("service")
settings = get_settings()


async def get_users(backend_id):
    user_id_path = f"{settings.FORC_USER_PATH}/{backend_id}"
    if not os.path.exists(user_id_path) and not os.access(user_id_path, os.R_OK):
        logger.exception(f"Not able to access configured user id path. Backend id: {backend_id}")
        return []
    return os.listdir(user_id_path)


async def add_user(backend_id, user_id):
    user_id_path = f"{settings.FORC_USER_PATH}/{backend_id}"
    user_file_name = f"{user_id}@elixir-europe.org"
    if not os.path.exists(user_id_path):
        try:
            os.mkdir(user_id_path)
        except OSError:
            logger.exception(f"Not able to create backend directory with id {backend_id}.")
            return 1
    if not os.access(user_id_path, os.W_OK):
        logger.exception(f"Not able to access user id path {user_id_path}.")
        return 2
    existing_users = os.listdir(user_id_path)
    for file in existing_users:
        if file == user_file_name:
            logger.info(f"User {user_id} already added to backend {backend_id}.")
            return 3
    with open(f"{user_id_path}/{user_file_name}", 'w') as userFile:
        userFile.write("")

    return 0


async def delete_user(backend_id, user_id):
    user_id_path = f"{settings.FORC_USER_PATH}/{backend_id}"
    user_file_name = f"{user_id}@elixir-europe.org"
    user_file_path = f"{user_id_path}/{user_file_name}"
    if not os.path.exists(user_id_path):
        logger.exception(f"No user folder found for backend: {backend_id}.")
        return 1
    if not os.path.exists(user_file_path):
        logger.exception(f"No user file {user_file_name} found for backend: {backend_id}.")
        return 1
    if not os.access(user_file_path, os.W_OK):
        logger.exception(f"Not able to access user id path {user_file_path}.")
        return 2
    logger.info(f"Deleting user {user_file_name} from backend {backend_id}.")
    try:
        existing_users = os.listdir(user_id_path)
        if len(existing_users) != 1:
            os.remove(user_file_path)
        else:
            await delete_all(backend_id)
        return 0
    except OSError:
        logger.exception(f"Not able to delete user {user_file_name} from backend {backend_id}.")
        return 3


async def delete_all(backend_id):
    user_id_path = f"{settings.FORC_USER_PATH}/{backend_id}"
    if not os.path.exists(user_id_path):
        logger.info(f"No user folder found for backend: {backend_id}.")
        return 1
    try:
        shutil.rmtree(user_id_path, ignore_errors=True)
        return 0
    except OSError:
        logger.exception(f"Not able to delete users for backend {backend_id}.")
        return 3
