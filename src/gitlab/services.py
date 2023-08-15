from src.database import AsyncSession
from src.mattermost import crud as mm_crud
from src.mattermost.api import MattermostAPI
from src.mattermost.services import prepare_message

from . import crud
from .schemas import Status, WebHook


async def parse_webhook(data: WebHook):
    if data.object_attributes.status not in [Status.success, Status.warning, Status.failed]:
        return
    async with AsyncSession() as session:
        project = await crud.get_or_create_project(session, data.project)
        print(project)
        channels = project.mattermost_channels
        print(channels)
        bot = await mm_crud.get_last_bot(session)
        print(bot)
    message = await prepare_message(data)
    print(message)
    instance = MattermostAPI(bot.access_token)
    for channel in channels:
        await instance.create_post(channel.id, message)
