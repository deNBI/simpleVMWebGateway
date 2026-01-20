import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.main.views import backend as backend_views


@pytest.mark.parametrize(
    "exception_expected, backend_id, body",
    [
        (False, 123, {"auth_enabled": True}),
        # success cases
        (False, 123, {"auth_enabled": 1}),
        (False, 123, {"auth_enabled": 0}),
        (False, 123, {"auth_enabled": False}),
        # corrupted backend_id
        # TODO: more tests when there is further validation on backend_id
        (True, "not an int", {"auth_enabled": True}),
        (True, None, {"auth_enabled": True}),
        # corrupted body
        (True, 123, {"auth_enabled": "not a boolean"}),
        (True, 123, {"auth_enabled": ""}),
        (True, 123, {"differrent_value": True}),
        (True, 123, None),
        (True, 123, {}),
    ]
)
@pytest.mark.asyncio
async def test_backend_update_auth(exception_expected, backend_id, body):

    with patch(
        "app.main.service.backend.update_backend_authorization"
    ) as mock_update_backend_authorization:
        # success case
        try:
            await backend_views.backend_update_auth(
                backend_id = backend_id,
                body = body,
                api_key = object() # type: ignore[reportArgumentType]
            )
            mock_update_backend_authorization.assert_called_once_with(backend_id = 123, auth_enabled = True)
        # fail case
        except Exception:
            if exception_expected:
                mock_update_backend_authorization.assert_not_awaited()
        #if not exception_expected:
