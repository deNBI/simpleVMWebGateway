import pytest
from app.main.views import utils as utils_views

@pytest.mark.asyncio
async def test_get_health():
    response = await utils_views.get_health()
    assert response == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_version():
    response = await utils_views.get_version()
    assert response.version is not None
