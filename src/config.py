from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    local: bool = False

    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str

    gitlab_secret: str

    mattermost_host: HttpUrl
    mattermost_bot_auth_token: str

    @property
    def db_url(self) -> str:
        return f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres'
    
    @property
    def db_async_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres'


settings = Settings()
