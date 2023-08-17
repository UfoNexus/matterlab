from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    local: bool = False

    db_host: str = 'localhost'
    db_port: int = 5432
    db_user: str
    db_password: str
    
    redis_host: str = 'localhost'
    redis_port: int = 6379

    gitlab_secret: str

    mattermost_host: HttpUrl
    mattermost_app_root_url: HttpUrl | None = Field(default=None)

    @property
    def db_url(self) -> str:
        return f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres'

    @property
    def db_async_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres'
    
    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}/0'


settings = Settings()
