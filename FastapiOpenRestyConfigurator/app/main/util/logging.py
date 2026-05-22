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
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/all_forc_logs.log",
            "maxBytes": 25 * 1024 * 1024, # 25 megabytes
            "backupCount": 4
        },
    },
    "loggers": {
        "internal": {"handlers": ["default", "file"], "level": settings.LOG_LEVEL},
        "view": {"handlers": ["default", "file"], "level": settings.LOG_LEVEL},
        "service": {"handlers": ["default", "file"], "level": settings.LOG_LEVEL},
        "validation": {"handlers": ["default", "file"], "level": settings.LOG_LEVEL},
        "util": {"handlers": ["default", "file"], "level": settings.LOG_LEVEL}
    },
}
