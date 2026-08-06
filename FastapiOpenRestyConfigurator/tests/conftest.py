import pytest
import os

from .factories.backendOutFactory import build_backend_out

@pytest.fixture(scope="session", autouse=True)
def test_dirs(tmp_path_factory):
    backend = tmp_path_factory.mktemp("backend")
    templates = tmp_path_factory.mktemp("templates")

    os.environ["FORC_BACKEND_PATH"] = str(backend)
    os.environ["FORC_TEMPLATE_PATH"] = str(templates)
    os.environ["FORC_API_KEY"] = "test-api-key"

    yield


@pytest.fixture
def backend_out_factory():
    """
    Returns a callable factory.
    """
    return build_backend_out
