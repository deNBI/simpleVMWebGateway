"""
Service to reload openresty by starting a process.
"""
import os
import logging


logger = logging.getLogger("service")


async def reload_openresty():
    logger.info("Reloading openresty config after backend change.")
    try:
        os.popen("sudo openresty -s reload")
        logger.info("Reload successful.")
    except OSError as e:
        logger.exception(f"Was not able to reload OpenResty: {e}")
