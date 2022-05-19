"""
Template view.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import APIKey

from ..model.serializers import Template
from ..service import template as template_service
from ..util.auth import get_api_key

router = APIRouter()
logger = logging.getLogger("view")


@router.get("/templates", response_model=List[Template], tags=["Templates"])
async def get_templates(api_key: APIKey = Depends(get_api_key)):
    templates = await template_service.get_templates()
    if not templates:
        return []
    return templates


@router.get("/templates/{template_name}", response_model=List[Template], tags=["Templates"])
async def get_templates_by_name(template_name: str, api_key: APIKey = Depends(get_api_key)):
    if not template_name:
        raise HTTPException(status_code=400)
    templates = await template_service.get_templates(template_name)
    if not templates or len(templates) == 0:
        raise HTTPException(status_code=404, detail=f"No templates found for {template_name}")
    return templates


@router.get("/templates/{template_name}/{template_version}", response_model=Template, tags=["Templates"])
async def get_template_by_name_and_version(
        template_name: str,
        template_version: str,
        api_key: APIKey = Depends(get_api_key)
):
    if not template_name:
        raise HTTPException(status_code=400)
    if not template_version:
        raise HTTPException(status_code=400)
    templates = await template_service.get_templates(template_name, template_version)
    if not templates or len(templates) == 0 or len(templates) > 1:
        raise HTTPException(status_code=404, detail=f"No single template found for {template_name} {template_version}")
    return templates[0]
