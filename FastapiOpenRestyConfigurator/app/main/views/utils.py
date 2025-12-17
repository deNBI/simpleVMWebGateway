"""
Util view.
"""
import logging

from fastapi import APIRouter

from ..model.serializers import Util
from ..config import get_settings

router = APIRouter()
logger = logging.getLogger("view")
settings = get_settings()


@router.get("/utils", response_model=Util, tags=["Miscellanous"])
async def get_version():
    return Util(version=settings.FORC_VERSION)
