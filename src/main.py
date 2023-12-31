from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.gitlab.routers import router as gitlab_router
from src.mattermost.routers import router as mattermost_router

from .config import settings

app = FastAPI(
    debug=settings.debug,
    title='Matterlab',
    version='0.0.1',
    docs_url='/openapi'
)
app.openapi_version = '3.0.3'
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/mattermost/static', StaticFiles(directory='static'), name='mm_static')

# Роутеры
app.include_router(gitlab_router)
app.include_router(mattermost_router)
