"""
Backend view.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.models import APIKey
from werkzeug.exceptions import NotFound, InternalServerError

from ..model.serializers import BackendIn, BackendOut
from ..service import backend as backend_service
from ..service import user as user_service
from ..util.auth import get_api_key

router = APIRouter()
logger = logging.getLogger("view")


@router.get(
    "/backends",
    response_model=List[BackendOut],
    tags=["Backends"],
    summary="List all created backends."
)
async def list_backends(api_key: APIKey = Depends(get_api_key)):
    backends = await backend_service.get_backends()
    if not backends:
        return []
    return backends


@router.post(
    "/backends",
    response_model=BackendOut,
    tags=["Backends"],
    summary="Create a new backend."
)
async def create_backend(backend_in: BackendIn, api_key: APIKey = Depends(get_api_key)):
    if backend_in:
        backend = await backend_service.create_backend(backend_in)
        return backend
    else:
        raise HTTPException(status_code=400)


@router.get(
    "/backends/{backend_id}",
    response_model=BackendOut,
    tags=["Backends"],
    summary="Get a backend by id."
)
async def get_backend(backend_id: int, api_key: APIKey = Depends(get_api_key)):
    backends = await backend_service.get_backends()
    if not backends:
        raise HTTPException(status_code=404, detail="No backends found.")
    for backend in backends:
        if int(backend.id) == int(backend_id):
            return backend
    raise HTTPException(status_code=404, detail="No backend found.")


@router.delete(
    "/backends/{backend_id}",
    tags=["Backends"],
    summary="Delete a backend by id.",
    responses={
        404: {"description": "Backend was not found."},
        500: {"description": "Internal server error."}
    }
)
async def delete_backend(backend_id: int, api_key: APIKey = Depends(get_api_key)):
    try:
        await backend_service.delete_backend(backend_id)
        await user_service.delete_all(backend_id)
    except NotFound:
        return JSONResponse(status_code=404)
    except InternalServerError as e:
        logger.exception(e)
        return JSONResponse(status_code=500)
    return {"message": f"Backend deleted: {backend_id}."}


@router.get(
    "/backends/byOwner/{owner}",
    response_model=List[BackendOut],
    tags=["Backends"],
    summary="Get all backends by an owner."
)
async def get_backends_by_owner(owner: str, api_key: APIKey = Depends(get_api_key)):
    backends = await backend_service.get_backends() # noqa
    if not backends:
        raise HTTPException(status_code=404, detail="No Backends found.")
    backends_by_owner = []
    for backend in backends:
        if backend.owner == owner:
            backends_by_owner.append(backend)
    if backends_by_owner:
        return backends_by_owner
    else:
        raise HTTPException(status_code=404, detail=f"No Backends found for {owner}.")


@router.get(
    "/backends/byTemplate/{template}",
    response_model=List[BackendOut],
    tags=["Backends"],
    summary="Get all backends by template."
)
async def get_backends_by_template(template: str, api_key: APIKey = Depends(get_api_key)):
    backends = await backend_service.get_backends() # noqa
    if not backends:
        raise HTTPException(status_code=404, detail="No Backends found.")
    backends_by_template = []
    for backend in backends:
        if backend.template == template:
            backends_by_template.append(backend)
    if backends_by_template:
        return backends_by_template
    else:
        raise HTTPException(status_code=404, detail=f"No Backends found for template {template}.")
