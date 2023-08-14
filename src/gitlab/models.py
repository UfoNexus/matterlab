from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from src.database import Model
from src.mattermost.models import Channel, GitlabProjectChannel, User


class Project(Model):
    __tablename__ = 'gitlab_project'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    web_url: Mapped[str] = mapped_column(unique=True, index=True)
    path_with_namespace: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    mattermost_channels: Mapped[list['Channel']] = relationship(
        back_populates='gitlab_projects', secondary='gitlab_project_mattermost_channel'
    )
    mattermost_channel_associations: Mapped[list['GitlabProjectChannel']] = relationship(
        back_populates='gitlab_project'
    )


class GitlabUser(Model):
    __tablename__ = 'gitlab_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    iid: Mapped[int | None] = mapped_column(unique=True, nullable=True)
    name: Mapped[str | None] = mapped_column(nullable=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    access_token: Mapped[str] = mapped_column(index=True)

    mattermost_user: Mapped['User'] = relationship(back_populates='gitlab_user')
