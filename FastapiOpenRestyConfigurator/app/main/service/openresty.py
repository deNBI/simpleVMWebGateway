"""
Service to reload openresty by starting a process.
"""

import asyncio
import logging

from FastapiOpenRestyConfigurator.app.main.config import get_settings

settings = get_settings()


logger = logging.getLogger("service")


async def reload_openresty():
    logger.info("Reloading openresty config after backend change.")

    try:
        if settings.CONTAINERIZED:
            cmd = ["openresty", "-s", "reload"]
        else:
            cmd = ["sudo", "openresty", "-s", "reload"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode().strip())

        logger.info("Reload successful.")

    except Exception as e:
        logger.exception(f"Was not able to reload OpenResty: {e}")
