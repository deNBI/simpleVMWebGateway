import os
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import SecretStr, validator, DirectoryPath
basedir = os.path.abspath(os.path.dirname(__file__))


class Settings(BaseSettings):
    """
    Settings object.
    Reads settings from .env file.
    """
    FORC_VERSION: str = '0.2'
    DEBUG: bool = True #temporary !!!!!!!!!
    LOG_LEVEL: str = "DEBUG" #temporary !!!!!!!!!
    FORC_API_KEY: SecretStr
    FORC_SECRET_KEY: SecretStr = 'my_precious_secret_key'
    FORC_BACKEND_PATH: DirectoryPath
    FORC_TEMPLATE_PATH: DirectoryPath
    FORC_USER_PATH: str = "users"

    @validator('FORC_USER_PATH', pre=True)
    def apply_backend_path(cls, v, values):
        """
        Validates forc user path, as it depends on forc backend path.
        :param v: Value for forc user path.
        :param values: Values already read for settings object.
        :return: Updated FORC_USER_PATH.
        """
        # := assigns and compares a value. (if a := b:) == (a = b; if a:)
        if FORC_BACKEND_PATH := values.get('FORC_BACKEND_PATH'):
            return f"{FORC_BACKEND_PATH}/{v}"
        else:
            # should only happen when there was an error with FORC_BACKEND_PATH
            return "/var/forc/backend_path/users"

    class Config:
        """
        Config for settings object.
        """
        # Enabled case sensitive for reading variables from .env file
        case_sensitive = True
        # Path to .env file
        env_file = ".env"
        # Encoding of .env file
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    """
    Function to get settings object.
    With lru_cache so object is initialized once and not everytime function is called.
    :return: Settings object.
    """
    return Settings()
