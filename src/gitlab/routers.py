from typing import Annotated

from fastapi import APIRouter, Body, Header

from src.config import settings
from .schemas import WebHook

router = APIRouter(prefix='/gitlab', tags=['GitLab'])


@router.post("/webhook", summary='Обработка вебхуков с GitLab')
async def webhook(
        x_gitlab_token: Annotated[str, Header()],
        data: Annotated[WebHook, Body()]
):
    """
    Присутствует обработка следующих хуков:

    - pipeline events
    """
    print(data.model_dump(mode='json'))
    if x_gitlab_token != settings.gitlab_secret:
        print('Несанкционированный доступ')
        return
