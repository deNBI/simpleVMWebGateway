from fastapi import FastAPI
from logging.config import dictConfig

from app.main.model.serializers import tags_metadata
from app.main.util.logging import log_config
from app.main.views.backend import router as backend_router
from app.main.views.template import router as template_router
from app.main.views.user import router as user_router
from app.main.views.utils import router as util_router

# Apply logging config
dictConfig(log_config)


# Apply tags metadata for openapi and create app
app = FastAPI(openapi_tags=tags_metadata)

# Apply routes
app.include_router(backend_router)
app.include_router(template_router)
app.include_router(user_router)
app.include_router(util_router)
