from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from src.database import Model
from src.mattermost.models import Channel, GitlabProjectChannel


class Project(Model):
    __tablename__ = 'gitlab_project'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    url: Mapped[str] = mapped_column(unique=True, index=True)

    mattermost_channels: Mapped[list['Channel']] = relationship(
        back_populates='gitlab_projects', secondary='gitlab_project_mattermost_channel'
    )
    mattermost_channel_associations: Mapped[list['GitlabProjectChannel']] = relationship(
        back_populates='gitlab_project'
    )
