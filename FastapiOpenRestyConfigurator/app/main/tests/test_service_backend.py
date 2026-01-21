import pytest
from unittest.mock import patch

from app.main.model.serializers import BackendOut

from app.main.service import backend as backend_service

from werkzeug.exceptions import NotFound

file_path_example_1 = "/var/forc/backend_path/1234567890%testuser%animal_100%testtemplate%v01%0.conf"
file_path_example_2 = "/var/forc/backend_path/9876543210%otheruser%cat_200%othertemplate%v02%1.conf"

# TEST DATA

# backend test cases: (exception_expected, filename, backend), see test_generate_backend_filename()
test_backends = [
    (False, "123%testuser%dog_100%testtemplate%v01%0.conf",
         BackendOut.model_construct(
            id = 123,
            owner = "testuser",
            location_url = "dog_100",
            template = "testtemplate",
            template_version = "v01",
            auth_enabled = False
        )),
        (False, None,
         BackendOut.model_construct(
            id = None,
            owner = "otheruser",
            location_url = "cat_200",
            template = "othertemplate",
            template_version = "v02",
            auth_enabled = True
        )),
        (False, None,
         BackendOut.model_construct(
            id = 123,
            owner = None,
            location_url = "cat_200",
            template = "othertemplate",
            template_version = "v02",
            auth_enabled = True
        )),
        (False, None,
         BackendOut.model_construct(
            id = 123,
            owner = "otheruser",
            location_url = None,
            template = "othertemplate",
            template_version = "v02",
            auth_enabled = True
        )),
        (False, None,
         BackendOut.model_construct(
            id = 123,
            owner = "otheruser",
            location_url = "cat_200",
            template = None,
            template_version = "v02",
            auth_enabled = True
        )),
        (False, None,
         BackendOut.model_construct(
            id = 123,
            owner = "otheruser",
            location_url = "cat_200",
            template = "othertemplate",
            template_version = None,
            auth_enabled = True
        )),
        (False, None,
         BackendOut.model_construct(
            id = 123,
            owner = "otheruser",
            location_url = "cat_200",
            template = "othertemplate",
            template_version = "v02",
            auth_enabled = None
        ))
    ]


# HELPER FUNCTIONS

@pytest.mark.parametrize(
    "exception_expected, user_key_url",
    [
        (False, None),
        (False, 200),
        (True, 999),
        (True, -10),
        (True, None),
        (True, "not an int")
    ]
)
@pytest.mark.asyncio
async def test_generate_suffix_number():
    


@pytest.mark.parametrize(
    "exception_expected, filename, backend",
    test_backends
)
@pytest.mark.asyncio
async def test_generate_backend_filename(exception_expected, filename, backend):
    ...
    assert filename == f"{backend.id}%{backend.owner}%{backend.location_url}%{backend.template}%{backend.template_version}%{str(int(backend.auth_enabled))}.conf"



# CORE GETTER FUNCTIONS

@pytest.mark.parametrize(
    "exception_expected, backend_id",
    [
        (False, 123),
        (True, None)
    ]
)
@pytest.mark.asyncio
async def test_get_backend_by_id(exception_expected, backend_id):

    with patch(
        "app.main.service.backend.get_backends",
        return_value = [BackendOut.model_construct(backend_id = backend_id), BackendOut.model_construct(backend_id = 456)]
    ) as mock_get_backends:

        try:
            response: BackendOut = await backend_service.get_backend_by_id(backend_id)
            # success case
            if not exception_expected:
                assert response.id == backend_id
                mock_get_backends.assert_awaited_once()
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e


@pytest.mark.parametrize(
    "exception_expected, backend_id",
    [
        (False, 123),
        (True, None)
    ]
)
@pytest.mark.asyncio
async def test_get_filepath_by_id(exception_expected, backend_id):

    with patch(
        "app.main.service.backend.get_backend_by_id",
        return_value = BackendOut.model_construct(backend_id = backend_id, file_path = "test_path")
    ) as mock_get_backend_by_id:

        try:
            filepath: str = await backend_service.get_file_path_by_id(backend_id)
            # success case
            if not exception_expected:
                assert filepath == "test_path"
                mock_get_backend_by_id.assert_awaited_once()
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e



# FURTHER GETTER FUNCTIONS

@pytest.mark.parametrize(
    "exception_expected, proxy_pass",
    [
        (False, "http://1.1.1.1:1000/guacamole/"),
        (True, None)
    ]
)
@pytest.mark.asyncio
async def test_get_upstream_url(exception_expected, proxy_pass):
    with patch(
        "app.main.service.backend.extract_proxy_pass",
        return_value = proxy_pass
    ) as mock_extract_proxy_pass:

        upstream_url = backend_service.get_upstream_url("")
        # success case
        if not exception_expected:
            assert upstream_url == "http://1.1.1.1:1000"
            mock_extract_proxy_pass.assert_called_once()
        # fail case
        else:
            assert upstream_url is None


@pytest.mark.parametrize(
    "exception_expected, proxy_pass",
    [
        (False, "http://1.1.1.1:1000/guacamole/"),
        (True, None)
    ]
)
def test_get_basekey_from_backend():
    ...



# CORE MUTATOR AND SERVICE FUNCTIONS

@pytest.mark.asyncio
async def test_create_backend():
    ...

@pytest.mark.asyncio
async def test_delete_backend():
    ...

@pytest.mark.asyncio
async def test_update_backend_authorization():
    ...



# HELPER FUNCTIONS FOR MUTATORS

@pytest.mark.asyncio
async def test_set_backend_id_and_suffix():
    ...

@pytest.mark.asyncio
async def test_delete_duplicate_backends():
    ...

@pytest.mark.asyncio
async def test_convert_backend_temp_to_out():
    ...

def test_check_backend_path_file():
    ...

def test_check_backend_path_file_naming():
    ...

def test_get_backend_path_filenames():
    ...

def test_get_valid_backend_filenames():
    ...

def test_filter_backend_filenames_by_id():
    ...

def test_build_payload_for_auth_update():
    ...