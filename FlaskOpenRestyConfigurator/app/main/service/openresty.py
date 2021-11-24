import os
import logging


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def reloadOpenresty():
    logger.info("Reloading openresty config after backend change.")
    try:
        os.popen("sudo openresty -s reload")
        logger.info("Reload succesful.")
    except OSError as e:
        logger.error("Was not able to reload OpenResty: " + str(e))
