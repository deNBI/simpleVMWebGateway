import pytest
from unittest.mock import call, patch

from app.main.model.serializers import BackendIn, BackendOut, BackendTemp

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
    (False, "456%otheruser%ant_300%anothertemplate%v03%1.conf",
     BackendOut.model_construct(
        id = 456,
        owner = "otheruser",
        location_url = "ant_300",
        template = "anothertemplate",
        template_version = "v03",
        auth_enabled = True
        )),
    (True, None,
     BackendOut.model_construct(
        id = None,
        owner = "otheruser",
        location_url = "cat_200",
        template = "othertemplate",
        template_version = "v02",
        auth_enabled = True
        )),
    (True, None,
     BackendOut.model_construct(
        id = 123,
        owner = None,
        location_url = "cat_200",
        template = "othertemplate",
        template_version = "v02",
        auth_enabled = True
        )),
    (True, None,
     BackendOut.model_construct(
        id = 123,
        owner = "otheruser",
        location_url = None,
        template = "othertemplate",
        template_version = "v02",
        auth_enabled = True
        )),
    (True, None,
     BackendOut.model_construct(
        id = 123,
        owner = "otheruser",
        location_url = "cat_200",
        template = None,
        template_version = "v02",
        auth_enabled = True
        )),
    (True, None,
     BackendOut.model_construct(
        id = 123,
        owner = "otheruser",
        location_url = "cat_200",
        template = "othertemplate",
        template_version = None,
        auth_enabled = True
        )),
    (True, None,
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
    "exception_expected, expected_suffix, user_key_url",
    [
        (False, 100, None),
        (False, 201, "test_200"),
        (True, None, "test_-10"),
        (True, None, "test_999"),
        (True, None, "test_1000"),
        (True, None, "test_150.5"),
        (True, None, "test_not-an-int")
    ]
)
@pytest.mark.asyncio
async def test_generate_suffix_number(exception_expected, expected_suffix, user_key_url):

    with patch(
        "app.main.service.backend.get_backends",
        return_value = [BackendOut.model_construct(location_url = user_key_url), BackendOut.model_construct(location_url = "animal_100")]
    ) as mock_get_backends:

        try:
            response_suffix: int = await backend_service.generate_suffix_number(user_key_url)
            # success case
            if not exception_expected:
                assert response_suffix == expected_suffix
                if user_key_url is not None:
                    mock_get_backends.assert_awaited_once()
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e


@pytest.mark.parametrize(
    "exception_expected, filename, backend",
    test_backends
)
@pytest.mark.asyncio
async def test_generate_backend_filename(exception_expected, filename, backend):
    try:
        response_filename: str = backend_service.generate_backend_filename(backend)
        # success case
        if not exception_expected:
            assert response_filename == filename
    # fail case
    except Exception as e:
        if not exception_expected:
            raise e



# CORE GETTER FUNCTIONS

# TODO: async def test_get_backends():


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
        return_value = [BackendOut.model_construct(id = backend_id), BackendOut.model_construct(id = 456)]
    ) as mock_get_backends:

        try:
            response_backend: BackendOut = await backend_service.get_backend_by_id(backend_id)
            # success case
            if not exception_expected:
                assert response_backend.id == backend_id
                mock_get_backends.assert_awaited_once()
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e



# FURTHER GETTER FUNCTIONS

@pytest.mark.parametrize(
    "exception_expected, proxy_pass, expected_upstream_url",
    [
        (False, "http://1.1.1.1:1000/guacamole/", "http://1.1.1.1:1000"),
        (False, "http://200.100.50.10:4200/other/", "http://200.100.50.10:4200"),
        (True, None, None)
    ]
)
@pytest.mark.asyncio
async def test_get_upstream_url(exception_expected, proxy_pass, expected_upstream_url):

    with patch(
        "app.main.service.backend.extract_proxy_pass",
        return_value = proxy_pass
    ) as mock_extract_proxy_pass:

        response_upstream_url = backend_service.get_upstream_url("test_path")
        mock_extract_proxy_pass.assert_called_once()

        # success case
        if not exception_expected:
            assert response_upstream_url == expected_upstream_url
        # fail case
        else:
            assert response_upstream_url is None


@pytest.mark.parametrize(
    "exception_expected, backend, expected_basekey",
    [
        (False, BackendOut.model_construct(location_url = "test_100"), "test"),
        (False, BackendOut.model_construct(location_url = "example_200"), "example"),
        (True, BackendOut.model_construct(location_url = "corrupted"), None),
        (True, BackendOut.model_construct(location_url = "123"), None),
        (True, None, None)
    ]
)
def test_get_basekey_from_backend(exception_expected, backend, expected_basekey):

    response_basekey = backend_service.get_basekey_from_backend(backend)
    # success case
    if not exception_expected:
        assert response_basekey == expected_basekey
    # fail case
    else:
        assert response_basekey is None


"""
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
"""



# HELPER FUNCTIONS FOR MUTATORS

@pytest.mark.parametrize(
    "exception_expected, kwargs",
    [
        # SUCESS CASES
        (False, {}),
        (False, {"id": 123, "location_url": "test_200"}),
        # FAIL CASES
        # one param is missing
        (True, {"id": 123}),
        (True, {"location_url": "test_200"}),
        # required param is None
        (True, {"id": None, "location_url": "test_200"}),
        (True, {"id": 123, "location_url": None}),
        # wrong type param
        (True, {"id": "not-an-int", "location_url": "test_200"}),
        (True, {"id": 123, "location_url": 111})
    ]
)
@pytest.mark.asyncio
async def test_set_backend_id_and_suffix(exception_expected, kwargs):
    with patch(
        "app.main.service.backend.generate_suffix_number",
    ) as mock_generate_suffix_number:

        try:
            backend, suffix_number = await backend_service.set_backend_id_and_suffix(BackendTemp.model_construct(), **kwargs)
            backend: BackendTemp
            suffix_number: int
            # success case
            if not exception_expected:
                assert backend.id
                assert suffix_number
                if kwargs == {}:
                    mock_generate_suffix_number.assert_awaited_once()
                else:
                    mock_generate_suffix_number.assert_not_awaited()
                    assert int(backend.id) == int(kwargs["id"])
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e


@pytest.mark.parametrize(
    "delete_succeeded, proxy_pass, expected_delete_backend_ids",
    [
        (True, "http://192.168.0.1:8787/guacamole/", [12, 34]),
        (True, "http://192.168.0.1:8787", [56, 78]),
        (False, "http://192.168.0.1:8787", [56, 78]),
        (True, "http://1.1.1.1:4000", [])
    ]
        # not able to test cases like None, "", "not_valid" without a validator, TODO: can we use serializer.BackendIn validator?
)
@pytest.mark.asyncio
async def test_delete_duplicate_backends(delete_succeeded, proxy_pass, expected_delete_backend_ids):
    with patch(
        "app.main.service.backend.get_backends_proxy_pass",
        return_value = {
            "http://192.168.0.1:8787/guacamole/": [
                BackendOut.model_construct(
                    id = 12,
                    upstream_url = "http://192.168.0.1:8787/guacamole/",
                ),
                BackendOut.model_construct(
                    id = 34,
                    upstream_url = "http://192.168.0.1:8787/guacamole/",
                ),
            ],
            "http://192.168.0.1:8787": [
                BackendOut.model_construct(
                    id = 56,
                    upstream_url = "http://192.168.0.1:8787",
                ),
                BackendOut.model_construct(
                    id = 78,
                    upstream_url = "http://192.168.0.1:8787",
                ),
            ],
            "http://1.1.1.1:4000": [
                BackendOut.model_construct(
                    id = 90,
                    upstream_url = "http://1.1.1.1:4000/",
                ),
            ],
        }
    ) as mock_get_backends_upstream_urls, patch(
        "app.main.service.backend.delete_backend",
        return_value = delete_succeeded
    ) as mock_delete_backend:

        response_success: bool = await backend_service.delete_duplicate_backends(BackendIn.model_construct(upstream_url = proxy_pass))
        mock_get_backends_upstream_urls.assert_awaited_once()
        # success case
        if delete_succeeded:
            assert response_success is True
            if len(expected_delete_backend_ids) != 0:
                mock_delete_backend.assert_has_awaits(
                    [call(backend_id=id) for id in expected_delete_backend_ids],
                    any_order = True
                )
        # fail case
        elif not delete_succeeded:
            assert response_success is False
            mock_delete_backend.assert_awaited()


@pytest.mark.parametrize(
    "exception_expected, filename, backend",
    test_backends
)
@pytest.mark.asyncio
async def test_convert_backend_temp_to_out(exception_expected, backend):
    with patch(
        "app.main.service.backend.get_backend_by_id",
        return_value = BackendOut.model_construct(file_path = "test_path")
    ) as mock_get_backend_by_id:

        backend_out: BackendOut = await backend_service.convert_backend_temp_to_out(backend)












"""
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
"""