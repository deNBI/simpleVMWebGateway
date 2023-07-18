"""
File containing logging configuration.
"""
from ..config import get_settings

settings = get_settings()

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(levelprefix)s %(asctime)s - %(name)s - %(funcName)s:%(lineno)d]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "internal": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "view": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "service": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "validation": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "util": {"handlers": ["default"], "level": settings.LOG_LEVEL}
    },
}
