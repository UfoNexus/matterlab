import enum

import httpx

from src.config import settings


class MattermostAPI:

    def __init__(self):
        self.base_url = f'{settings.mattermost_host}api/v4'
        self.headers = {'Authorization': f'Bearer {settings.mattermost_bot_auth_token}'}

    class Endpoints(enum.StrEnum):
        create_post = '/posts'

    def _get_url(self, endpoint: str) -> str:
        return f'{str(self.base_url)}{endpoint}'

    async def create_post(self, channel_id: str, content: str):
        data = {
            'channel_id': channel_id,
            'message': content
        }
        async with httpx.AsyncClient() as session:
            await session.post(self._get_url(self.Endpoints.create_post), json=data, headers=self.headers)
