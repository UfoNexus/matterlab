import enum

import httpx

from src.config import settings
from . import schemas
from .exceptions import GitlabException


class GitlabAPI:

    def __init__(self, access_token: str):
        self.base_url = 'https://gitlab.com/api/v4'
        self.headers = {'Authorization': f'Bearer {access_token}'}

    class Endpoints(enum.StrEnum):
        list_projects = '/projects'
        get_project = '/projects/{id}'
        create_webhook = '/projects/{id}/hooks'
        get_current_user = '/user'

    def _get_url(self, endpoint: str) -> str:
        return f'{str(self.base_url)}{endpoint}'

    async def get_current_user(self) -> schemas.GitlabUser:
        async with httpx.AsyncClient() as client:
            response = await client.get(self._get_url(self.Endpoints.get_current_user), headers=self.headers)
        if response.status_code >= 400:
            raise GitlabException
        response = response.json()
        return schemas.GitlabUser(**response)

    async def get_projects(self) -> list[schemas.ProjectAttrs]:
        page = 1
        per_page = 100
        result = response = []
        is_first = True
        async with httpx.AsyncClient() as client:
            while is_first or len(response) == per_page:
                is_first = False
                params = {
                    'archived': False,
                    'membership': True,
                    'simple': True,
                    'order_by': 'name',
                    'sort': 'asc',
                    'per_page': per_page,
                    'page': page
                }
                response = await client.get(
                    self._get_url(self.Endpoints.list_projects),
                    headers=self.headers,
                    params=params
                )
                if response.status_code >= 400:
                    raise GitlabException
                response = response.json()
                result.extend([schemas.ProjectAttrs(**item) for item in response])
                page += 1
        return result

    async def get_project_detail(self, project_id: int) -> schemas.ProjectAttrs:
        url = self._get_url(self.Endpoints.get_project)
        url = url.replace('{id}', str(project_id))
        async with httpx.AsyncClient() as session:
            response = await session.get(url, headers=self.headers)
        if response.status_code >= 400:
            raise GitlabException
        response = response.json()
        return schemas.ProjectAttrs(**response)

    async def create_webhook(self, project_id: int, webhook_url: str) -> None:
        url = self._get_url(self.Endpoints.create_webhook)
        url = url.replace('{id}', str(project_id))
        data = {
            'url': webhook_url,
            'enable_ssl_verification': False,
            'pipeline_events': True,
            'push_events': False,
            'token': settings.gitlab_secret
        }
        async with httpx.AsyncClient() as session:
            response = await session.post(url, headers=self.headers, json=data)
        if response.status_code >= 400:
            raise GitlabException(response.json())
