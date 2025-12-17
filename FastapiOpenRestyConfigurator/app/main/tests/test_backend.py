import pytest
from unittest.mock import patch

from app.main.model.serializers import BackendOut

from app.main.views import backend as backend_views
from app.main.service import backend as backend_service

# views/backend.py

@pytest.mark.asyncio
async def test_backend_update_auth_activate():

    with patch(
        "app.main.views.backend.backend_service.update_backend_authorization",
        return_value = BackendOut(
            id = 1,
            auth_enabled = True,
        )
    ) as mock_update_backend_authorization:

        res: BackendOut = await backend_views.backend_update_auth(
            backend_id = 1,
            body = {"auth_enabled": True},
            api_key = "test"
        )

        assert res.id == 1
        assert res.auth_enabled is True
        mock_update_backend_authorization.assert_awaited_once_with(backend_id = 1, auth_enabled = True)

@pytest.mark.asyncio
async def test_backend_update_auth_deactivate():

    with patch(
        "app.main.views.backend.backend_service.update_backend_authorization",
        return_value = BackendOut(
            id = 1,
            auth_enabled = False,
        )
    ) as mock_update_backend_authorization:

        res: BackendOut = await backend_views.backend_update_auth(
            backend_id = 1,
            body = {"auth_enabled": False},
            api_key = "test"
        )

        assert res.id == 1
        assert res.auth_enabled is False
        mock_update_backend_authorization.assert_awaited_once_with(backend_id = 1, auth_enabled = False)


# service/backend.py

@pytest.mark.asyncio
async def test_update_backend_authorization_activate():

    with patch(
        "app.main.service.backend.get_backend_by_id",
        return_value = BackendOut(
            id = 1234567890,
            auth_enabled = False,
            owner = "testuser",
            template = "testtemplate",
            template_version = "v01",
            location_url = "animal_100",
            file_path = "/var/forc/backend_path/1234567890%testuser%animal_100%testtemplate%v01%0.conf"
        )
    ) as mock_get_backend_by_id, patch(
        "app.main.service.backend.create_backend",
        return_value = BackendOut(
            id = 1234567890,
            auth_enabled = True,
            owner = "testuser",
            template = "testtemplate",
            template_version = "v01",
            location_url = "animal_100",
            file_path = "/var/forc/backend_path/1234567890%testuser%animal_100%testtemplate%v01%1.conf"
        )
    ) as mock_create_backend, patch(
        "app.main.service.backend.extract_proxy_pass",
        return_value = "https://example.com:1000/"
    ) as mock_extract_proxy_pass, patch(
        "app.main.service.backend.get_file_path_by_id",
        return_value = "/var/forc/backend_path/1234567890%testuser%animal_100%testtemplate%v01%0.conf"
    ) as mock_get_file_path_by_id:

        res: BackendOut = await backend_service.update_backend_authorization(
            backend_id = 1234567890,
            auth_enabled = True,
        )

        assert res.id == 1234567890
        assert res.auth_enabled is True

        mock_get_backend_by_id.assert_awaited_once_with(backend_id = 1234567890)
        mock_get_file_path_by_id.assert_called_once_with(backend_id = 1234567890)
        mock_extract_proxy_pass.assert_called_once()
        mock_create_backend.assert_awaited_once()

def test_get_backend_by_id():
    patch(
        "app.main.service.backend.get_backends",
        return_value = [BackendOut(id = 1)]
    ):
        assert await backend_service.get_backend_by_id(1).id == 1