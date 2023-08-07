from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Header

from src.config import settings
from .schemas import WebHook
from .services import parse_webhook

router = APIRouter(prefix='/gitlab', tags=['GitLab'])


@router.post("/webhook", summary='Обработка вебхуков с GitLab')
async def webhook(
        x_gitlab_token: Annotated[str, Header()],
        data: Annotated[WebHook, Body()],
        bg_tasks: BackgroundTasks
):
    """
    Присутствует обработка следующих хуков:

    - pipeline events
    """
    if x_gitlab_token != settings.gitlab_secret:
        print('Несанкционированный доступ')
        return
    bg_tasks.add_task(parse_webhook, data)
