import pytest
from unittest.mock import patch

from app.main.model.serializers import BackendOut

from app.main.service import backend as backend_service

from werkzeug.exceptions import NotFound

file_path_example_1 = "/var/forc/backend_path/1234567890%testuser%animal_100%testtemplate%v01%0.conf"
file_path_example_2 = "/var/forc/backend_path/9876543210%otheruser%cat_200%othertemplate%v02%1.conf"


@pytest.mark.asyncio
async def test_get_backend_by_id():

    with patch(
        "app.main.service.backend.get_backends",
        return_value = [BackendOut(backend_id = 123), BackendOut(backend_id = 456)]
    ) as mock_get_backends:

        response: BackendOut = await backend_service.get_backend_by_id(123)

        assert response.backend_id == 123
        mock_get_backends.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_backend_by_id_not_found():

    with pytest.raises(NotFound):
        with patch(
            "app.main.service.backend.get_backends",
            return_value = [BackendOut(backend_id = 123), BackendOut(backend_id = 456)]
        ) as mock_get_backends:

            await backend_service.get_backend_by_id(789)
            mock_get_backends.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_filepath_by_id():

    with patch(
        "app.main.service.backend.get_backends",
        return_value = [
            BackendOut(
                backend_id = 1234567890,
                file_path = file_path_example_1),
            BackendOut(
                backend_id = 9876543210,
                file_path = file_path_example_2)]
    ) as mock_get_backends:

        response: str = await backend_service.get_file_path_by_id(1234567890)

        assert response == file_path_example_1
        mock_get_backends.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_filepath_by_id_not_found():

    with pytest.raises(NotFound):
        with patch(
            "app.main.service.backend.get_backends",
            return_value = BackendOut(backend_id = 1234567890)
        ) as mock_get_backends:
            await backend_service.get_file_path_by_id(9876543210)
            mock_get_backends.assert_awaited_once()

"""
@pytest.mark.asyncio
async def test_create_backend(): # check kwargs payload id and suffix number at the end

    with patch(
        "app.main.service.backend.generate_suffix_number",
        return_value = 111
    ) as mock_generate_suffix_number, patch(
        "app.main.service.backend.random_with_n_digits",
        return_value = 9876543210
    ) as mock_random_with_n_digits, patch(
        "app.main.service.backend.generate_backend_by_template",


@pytest.mark.asyncio
async def test_update_backend_authorization_activate():

"""
