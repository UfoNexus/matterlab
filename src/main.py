import os

from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

from src.gitlab.routers import router as gitlab_router

from .config import settings

app = FastAPI(
    debug=os.getenv('DEBUG', False),
    title='Matterlab',
    version='0.0.1',
    docs_url='/openapi'
)
app.openapi_version = '3.0.3'

if settings.local:
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=['debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel'],
    )

# Роутеры
app.include_router(gitlab_router)
