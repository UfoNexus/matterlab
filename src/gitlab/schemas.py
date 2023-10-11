from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Source(StrEnum):
    """Триггеры pipeline"""
    push = 'push'
    web = 'web'


class Status(StrEnum):
    """Статусы билда"""
    success = 'success'
    warning = 'warning'
    failed = 'failed'
    pending = 'pending'
    created = 'created'
    running = 'running'
    canceled = 'canceled'


class ObjectAttrs(BaseModel):
    """Аттрибуты объекта оповещения"""
    id_: int = Field(title='ID', alias='id')
    iid: int = Field(title='ID внутри проекта')
    ref: str = Field(title='Название ветки')
    source: Source = Field(title='Триггер pipeline')
    status: Status = Field(title='Статус')
    url: HttpUrl = Field(title='Ссылка на pipeline')


class ProjectAttrs(BaseModel):
    """Аттрибуты проекта/репозитория"""
    model_config = ConfigDict(from_attributes=True)

    id_: int = Field(title='ID', alias='id')
    name: str = Field(title='Название репы')
    web_url: HttpUrl = Field(title='Ссылка')
    path_with_namespace: str | None = Field(default=None, title='Обозначение репы')
    avatar_url: HttpUrl | None = Field(default=None, title='Аватар')


class CommitAttrs(BaseModel):
    """Аттрибуты коммита"""
    id_: str = Field(title='sha коммита', alias='id')
    title: str = Field(title='Текст коммита')
    url: HttpUrl = Field(title='Ссылка')


class Build(BaseModel):
    """Job у pipeline"""
    stage: str
    name: str = Field(title='Название')
    status: Status = Field(title='Статус')
    allow_failure: bool = Field(default=False, title='Ошибки не вызывают отмену сборки')


# noinspection PyNestedDecorators
class GitlabUser(BaseModel):
    """Пользователь GitLab"""
    id_: int = Field(title='ID', alias='id')
    name: str = Field(title='Имя')
    username: str
    avatar_url: HttpUrl = Field(title='Аватарка')
    email: str | None

    @field_validator('email')
    @classmethod
    def parse_email(cls, value, info):
        if value == '[REDACTED]':
            value = None
        return value


# noinspection PyNestedDecorators
class WebHook(BaseModel):
    """Объект оповещения"""
    object_kind: str = Field(title='Тип оповещения', examples=['pipeline'])
    builds: list[Build]
    object_attributes: ObjectAttrs
    user: GitlabUser
    project: ProjectAttrs
    commit: CommitAttrs

    @field_validator('object_attributes')
    @classmethod
    def validate_pipeline_status(cls, value, info):
        if value.status == Status.success:
            for build in info.data['builds']:
                if build.status == Status.failed and build.allow_failure:
                    value.status = Status.warning
                    break
        return value

    @property
    def failed_job(self) -> Build | None:
        failed = list(filter(lambda item: item.status == Status.failed and not item.allow_failure, self.builds))
        if len(failed) == 0:
            return
        return failed[0]

    @property
    def allowed_failed_job(self) -> Build | None:
        allowed_fail = list(filter(lambda item: item.status == Status.failed and item.allow_failure, self.builds))
        if len(allowed_fail) == 0:
            return
        return allowed_fail[0]


class HookData(BaseModel):
    """Хук, подключенный на проекте"""
    url: HttpUrl
    project_id: int
    pipeline_events: bool
