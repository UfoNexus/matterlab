import os

from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.openapi.utils import get_openapi

from src.gitlab.routers import router as gitlab_router

from .config import settings

app = FastAPI(debug=os.getenv('DEBUG', False))

app.add_middleware(
    DebugToolbarMiddleware,
    panels=['debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel']
)
if not settings.local:
    app.add_middleware(HTTPSRedirectMiddleware)

# Роутеры
app.include_router(gitlab_router)


# Настройка OpenAPI
def custom_openapi():
    openapi_schema = get_openapi(
        title='Matterlab',
        version='0.0.1',
        openapi_version='3.0.3',
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
