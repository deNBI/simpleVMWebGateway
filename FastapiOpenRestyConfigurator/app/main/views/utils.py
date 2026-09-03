"""
Util view.
"""
import logging

from fastapi import APIRouter

from ..model.serializers import Util
from ..config import get_settings

router = APIRouter()
logger = logging.getLogger("view")


@router.get("/utils", response_model=Util, tags=["Miscellanous"])
async def get_version():
    settings = get_settings()
    return Util(version=settings.FORC_VERSION)


@router.get("/health", tags=["Miscellanous"])
async def get_health():
    return {"status": "ok"}
