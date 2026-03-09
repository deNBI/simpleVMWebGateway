import pytest
from unittest.mock import call, patch

from werkzeug.exceptions import NotFound, InternalServerError

from app.main.model.serializers import BackendIn, BackendOut, BackendTemp

from app.main.service import backend as backend_service

file_path_example_1 = "1234567890%testuser%animal_100%testtemplate%v01%0.conf"
file_path_example_2 = "9876543210%otheruser%cat_200%othertemplate%v02%1.conf"

# TEST DATA

# backend test cases: (exception_expected, filename, backend), see test_generate_backend_filename()
test_backends_for_generate_backend_filename = [
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
# backend test cases: (exception_expected, backend), see test_convert_backend_temp_to_out()
test_backends_for_convert_backend_temp_to_out = [
    (False,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (False,
     BackendTemp.model_construct(
        id = 456,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "ant_300",
        template = "anothertemplate",
        template_version = "v03",
        user_key_url = "myRstudio",
        upstream_url = "http://1.1.1.1:8002",
        auth_enabled = True,
        file_path = "another_file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = None,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = None,
        location_url = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = None,
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = None,
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = None,
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = None,
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = None,
        auth_enabled = False,
        file_path = "file_path"
        )),
    (True,
     BackendTemp.model_construct(
        id = 123,
        owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb",
        location_url = "dog_100",
        template = "testtemplate",
        template_version = "v01",
        user_key_url = "myRstudio",
        upstream_url = "http://192.168.0.1:4000",
        auth_enabled = None,
        file_path = None
        )),
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
        "app.main.service.backend.get_highest_suffix_number",
        return_value = (expected_suffix - 1) if expected_suffix else None
    ) as mock_get_highest_suffix_number:

        try:
            response_suffix: int = await backend_service.generate_suffix_number(user_key_url)
            # success case
            if not exception_expected:
                assert response_suffix == expected_suffix
                if user_key_url is not None:
                    mock_get_highest_suffix_number.assert_awaited_once()
        # fail case
        except Exception as e:
            if not exception_expected:
                raise e


@pytest.mark.parametrize(
    "expected_suffix, user_key_url, backends",
    [
        (100, "unusual_123", []),
        (123, "test_123", [BackendOut.model_construct(location_url = "test_123"), BackendOut.model_construct(location_url = "animal_100")]),
        (250, "test_250", [BackendOut.model_construct(location_url = "test_250"), BackendOut.model_construct(location_url = "animal_100")]),
        (499, "test_499", [BackendOut.model_construct(location_url = "test_499"), BackendOut.model_construct(location_url = "animal_100")])
    ]
)
@pytest.mark.asyncio
async def test_get_highest_suffix_number(expected_suffix, user_key_url, backends):

    with patch(
        "app.main.service.backend.get_backends",
        return_value = backends
    ) as mock_get_backends:
        
        highest_id = await backend_service.get_highest_suffix_number(user_key_url)
        mock_get_backends.assert_awaited_once()
        assert highest_id == expected_suffix



@pytest.mark.parametrize(
    "exception_expected, filename, backend",
    test_backends_for_generate_backend_filename
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

"""
async def test_get_backends():
"""


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



# CORE MUTATOR AND SERVICE FUNCTIONS

@pytest.mark.parametrize(
    "backend_file_contents, delete_duplicate_backends",
    [
        ("something", True),
        ("something", False),
        (None, True),
        (None, False)
    ]
)
@pytest.mark.asyncio
async def test_create_backend(backend_file_contents, delete_duplicate_backends):
    with patch(
        "app.main.config.get_settings",
    ) as mock_get_settings, patch(
        "app.main.service.backend.set_backend_id_and_suffix",
            return_value = (BackendTemp.model_construct(user_key_url="olddragon"), 100)
    ) as mock_set_backend_id_and_suffix, patch(
        "app.main.service.backend.generate_backend_by_template",
        return_value = backend_file_contents
    ) as mock_generate_backend_by_template, patch(
        "app.main.service.backend.delete_duplicate_backends",
        return_value = delete_duplicate_backends
    ) as mock_delete_duplicate_backends, patch(
        "app.main.service.backend.generate_backend_filename"
    ) as mock_generate_backend_filename, patch(
        "os.open"
    ) as mock_os_open, patch(
        "os.write"
    ) as mock_os_write, patch(
        "os.close"
    ) as mock_os_close, patch(
        "app.main.service.backend.reload_openresty"
    ) as mock_reload_openresty:
        backend_in = BackendIn(
            owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb7",
            template = "theiaide",
            template_version = "v03",
            auth_enabled = True,
            user_key_url = "olddragon",
            upstream_url = "http://192.168.0.1:8787/guacamole/"
        )
        try:
            result = await backend_service.create_backend(backend_in)
            # mock_get_settings.assert_called_once()
            mock_set_backend_id_and_suffix.assert_awaited_once()
            mock_generate_backend_by_template.assert_awaited_once()
            mock_delete_duplicate_backends.assert_awaited_once()
            mock_generate_backend_filename.assert_called_once()
            # mock_os_open.assert_called_once()
            # mock_os_write.assert_called_once()
            # mock_os_close.assert_called_once() @ reviewer: these 4 mocks are not called
            mock_reload_openresty.assert_awaited_once()
            assert result.location_url == "olddragon_100"
        except Exception as e:
            assert not backend_file_contents or not delete_duplicate_backends


@pytest.mark.parametrize(
    "exception_expected, backend_path_filenames, matching_backend_filenames",
    [
        (False, [file_path_example_1, file_path_example_2], [file_path_example_1]),
        (False, [file_path_example_1, file_path_example_2], [file_path_example_2]),
        (True, [file_path_example_1, file_path_example_2], []),
        (True, [], []),
        (True, [file_path_example_2], [])
    ]
)
@pytest.mark.asyncio
async def test_delete_backend(exception_expected, backend_path_filenames, matching_backend_filenames):
    with patch(
        "app.main.config.get_settings"
    ) as mock_get_settings, patch(
        "app.main.service.backend.get_valid_backend_filenames",
        return_value = backend_path_filenames
    ) as mock_get_valid_backend_filenames, patch(
        "app.main.service.backend.filter_backend_filenames_by_id",
        return_value = matching_backend_filenames
    ) as mock_filter_backend_filenames_by_id, patch(
        "os.remove"
    ) as mock_os_remove, patch(
        "app.main.service.backend.reload_openresty"
    ) as mock_reload_openresty:

        try:
            number_of_files = len(matching_backend_filenames)
            result = await backend_service.delete_backend(0) # backend_id irrelevant due to mocks
            # mock_get_settings.assert_called_once()
            mock_get_valid_backend_filenames.assert_called_once()
            mock_filter_backend_filenames_by_id.assert_called_once()
            mock_os_remove.assert_called_once()
            mock_reload_openresty.assert_awaited_once()
            assert result is True
        except NotFound as e:
            assert exception_expected and (not backend_path_filenames or number_of_files == 0)
        except InternalServerError as e:
            assert exception_expected and backend_path_filenames and number_of_files != 1
        except OSError as e:
            assert exception_expected and (not backend_path_filenames or number_of_files == 0)
        except Exception as e:
            raise e


@pytest.mark.parametrize(
    "exception_expected, auth_enable, get_backend, temp_payload, new_contents, returning_backend",
    [
        (False, True, True, True, True, True),
        (False, False, True, True, True, True),
        (True, True, False, True, True, True),
        (True, True, True, False, True, True),
        (True, True, True, True, False, True),
        (True, True, True, True, True, False)
    ]
)
@pytest.mark.asyncio
async def test_update_backend_authorization(exception_expected, auth_enable, get_backend, temp_payload, new_contents, returning_backend):
    with patch(
        "app.main.service.backend.get_backend_by_id",
        return_value = BackendOut.model_construct(location_url="test_100") if get_backend else None
    ) as mock_get_backend_by_id, patch(
        "app.main.service.backend.build_payload_for_auth_update",
        return_value = BackendIn.model_construct() if temp_payload else None
    ) as mock_build_payload_for_auth_update, patch(
        "app.main.service.backend.create_backend",
        return_value = BackendTemp.model_construct() if new_contents else None
    ) as mock_create_backend, patch(
        "app.main.service.backend.convert_backend_temp_to_out",
        return_value = BackendOut.model_construct() if returning_backend else None
    ) as mock_convert_backend_temp_to_out:

        result = await backend_service.update_backend_authorization(0, auth_enable) # backend_id irrelevant due to mocks
        if not exception_expected:
            mock_get_backend_by_id.assert_awaited_once_with(0)
            mock_build_payload_for_auth_update.assert_called_once_with(mock_get_backend_by_id.return_value, auth_enable)
            mock_create_backend.assert_awaited_once_with(mock_build_payload_for_auth_update.return_value, id='0', location_url='test_100')
            mock_convert_backend_temp_to_out.assert_awaited_once_with(mock_create_backend.return_value)
            assert result == mock_convert_backend_temp_to_out.return_value
        else:
            assert result is None



# HELPER FUNCTIONS FOR MUTATORS

@pytest.mark.parametrize(
    "exception_expected, kwargs",
    [
        # SUCCESS CASES
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
    "exception_expected, backend",
    test_backends_for_convert_backend_temp_to_out
)
@pytest.mark.asyncio
async def test_convert_backend_temp_to_out(exception_expected, backend):
    with patch(
        "app.main.service.backend.get_backend_by_id",
        return_value = BackendOut.model_construct(file_path = backend.file_path)
    ) as mock_get_backend_by_id:
        try: # @reviewer: is there an easier way?
            backend_out = await backend_service.convert_backend_temp_to_out(backend)
            if not exception_expected:
                assert isinstance(backend_out, BackendOut)
                mock_get_backend_by_id.assert_awaited_once_with(backend.id)
                assert backend_out.id == backend.id
                assert backend_out.owner == backend.owner
                assert backend_out.location_url == backend.location_url
                assert backend_out.template == backend.template
                assert backend_out.template_version == backend.template_version
                assert backend_out.auth_enabled == backend.auth_enabled
                assert backend_out.file_path == backend.file_path
        except Exception as e:
            if not exception_expected:
                raise e


@pytest.mark.parametrize(
        "expected, path_exists, access, listdir",
        [
            (True, True, True, ["first"]),
            (True, True, True, ["first", "second"]),
            (True, True, True, ["first", "second", "third"]),
            (False, False, False, ["first"]),
            (False, False, True, ["first"]),
            (False, True, False, ["first"]),
            (False, True, True, []),

        ]
)
def test_check_backend_path(expected, path_exists, access, listdir):

    with patch(
        "app.main.service.backend.get_settings" # imported
    ) as mock_get_settings, patch(
        "os.path.exists",
        return_value = path_exists
    ) as mock_os_path_exists, patch(
        "os.access",
        return_value = access
    ) as mock_os_access, patch(
        "os.listdir",
        return_value = listdir
    ) as mock_os_listdir:
        assert backend_service.check_backend_path() == expected
        mock_get_settings.assert_called_once()
        mock_os_path_exists.assert_called_once()
        if path_exists:
            mock_os_access.assert_called_once()
            if access:
                mock_os_listdir.assert_called_once()


@pytest.mark.parametrize(
    "expected, filename",
    [
        (True, file_path_example_1),
        (True, file_path_example_2),
        (False, "users"),
        (False, "scripts"),
        (False, "obviously_wrong"),
        (False, 37)
    ]
)
def test_check_backend_file_naming(expected, filename):
    try:
        assert backend_service.check_backend_file_naming(filename) is expected
    except TypeError as e:
        assert not expected
        if expected:
            raise e

@pytest.mark.parametrize(
    "returning, backend_check",
    [
        (["something"], True),
        (None, False)
    ]
)
def test_get_backend_path_filenames(returning, backend_check):

    with patch(
        "app.main.service.backend.get_settings" # imported
    ) as mock_get_settings, patch(
        "app.main.service.backend.check_backend_path",
        return_value = backend_check
    ) as mock_check_backend_path, patch(
        "os.listdir",
        return_value = returning
    ) as mock_os_listdir:
        assert backend_service.get_backend_path_filenames() == returning
        mock_check_backend_path.assert_called_once()
        if backend_check:
            mock_os_listdir.assert_called_once()
            mock_get_settings.assert_called_once()


@pytest.mark.parametrize(
    "filenames, naming_check",
    [
        ([file_path_example_1, file_path_example_2], True),
        (["invalid_file_1", "invalid_file_2"], False),
        (["users", "scripts"], False),
        ([], False)
    ]
)
def test_get_valid_backend_filenames(filenames, naming_check):

    with patch(
        "app.main.service.backend.get_backend_path_filenames",
        return_value = filenames
    ) as mock_get_backend_path_filenames, patch(
        "app.main.service.backend.check_backend_file_naming",
        return_value = naming_check
    ) as mock_check_backend_file_naming:

        expected = None
        if filenames:
            expected = filenames if naming_check else []
            
        assert backend_service.get_valid_backend_filenames() == expected

        mock_get_backend_path_filenames.assert_called_once()
        if filenames:
            mock_check_backend_file_naming.assert_called()


@pytest.mark.parametrize(
    "backend_id, filenames, expected",
    [
        (1234567890, [file_path_example_1, file_path_example_2], [file_path_example_1]),
        (9876543210, [file_path_example_1, file_path_example_2], [file_path_example_2]),
        (None, [], [])
    ]
)
def test_filter_backend_filenames_by_id(backend_id, filenames, expected):
    assert backend_service.filter_backend_filenames_by_id(filenames, backend_id) == expected


@pytest.mark.parametrize(
    "exception_expected, upstream_url, base_key, auth_enabled",
    [
        (False, "http://192.168.0.1:8787/guacamole/", "olddragon", True),
        (False, "http://192.168.0.1:4000/guacamole/", "youngmonkey", False),
        (True, None, "crazydog", True),
        (True, "http://192.168.0.1:1000/", None, False),
        (True, "http://192.168.0.1:1234/", "test_100", None)
    ]
)
def test_build_payload_for_auth_update(exception_expected, upstream_url, base_key, auth_enabled):
    with patch(
        "app.main.service.backend.get_upstream_url",
        return_value = upstream_url
    ) as mock_get_upstream_url, patch(
        "app.main.service.backend.get_basekey_from_backend",
        return_value = base_key
    ) as mock_get_basekey_from_backend:
        backend: BackendOut = BackendOut(
            owner = "4d2e5e17-a378-4df0-ba9e-4fb710f0eeb7",
            template = "theiaide",
            template_version = "v03",
            auth_enabled = True,
            id = 3872943384,
            location_url = "tropicalantelope_100",
            file_path = "3872943384%4d2e5e17-a378-4df0-ba9e-4fb710f0eeb7%tropicalantelope_100%theiaide%v03%1.conf"
            )

        result = backend_service.build_payload_for_auth_update(backend, auth_enabled)
        mock_get_upstream_url.assert_called_once_with(backend.file_path)
        mock_get_basekey_from_backend.assert_called_once_with(backend)
        if not upstream_url or not base_key or exception_expected:
            assert result is None
            return
        
        assert isinstance(result, BackendIn)
        assert result.owner == backend.owner
        assert result.template == backend.template
        assert result.template_version == backend.template_version
        assert result.user_key_url == base_key
        assert result.upstream_url == upstream_url
        assert result.auth_enabled == auth_enabled
