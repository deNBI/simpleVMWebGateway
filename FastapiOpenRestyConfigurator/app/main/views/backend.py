"""
Backend view.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.openapi.models import APIKey
from werkzeug.exceptions import NotFound, InternalServerError
from werkzeug.utils import secure_filename

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


@router.post(
    "/backends/{backend_id}/auth/",
    response_model=BackendOut,
    tags=["Backends"],
    summary="Set owner authorization to true/false for an existing backend."
)
async def backend_update_auth(backend_id: int, body: dict = Body(...), api_key: APIKey = Depends(get_api_key)):
    # process inputs TODO: should we validate further?
    backend_id = int(secure_filename(str(backend_id))) # TODO: are secure_filename and str necessary? validation?
    enable_auth = bool(body.get("auth_enabled", None))
    logger.debug(f"Attempting to update backend authorization to {enable_auth} for backend id: {backend_id}")

    # check inputs and raise error
    if backend_id is None or enable_auth is None or not isinstance(enable_auth, bool):
        logger.error(
            f"Received faulty data. backend_id: {backend_id}, auth_enabled: {enable_auth}, {type(enable_auth)}")
        raise HTTPException(status_code=422, detail =
                            f"auth_enabled is required and must be a boolean, \
                                backend_id: {backend_id}, auth_enabled: {enable_auth}, {type(enable_auth)}")
    # forward to service layer
    else:
        try:
            return await backend_service.update_backend_authorization(backend_id, enable_auth)
        # TODO: the exceptions are raised in the service layer already, do we still need this?
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Backend with id {backend_id} not found.")
        except InternalServerError:
            raise HTTPException(status_code=500, detail="Internal server error.")


@router.get(
    "/backends/{backend_id}",
    response_model=BackendOut,
    tags=["Backends"],
    summary="Get a backend by id."
)
async def get_backend(backend_id: int, api_key: APIKey = Depends(get_api_key)):
    backend_id = int(secure_filename(str(backend_id)))
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
        backend_id = int(secure_filename(str(backend_id)))
        await backend_service.delete_backend(backend_id)
        await user_service.delete_all(backend_id)
    except NotFound:
        return JSONResponse(status_code=404, content={"error": f"Backend with {backend_id} not found."})
    except InternalServerError as e:
        logger.exception(e)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
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
