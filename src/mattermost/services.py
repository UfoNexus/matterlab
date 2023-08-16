import os
from typing import TYPE_CHECKING

from mdutils import MdUtils

from src.config import settings
from src.database import AsyncSession
from src.gitlab.schemas import Status, WebHook

from . import crud

if TYPE_CHECKING:
    from .schemas import CommandRequestContext

color_status_match = {
    Status.success: 'brightgreen',
    Status.failed: 'ff0000',
    Status.warning: 'yellow'
}


async def prepare_message(data: WebHook) -> str:
    md_file = MdUtils(file_name='mattermost_message')

    # Значки со статусом pipeline и ссылкой на репу
    badge_url = (
        f'https://img.shields.io/badge/build-{data.object_attributes.status}-'
        f'{color_status_match[data.object_attributes.status]}?logo=gitlab'
    )
    repo_badge_url = f'https://img.shields.io/badge/repository-{data.project.name.replace("-", "--")}-white'
    md_file.new_line(
        md_file.new_inline_image("gitlab build badge", badge_url) +
        md_file.new_inline_link(str(data.project.web_url), md_file.new_inline_image('gitlab repo badge', repo_badge_url))
    )

    # Информация о пользователе, запустившего сборку
    md_file.new_line(
        f'{md_file.new_inline_image("user avatar", str(data.user.avatar_url) + " =x25")} '
        f'**{data.user.name} ({data.user.username})**'
    )

    # Инфо о pipeline
    md_file.new_line(
        f'**Статус '
        f'{md_file.new_inline_link(str(data.object_attributes.url), f"Pipeline #{data.object_attributes.iid}")}** - '
        f'{data.object_attributes.status}'
    )

    table_data = []

    # Данные о коммите и ветке
    branch_url = str(data.project.web_url) + "/-/tree/" + data.object_attributes.ref
    branch = (
        f'**Ветка: **'
        f'{md_file.new_inline_link(branch_url, data.object_attributes.ref)}&emsp;&emsp;&emsp;'
    )
    commit = (
        f'**Коммит: **'
        f'{md_file.new_inline_link(str(data.commit.url), data.commit.title)}'
    )
    table_data.extend([branch, commit])

    # Опциональные данные о провале сборке или с допущенными ошибками
    failed_job = data.failed_job or data.allowed_failed_job
    if data.object_attributes.status in [Status.failed, Status.warning] and failed_job:
        stage = f'**Ошибка в стейдже: **{failed_job.stage}&emsp;&emsp;&emsp;'
        job = f'**Ошибка в задаче: **{failed_job.name}'
        table_data.extend([stage, job])

    columns = 2
    md_file.new_line()
    md_file.new_table(columns=columns, rows=round(len(table_data) / columns), text=table_data, text_align='left')

    md_file.file_data_text = md_file.file_data_text.lstrip(' \n')
    return md_file.file_data_text


def get_root_url():
    if host := os.getenv('CI_ENVIRONMENT_DOMAIN'):
        return f'https://{host}/mattermost'
    return settings.mattermost_app_root_url or 'http://localhost'


async def update_bot_access_token(data: 'CommandRequestContext') -> None:
    async with AsyncSession() as session:
        bot, created = await crud.get_or_create_bot(session, data)
        if created:
            return
        await crud.update_bot(session, bot, data)
