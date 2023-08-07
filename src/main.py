import os

from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.gitlab.routers import router as gitlab_router

app = FastAPI(debug=os.getenv('DEBUG', False))

app.add_middleware(DebugToolbarMiddleware)

# Роутеры
app.include_router(gitlab_router)


# Настройка OpenAPI
def custom_openapi():
    openapi_schema = get_openapi(
        title='Matterlab',
        version='0.1.0',
        openapi_version='3.0.3',
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
