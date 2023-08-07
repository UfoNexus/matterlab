from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from src.database import Model

if TYPE_CHECKING:
    from src.gitlab.models import Project


class Channel(Model):
    __tablename__ = 'mattermost_channel'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]

    gitlab_projects: Mapped[list['Project']] = relationship(
        back_populates='mattermost_channels', secondary='gitlab_project_mattermost_channel'
    )
    gitlab_project_associations: Mapped[list['GitlabProjectChannel']] = relationship(
        back_populates='mattermost_channel'
    )


class GitlabProjectChannel(Model):
    __tablename__ = 'gitlab_project_mattermost_channel'

    gitlab_project_id: Mapped[int] = mapped_column(ForeignKey('gitlab_project.id'), primary_key=True)
    mattermost_channel_id: Mapped[int] = mapped_column(ForeignKey('mattermost_channel.id'), primary_key=True)

    gitlab_project: Mapped['Project'] = relationship(back_populates='mattermost_channel_associations')
    mattermost_channel: Mapped['Channel'] = relationship(back_populates='gitlab_project_associations')
