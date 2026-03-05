import pytest
from unittest.mock import patch

from app.main.model.serializers import BackendOut

from app.main.views import backend as backend_views

from fastapi import HTTPException


@pytest.mark.asyncio
async def test_backend_update_auth_activate(backend_out_factory):
    backendOut = backend_out_factory(id=123, auth_enabled=True)


    with patch(
        "app.main.views.backend.update_backend_authorization",
        return_value=backendOut,
    ) as mock_update_backend_authorization:

        response: BackendOut = await backend_views.backend_update_auth(
            backend_id=123, body={"auth_enabled": True}, api_key="test"
        )

        assert response.id == 123
        assert response.auth_enabled is True
        mock_update_backend_authorization.assert_awaited_once_with(
            backend_id=123, auth_enabled=True
        )


@pytest.mark.asyncio
async def test_backend_update_auth_deactivate(backend_out_factory):
    backendOut = backend_out_factory(id=123, auth_enabled=False)

    with patch(
        "app.main.views.backend.update_backend_authorization",
        return_value=backendOut,
    ) as mock_update_backend_authorization:

        response: BackendOut = await backend_views.backend_update_auth(
            backend_id=123, body={"auth_enabled": False}, api_key="test"
        )

        assert response.id == 123
        assert response.auth_enabled is False
        mock_update_backend_authorization.assert_awaited_once_with(
            backend_id=123, auth_enabled=False
        )


@pytest.mark.asyncio
async def test_backend_update_auth_invalid_body():

    with pytest.raises(HTTPException) as not_boolean_exception:
        await backend_views.backend_update_auth(
            backend_id=123, body={"auth_enabled": "not a boolean"}, api_key="test"
        )
    assert not_boolean_exception.value.status_code == 422

    with pytest.raises(HTTPException) as empty_body_exception:
        await backend_views.backend_update_auth(backend_id=123, body={}, api_key="test")
    assert empty_body_exception.value.status_code == 422
