from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from src.database import Model

if TYPE_CHECKING:
    from src.gitlab.models import GitlabUser, Project


class User(Model):
    __tablename__ = 'mattermost_user'

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    email: Mapped[str | None] = mapped_column(nullable=True)

    gitlab_user_id: Mapped[int | None] = mapped_column(ForeignKey('gitlab_user.id'))
    gitlab_user: Mapped['GitlabUser'] = relationship(back_populates='mattermost_user')


class Channel(Model):
    __tablename__ = 'mattermost_channel'

    id: Mapped[int] = mapped_column(primary_key=True)
    iid: Mapped[str]
    name: Mapped[str]
    display_name: Mapped[str | None] = mapped_column(nullable=True)

    gitlab_projects: Mapped[list['Project']] = relationship(
        back_populates='mattermost_channels', secondary='gitlab_project_mattermost_channel',
        sa_relationship_kwargs={'lazy': 'selectin'}
    )
    gitlab_project_associations: Mapped[list['GitlabProjectChannel']] = relationship(
        back_populates='mattermost_channel', sa_relationship_kwargs={'lazy': 'selectin'}
    )


class GitlabProjectChannel(Model):
    __tablename__ = 'gitlab_project_mattermost_channel'

    gitlab_project_id: Mapped[int] = mapped_column(ForeignKey('gitlab_project.id'), primary_key=True)
    mattermost_channel_id: Mapped[int] = mapped_column(ForeignKey('mattermost_channel.id'), primary_key=True)

    gitlab_project: Mapped['Project'] = relationship(
        back_populates='mattermost_channel_associations', sa_relationship_kwargs={'lazy': 'selectin'}
    )
    mattermost_channel: Mapped['Channel'] = relationship(
        back_populates='gitlab_project_associations', sa_relationship_kwargs={'lazy': 'selectin'}
    )
