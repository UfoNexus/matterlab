from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Header

from src.database import AsyncSession
from src.database import get_db_session
from src.gitlab import crud as gl_crud
from src.gitlab.api import GitlabAPI
from src.gitlab.exceptions import GitlabException
from . import crud
from .models import User
from .schemas import (
    Binding,
    BindingResponse,
    Call,
    Channel,
    CommandRequest,
    DynamicFieldChoice,
    Expand,
    ExpandLevel,
    Form,
    FormField,
    FormFieldType,
    Location,
    Manifest,
    TextFieldSubtype,
    TopLevelBinding
)

router = APIRouter(prefix='/mattermost', tags=['Mattermost'])


@router.get('/manifest', response_model=Manifest, response_model_exclude_none=True)
async def manifest():
    return Manifest()


@router.post('/ping')
async def ping():
    return {'type': 'ok'}


@router.post('/bindings', response_model=BindingResponse, response_model_exclude_none=True)
async def bindings(request: Request):
    return BindingResponse(
        data=[
            TopLevelBinding(
                location=Location.command,
                bindings=[
                    Binding(
                        label='matterlab',
                        icon=f'{str(request.base_url)}static/creonit.png',
                        description='Управление связкой с gitlab',
                        hint='[command]',
                        bindings=[
                            Binding(
                                label='connect',
                                description='Привязать профиль GitLab',
                                submit=Call(
                                    path='/connect_gitlab',
                                    expand=Expand(
                                        acting_user=ExpandLevel.summary,
                                        channel=ExpandLevel.summary
                                    )
                                )
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )


def generate_connect_gitlab_form(user: User) -> dict:
    access_token_default = None
    if user.gitlab_user:
        access_token_default = user.gitlab_user.access_token
    return {
        'type': 'form',
        'form': Form(
            title='Прикрепление репозитория к каналу',
            submit=Call(
                path='/connect_gitlab_complete',
                expand=Expand(
                    acting_user=ExpandLevel.id,
                    channel=ExpandLevel.summary
                )
            ),
            fields=[
                FormField(
                    name='access_token',
                    type=FormFieldType.text,
                    is_required=True,
                    label='personal_access_token',
                    description='Персональный токен Gitlab',
                    refresh=True,
                    value=access_token_default,
                    subtype=TextFieldSubtype.input,
                    position=1
                ),
                FormField(
                    name='repo',
                    type=FormFieldType.dynamic_select,
                    is_required=True,
                    description='Выбор репозитория',
                    label='repo',
                    position=2,
                    lookup=Call(
                        path='/get_repos',
                        expand=Expand(
                            acting_user=ExpandLevel.summary
                        )
                    )
                )
            ],
            source=Call(
                path='/connect_gitlab_refresh',
                expand=Expand(
                    acting_user=ExpandLevel.summary
                )
            ),
            header='Для прикрепления репозитория к каналу нужно один раз создать и указать персональный токен доступа '
                   'к профилю GitLab. Создать его можно так:\n'
                   '1. Быть авторизованным на gitlab.com и перейти по ссылке '
                   'https://gitlab.com/-/profile/personal_access_tokens\n'
                   '2. Жмакаем "Add new token"\n'
                   '3. Поле "Token name" заполняем как угодно\n'
                   '4. Поле "Expiration date" заполняем любой датой в будущем (не больше, чем на 1 год)\n'
                   '5. Среди чекбоксов выбираем "api" и "read_user"\n'
                   '6. Жмем на кнопку "Create personal access token"\n'
                   '7. Копируем токен и вставляем в поле формы\n'
        )
    }


@router.post('/connect_gitlab')
async def connect_gitlab(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)
):
    user = await crud.get_or_create_user(db_session, data.context.acting_user)
    return generate_connect_gitlab_form(user)


@router.post('/connect_gitlab_refresh')
async def connect_gitlab_refresh(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)
):
    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    gl_user = await gl_crud.get_or_create_gl_user_by_mm_user(db_session, mm_user, data.values)
    if data.values.get('access_token') and data.values['access_token'] != gl_user.access_token:
        await gl_crud.update_gl_user(db_session, gl_user, data.values)
    return generate_connect_gitlab_form(mm_user)


@router.post('/connect_gitlab_complete')
async def connect_gitlab_complete(
        data: Annotated[CommandRequest, Body()],
        request: Request,
        # headers: Annotated[dict, Header()],
        db_session: AsyncSession = Depends(get_db_session)
):
    from src.main import app

    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    instance = GitlabAPI(mm_user.gitlab_user.access_token)
    gl_user_schema = await instance.get_current_user()
    gl_user = await gl_crud.get_or_create_gl_user_by_mm_user(db_session, mm_user, data.values)
    await gl_crud.update_gl_user_from_schema(db_session, gl_user, gl_user_schema)
    project_schema = await instance.get_project_detail(data.values['repo']['value'])
    project = await gl_crud.get_or_create_project(db_session, project_schema)
    channel = await crud.get_or_create_channel(db_session, data.context.channel)
    await crud.attach_gl_project_to_channel(db_session, channel, [project])
    base_url = str(request.base_url).strip('/')
    base_url = base_url.replace('http', request.headers.get('X-Forwarded-Proto', 'http'))
    webhook_url = base_url + app.url_path_for('gitlab_webhook')
    hooks = await instance.get_webhooks(project.id)
    urls = [item.url for item in hooks]
    if webhook_url not in urls:
        await instance.create_webhook(project.id, webhook_url)
    return {'type': 'ok', 'text': f'Этот канал теперь будет получать хуки с проекта {project.path_with_namespace}'}


@router.post('/get_repos')
async def get_repos(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)
):
    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    if not mm_user.gitlab_user or not mm_user.gitlab_user.access_token:
        return {'type': 'error', 'text': 'Нужно сначала указать персональный токен'}
    instance = GitlabAPI(mm_user.gitlab_user.access_token)
    try:
        projects = await instance.get_projects()
    except GitlabException:
        return {'type': 'error', 'text': 'Неверный персональный токен'}
    choices = [
        DynamicFieldChoice(
            label=project.path_with_namespace, value=str(project.id), icon_data=str(project.avatar_url)
        ) for project in projects
    ]
    return {'type': 'ok', 'data': {'items': choices}}
