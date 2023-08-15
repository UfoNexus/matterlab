from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models, schemas

if TYPE_CHECKING:
    from src.gitlab import models as gl_models


async def get_or_create_user(session: Session, user: schemas.User) -> models.User:
    result = await session.scalars(select(models.User).where(models.User.id == user.id).options(
        selectinload(models.User.gitlab_user)
    ))
    user_obj = result.first()
    if not user_obj:
        user_obj = models.User(**user.model_dump(mode='json'))
        session.add(user_obj)
        await session.commit()  # noqa
        await session.refresh(user_obj)  # noqa
    return user_obj


async def get_or_create_channel(
        session: Session, channel: schemas.Channel, gl_projects: list['gl_models.Project'] | None = None
) -> models.Channel:
    result = await session.scalars(select(models.Channel).where(models.Channel.iid == channel.iid).options(
        selectinload(models.Channel.gitlab_projects)
    ))
    channel_obj = result.first()
    if not channel_obj:
        channel_obj = models.Channel(**channel.model_dump(mode='json'))
        if gl_projects:
            channel_obj.gitlab_projects.extend(gl_projects)
        session.add(channel_obj)
        await session.commit()  # noqa
        await session.refresh(channel_obj)  # noqa
    return channel_obj


async def attach_gl_project_to_channel(
        session: Session, channel: models.Channel, gl_projects: list['gl_models.Project']
) -> models.Channel:
    result = await session.scalars(select(models.Channel).where(models.Channel.id == channel.id).options(
        selectinload(models.Channel.gitlab_projects)
    ))
    channel = result.first()
    channel.gitlab_projects.extend(gl_projects)
    session.add(channel)
    await session.commit()  # noqa
    await session.refresh(channel)  # noqa
    return channel
