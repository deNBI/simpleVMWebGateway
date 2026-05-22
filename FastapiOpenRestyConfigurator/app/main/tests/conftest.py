import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def test_dirs(tmp_path_factory):
    """
    See config.get_settings(). Creates the path structure and sets environment variables.
    """
    backend = tmp_path_factory.mktemp("backend")
    templates = tmp_path_factory.mktemp("templates")

    os.environ["FORC_BACKEND_PATH"] = str(backend)
    os.environ["FORC_TEMPLATE_PATH"] = str(templates)
    os.environ["FORC_API_KEY"] = "test-api-key"

    yield
