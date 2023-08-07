from src.database import AsyncSession
from src.mattermost.api import MattermostAPI
from src.mattermost.services import prepare_message

from .crud import get_project_by_id
from .schemas import Status, WebHook


async def parse_webhook(data: WebHook):
    if data.object_attributes.status not in [Status.success, Status.warning, Status.failed]:
        return
    async with AsyncSession() as session:
        project = await get_project_by_id(session, data.project.id)
        channels = project.mattermost_channels
    message = await prepare_message(data)
    instance = MattermostAPI()
    for channel in channels:
        await instance.create_post(channel.id, message)
