"""
Serializers for incoming and outgoing models.
"""
import re
import logging
from pydantic import BaseModel, Field, validator

logger = logging.getLogger("validation")
# Metadata for used tags.
tags_metadata = [
    {
        "name": "Backends",
        "description": "Operations with backends.",
    },
    {
        "name": "Templates",
        "description": "Operations with templates.",
    },
    {
        "name": "Users",
        "description": "Operations with users.",
    },
    {
        "name": "Miscellanous",
        "description": "Operations with miscellanous.",
    },
]

owner_regex = r'^[a-zA-Z0-9@.-]{30,}$'
user_key_url_regex = r"^[a-zA-Z0-9_-]{3,25}$"
upstream_url_regex = r"^(https?)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$"


class BackendBase(BaseModel):
    """
    Base class for backend.
    """
    owner: str = Field(
        ...,
        title="Owner",
        description="Owner of the backend",
        example="21894723853fhdzug92"
    )
    template: str = Field(
        ...,
        title="Template name",
        description="Name of the template the backend refers to.",
        example="rstudio"
    )
    template_version: str = Field(
        ...,
        title="Template version",
        description="Version of the template the backend refers to.",
        example="v04"
    )
    auth_enabled: bool = Field(
        True,
        title="Authorization for the research environment",
        description="If set to true, only the owner of the backend is allowed to access it.",
        example=False
    )

    @validator("owner")
    def owner_validation(cls, owner):
        """
        Validate owner string.
        :param owner: Value to assign to owner.
        :return: Value or AssertionError.
        """
        logger.info(f"Validate owner name -> {owner}")
        if re.fullmatch(owner_regex, owner):
            return owner
        else:
            raise AssertionError("The owner name can only contain alphabets, numerics, and '@' with at least 30 characters.")


class BackendIn(BackendBase):
    """
    Backend class which holds needed information for creating a backend.
    """
    user_key_url: str = Field(
        ...,
        title="Location URL prefix",
        description="Prefix of the location URL set by user.",
        example="myRstudio"
    )
    upstream_url: str = Field(
        ...,
        title="Upstream URL",
        description="Inject the full url (with protocol) for the real location of the backend service in the template.",
        example="http://192.168.0.1:8787/"
    )

    @validator("user_key_url")
    def user_key_url_validation(cls, v):
        """
        Validate user key url string.
        :param v: Value to assign to user key url.
        :return: Value or AssertionError.
        """
        assert re.fullmatch(user_key_url_regex, v), \
            "The user key url prefix can only contain alphabetics and numerics " \
            "with at least 3 and a maximum of 25 chars."
        return v

    @validator("upstream_url")
    def upstream_url_validation(cls, v):
        """
        Validate upstream_url string.
        :param v: Value to assign to upstream_url.
        :return: Value or AssertionError.
        """
        assert re.fullmatch(upstream_url_regex, v), \
            "This is not a valid upstream url. Example: http://129.70.168.5:3000"
        return v


class BackendOut(BackendBase):
    """
    Backend class which holds information needed when returning a backend.
    """
    id: int = Field(
        ...,
        title="ID",
        description="ID of the backend.",
        example=78621
    )
    location_url: str = Field(
        ...,
        title="Location URL",
        description="Protected reverse-proxy path which leads to specific backend.",
        example="myRstudio_103"
    )
    file_path:str=Field(
        None,
        title="File path of Backend",
        description=" Local File path of the backend",
    )


class BackendTemp(BackendIn, BackendOut):
    """
    Backend class to temporarily save information. Links BackendIn with BackendOut.
    """
    id: int = None
    owner: str = None
    location_url: str = None
    template: str = None
    template_version: str = None
    user_key_url: str = None
    upstream_url: str = None
    auth_enabled: bool = None


class Template(BaseModel):
    """
    Template model.
    """
    name: str
    version: str


class User(BaseModel):
    """
    User model.
    """

    user: str


class Util(BaseModel):
    """
    Util model.
    """
    version: str
