import enum

import httpx

from src.config import settings

from . import schemas
from .exceptions import GitlabException


class GitlabAPI:
    """Интерфейс работы с API GitLab. https://docs.gitlab.com/ee/api/rest/"""

    def __init__(self, access_token: str):
        version = 'v4'
        self.base_url = f'https://gitlab.com/api/{version}'
        self.headers = {'Authorization': f'Bearer {access_token}'}

    class Endpoints(enum.StrEnum):
        list_projects = '/projects'
        get_project = '/projects/{id}'
        create_webhook = '/projects/{id}/hooks'
        list_webhooks = create_webhook
        get_current_user = '/user'

    @staticmethod
    def _parse_response(response: httpx.Response) -> dict:
        """
        Обработка ответа с API
        :param response: Объект класса Response, полученный после выполнения запроса (httpx._models.Response)
        :return: Словарь данных ответа
        """
        response_data = response.json()
        if response.status_code >= 400:
            raise GitlabException(response_data)
        return response_data

    def _get_url(self, endpoint: Endpoints) -> str:
        """
        Формирование URL запроса
        :param endpoint: объект из набора Endpoints (src.gitlab.api.GitlabAPI.Endpoints)
        :return: готовый URL
        """
        return f'{str(self.base_url)}{endpoint}'

    async def get_current_user(self) -> schemas.GitlabUser:
        """
        Получение информации о пользователе, кому принадлежит access_token
        :return: Объект схемы GitlabUser (src.gitlab.schemas.GitlabUser)
        """
        url = self._get_url(self.Endpoints.get_current_user)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        response = self._parse_response(response)
        return schemas.GitlabUser(**response)

    async def get_projects(self) -> list[schemas.ProjectAttrs]:
        """
        Получение списка активных проектов, в которых пользователь является участником
        :return: список объектов схемы ProjectAttrs (src.gitlab.schemas.ProjectAttrs)
        """
        page = 1
        per_page = 100
        result = response = []
        is_first = True
        async with httpx.AsyncClient(timeout=10) as client:
            while is_first or len(response) == per_page:
                is_first = False
                params = {
                    'archived': False,
                    'membership': True,
                    'simple': True,
                    'order_by': 'path',
                    'sort': 'asc',
                    'per_page': per_page,
                    'page': page
                }
                response = await client.get(
                    self._get_url(self.Endpoints.list_projects),
                    headers=self.headers,
                    params=params
                )
                response = self._parse_response(response)
                result.extend([schemas.ProjectAttrs(**item) for item in response])
                page += 1
        return result

    async def get_project_detail(self, project_id: int) -> schemas.ProjectAttrs:
        url = self._get_url(self.Endpoints.get_project)
        url = url.replace('{id}', str(project_id))
        async with httpx.AsyncClient() as session:
            response = await session.get(url, headers=self.headers)
        response = self._parse_response(response)
        return schemas.ProjectAttrs(**response)

    async def get_webhooks(self, project_id: int) -> list[schemas.HookData]:
        url = self._get_url(self.Endpoints.list_webhooks)
        url = url.replace('{id}', str(project_id))
        async with httpx.AsyncClient() as session:
            response = await session.get(url, headers=self.headers)
        response = self._parse_response(response)
        return [schemas.HookData(**item) for item in response]

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
        self._parse_response(response)
