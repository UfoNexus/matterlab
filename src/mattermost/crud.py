from sqlalchemy.orm import Session

from . import models, schemas


# async def get_channel_by_gitlab(db: Session, gitlab_id: str) -> models.Channel | None:
#     return db.query(Channel).filter(Channel.gitlab_id == gitlab_id).first()
#
#
# async def create_channel(db: Session, channel: ChannelSchema) -> Channel:
#     db_channel = Channel(**channel.model_dump())
