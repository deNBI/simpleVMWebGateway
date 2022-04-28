"""
User view.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import APIKey

from ..model.serializers import User
from ..service import user as user_service
from ..util.auth import get_api_key

router = APIRouter()
logger = logging.getLogger("view")


@router.get("/users/{backend_id}", response_model=List[User], tags=["Users"])
async def get_users_for_backend(backend_id: str, api_key: APIKey = Depends(get_api_key)):
    users = await user_service.get_users(backend_id)
    logger.info(users)
    if not users:
        return []
    return users


@router.post("/users/{backend_id}", response_model=User, tags=["Users"])
async def add_user_to_backend(backend_id: str, new_user: User, api_key: APIKey = Depends(get_api_key)):
    res = await user_service.add_user(backend_id, new_user.user)
    if res != 0:
        raise HTTPException(status_code=500, detail=f"Could not add {new_user} to {backend_id}.")
    else:
        return new_user


@router.delete("/users/{backend_id}", tags=["Users"])
async def delete_user_from_backend(backend_id: str, user: User, api_key: APIKey = Depends(get_api_key)):
    await user_service.delete_user(backend_id, user.user)
    return {"message": f"User {user} deleted from {backend_id}."}
