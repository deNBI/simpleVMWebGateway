import os
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import SecretStr, field_validator, DirectoryPath
from pydantic import field_validator, ValidationInfo

basedir = os.path.abspath(os.path.dirname(__file__))


class Settings(BaseSettings):
    """
    Settings object.
    Reads settings from .env file.
    """

    FORC_VERSION: str = "0.2"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    FORC_API_KEY: SecretStr
    FORC_SECRET_KEY: SecretStr = "my_precious_secret_key"
    FORC_BACKEND_PATH: DirectoryPath
    FORC_TEMPLATE_PATH: DirectoryPath
    FORC_USER_PATH: str = "users"
    CONTAINERIZED: bool = False

    @field_validator("FORC_USER_PATH", mode="before")
    @classmethod
    def apply_backend_path(cls, v, info: ValidationInfo):
        """
        Validates forc user path, as it depends on forc backend path.
        :param v: Value for forc user path.
        :param info: Validation context containing already validated fields.
        :return: Updated FORC_USER_PATH.
        """
        forc_backend_path = info.data.get("FORC_BACKEND_PATH")

        if forc_backend_path:
            return f"{forc_backend_path}/{v}"

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
