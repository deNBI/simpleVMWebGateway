import logging
import os
import shutil

from app.main.service.openresty import reloadOpenresty
from ..config import user_path

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_users(backend_id):
    user_id_path = "{0}/{1}".format(user_path, backend_id)
    if not os.path.exists(user_id_path) and not os.access(user_id_path, os.R_OK):
        logger.error("Not able to access configured user id path. Backend id: {0}".format(backend_id))
        return []
    return os.listdir(user_id_path)


def add_user(backend_id, user_id):
    user_id_path = "{0}/{1}".format(user_path, backend_id)
    user_file_name = "{0}".format(user_id)
    if not os.path.exists(user_id_path):
        try:
            os.mkdir(user_id_path)
        except OSError:
            logger.error("Not able to create backend directory with id {0} for user.".format(backend_id))
            return 1
    if not os.access(user_id_path, os.W_OK):
        logger.error("Not able to access configured user id path.")
        return 2
    existing_users = os.listdir(user_id_path)
    for file in existing_users:
        if file == user_file_name:
            logger.info("User already added to backend.")
            return 3
    with open(user_id_path + "/" + user_file_name, 'w') as userFile:
        userFile.write("")

    # attempt to reload openrest
    reloadOpenresty()
    return 0


def delete_user(backend_id, user_id):
    user_id_path = "{0}/{1}".format(user_path, backend_id)
    user_file_name = "{0}".format(user_id)
    user_file_path = "{0}/{1}".format(user_id_path, user_file_name)
    if not os.path.exists(user_id_path):
        logger.error("No user folder found for backend: {0}.".format(backend_id))
        return 1
    if not os.path.exists(user_file_path):
        logger.error("No user file {1} found for backend: {0}.".format(backend_id, user_file_name))
        return 1
    if not os.access(user_file_path, os.W_OK):
        logger.error("Not able to access configured user id path.")
        return 2
    logger.info("Deleting user {0} from backend {1}.".format(user_file_name, backend_id))
    try:
        existing_users = os.listdir(user_id_path)
        if len(existing_users) != 1:
            os.remove(user_file_path)
        else:
            delete_all(backend_id)
        reloadOpenresty()
        return 0
    except OSError:
        logger.error("Not able to delete user {1} from backend {0}.".format(backend_id, user_file_name))
        return 3


def delete_all(backend_id):
    user_id_path = "{0}/{1}".format(user_path, backend_id)
    if not os.path.exists(user_id_path):
        logger.info("No user folder found for backend: {0}.".format(backend_id))
        return 1
    try:
        shutil.rmtree(user_id_path, ignore_errors=True)
        return 0
    except OSError:
        logger.error("Not able to delete users for backend {0}.".format(backend_id))
        return 3
