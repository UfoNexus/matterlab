from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request

from src.database import AsyncSession, get_db_session
from src.gitlab import crud as gl_crud
from src.gitlab.api import GitlabAPI
from src.gitlab.exceptions import GitlabException

from . import crud
from .models import User
from .schemas import (
    Binding,
    BindingResponse,
    Call,
    CommandRequest,
    DynamicFieldChoice,
    Expand,
    ExpandLevel,
    Form,
    FormField,
    FormFieldType,
    Location,
    Manifest,
    ReminderPeriod,
    Select,
    TextFieldSubtype,
    TopLevelBinding,
)
from .services import update_bot_access_token

router = APIRouter(prefix='/mattermost', tags=['Mattermost'])


@router.get('/manifest', response_model=Manifest, response_model_exclude_none=True, response_model_by_alias=True)
async def manifest():
    return Manifest(icon='creonit.png')


@router.post('/ping')
async def ping():
    return {'type': 'ok'}


def generate_reminder_form():
    return Form(
        title='Напомнить о сообщении',
        submit=Call(
            path='/create_reminder',
            expand=Expand(
                acting_user=ExpandLevel.summary,
                channel=ExpandLevel.summary,
                post=ExpandLevel.summary
            )
        ),
        fields=[
            FormField(
                name='interval',
                type=FormFieldType.static_select,
                is_required=True,
                label='Когда_напомнить?',
                position=1,
                multiselect=False,
                refresh=True,
                options=[
                    Select(
                        label='Через 15 минут',
                        value=ReminderPeriod.min_15
                    ),
                    Select(
                        label='Через 30 минут',
                        value=ReminderPeriod.min_30
                    ),
                    Select(
                        label='Через час',
                        value=ReminderPeriod.hour_1
                    ),
                    Select(
                        label='Через 2 часа',
                        value=ReminderPeriod.hour_2
                    ),
                    Select(
                        label='Через 4 часа',
                        value=ReminderPeriod.hour_4
                    ),
                    Select(
                        label='Указать дату и время',
                        value=ReminderPeriod.spec_datetime
                    ),

                ]
            )
        ],
        source=Call(
            path='/create_reminder_refresh'
        )
    )


@router.post(
    '/bindings', response_model=BindingResponse, response_model_exclude_none=True, response_model_by_alias=True
)
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
                            Binding(
                                label='disconnect',
                                description='Открепить профиль GitLab',
                                submit=Call(
                                    path='/disconnect_gitlab',
                                    expand=Expand(
                                        channel=ExpandLevel.id
                                    )
                                )
                            )
                        ]
                    ),
                ]
            ),
            TopLevelBinding(
                location=Location.post_menu,
                bindings=[
                    Binding(
                        location='send-button',
                        label='Напомнить мне',
                        icon=f'{str(request.base_url)}static/reminder.svg',
                        form=generate_reminder_form()
                    )
                ]
            )
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
                    description='Выбор репозитория. Для поиска введите не менее 3 символов',
                    label='Репозиторий',
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


@router.post('/connect_gitlab', response_model_exclude_none=True, response_model_by_alias=True)
async def connect_gitlab(
        data: Annotated[CommandRequest, Body()],
        bg_tasks: BackgroundTasks,
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    bg_tasks.add_task(update_bot_access_token, data.context)
    user = await crud.get_or_create_user(db_session, data.context.acting_user)
    return generate_connect_gitlab_form(user)


@router.post('/connect_gitlab_refresh', response_model_exclude_none=True, response_model_by_alias=True)
async def connect_gitlab_refresh(
        data: Annotated[CommandRequest, Body()],
        bg_tasks: BackgroundTasks,
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    bg_tasks.add_task(update_bot_access_token, data.context)
    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    gl_user = await gl_crud.get_or_create_gl_user_by_mm_user(db_session, mm_user, data.values)
    if data.values.get('access_token') and data.values['access_token'] != gl_user.access_token:
        await gl_crud.update_gl_user(db_session, gl_user, data.values)
    return generate_connect_gitlab_form(mm_user)


@router.post('/connect_gitlab_complete')
async def connect_gitlab_complete(
        data: Annotated[CommandRequest, Body()],
        request: Request,
        bg_tasks: BackgroundTasks,
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    from src.main import app

    bg_tasks.add_task(update_bot_access_token, data.context)
    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    instance = GitlabAPI(mm_user.gitlab_user.access_token)
    gl_user_schema = await instance.get_current_user()
    gl_user = await gl_crud.get_or_create_gl_user_by_mm_user(db_session, mm_user, data.values)
    await gl_crud.update_gl_user_from_schema(db_session, gl_user, gl_user_schema)
    project_schema = await instance.get_project_detail(data.values['repo']['value'])
    project = await gl_crud.get_or_create_project(db_session, project_schema)
    channel = await crud.get_or_create_channel(db_session, data.context.channel)
    await crud.add_gl_project_to_channel(db_session, channel, [project])
    base_url = str(request.base_url).strip('/')
    base_url = base_url.replace('http', request.headers.get('X-Forwarded-Proto', 'http'))
    webhook_url = base_url + app.url_path_for('gitlab_webhook')
    hooks = await instance.get_webhooks(project.id)
    urls = [str(item.url) for item in hooks]
    if webhook_url not in urls:
        await instance.create_webhook(project.id, webhook_url)
    return {'type': 'ok', 'text': f'Этот канал теперь будет получать хуки с проекта {project.path_with_namespace}'}


@router.post('/disconnect_gitlab', response_model_by_alias=True, response_model_exclude_none=True)
async def disconnect_gitlab(
        data: Annotated[CommandRequest, Body()],
        bg_tasks: BackgroundTasks
):
    bg_tasks.add_task(update_bot_access_token, data.context)
    return {
        'type': 'form',
        'form': Form(
            title='Открепить репозиторий от канала',
            submit=Call(
                path='/disconnect_gitlab_complete',
                expand=Expand(
                    channel=ExpandLevel.summary
                )
            ),
            fields=[
                FormField(
                    name='repo',
                    type=FormFieldType.dynamic_select,
                    is_required=True,
                    description='Выбор репозитория',
                    label='Репозиторий',
                    position=1,
                    lookup=Call(
                        path='/get_channel_repos',
                        expand=Expand(
                            channel=ExpandLevel.summary
                        )
                    )
                )
            ]
        )
    }


@router.post('/disconnect_gitlab_complete')
async def disconnect_gitlab_complete(
        data: Annotated[CommandRequest, Body()],
        bg_tasks: BackgroundTasks,
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    bg_tasks.add_task(update_bot_access_token, data.context)
    channel = await crud.get_or_create_channel(db_session, data.context.channel)
    project = await gl_crud.get_project_by_id(db_session, int(data.values['repo']['value']))
    await crud.delete_gl_project_from_channel(db_session, channel, project)
    return {'type': 'ok', 'text': f'Этот канал больше не будет получать хуки с проекта {data.values["repo"]["label"]}'}


@router.post('/get_repos', response_model_exclude_none=True, response_model_by_alias=True)
async def get_repos(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    mm_user = await crud.get_or_create_user(db_session, data.context.acting_user)
    if not mm_user.gitlab_user or not mm_user.gitlab_user.access_token:
        return {'type': 'error', 'text': 'Нужно сначала указать персональный токен'}
    instance = GitlabAPI(mm_user.gitlab_user.access_token)
    try:
        projects = await instance.get_projects(data.query)
    except GitlabException:
        return {'type': 'error', 'text': 'Неверный персональный токен'}
    choices = [
        DynamicFieldChoice(
            label=project.path_with_namespace, value=str(project.id_), icon_data=str(project.avatar_url)
        ) for project in projects
    ]
    return {'type': 'ok', 'data': {'items': choices}}


@router.post('/get_channel_repos', response_model_by_alias=True, response_model_exclude_none=True)
async def get_channel_repos(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    channel = await crud.get_or_create_channel(db_session, data.context.channel)
    choices = [
        DynamicFieldChoice(
            label=repo.path_with_namespace, value=str(repo.id), icon_data=str(repo.avatar_url)
        ) for repo in channel.gitlab_projects
    ]
    return {'type': 'ok', 'data': {'items': choices}}


@router.post('/create_reminder')
async def create_reminder(
        data: Annotated[CommandRequest, Body()],
        db_session: AsyncSession = Depends(get_db_session)  # noqa: B008
):
    return {
        'type': 'ok',
        'text': 'Успех'
    }


@router.post('/create_reminder_refresh')
async def create_reminder_refresh(
        data: Annotated[CommandRequest, Body()]
):
    form = generate_reminder_form()
    if data.values and data.values.get('interval', {}):
        form.fields[0].value = Select(
            label=data.values['interval']['label'],
            value=data.values['interval']['value']
        )
        if data.values['interval']['value'] == ReminderPeriod.spec_datetime:
            form.fields.append(
                FormField(
                    name='datetime',
                    type=FormFieldType.text,
                    is_required=True,
                    label='Введите_дату_и_время',
                    description='Формат: "01.01.1970 09:00" (учитывается ваш текущий часовой пояс)'
                )
            )
    return {
        'type': 'form',
        'form': form
    }
