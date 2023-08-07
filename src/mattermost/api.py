import enum

import requests

from src.config import settings


class MattermostAPI:

    def __init__(self):
        self.base_url = settings.mattermost_host
        self.headers = {'Authorization': f'Bearer {settings.mattermost_bot_auth_token}'}

    class Endpoints(enum.StrEnum):
        create_post = 'api/v4/posts'

    def _get_url(self, endpoint: str):
        return f'{str(self.base_url)}{endpoint}'

    async def create_post(self, channel_id: str, content: str):
        data = {
            'channel_id': channel_id,
            'message': content
        }
        response = requests.post(self._get_url(self.Endpoints.create_post), json=data, headers=self.headers)
        print(response)
        print(response.json())
