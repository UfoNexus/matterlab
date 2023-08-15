from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models

if TYPE_CHECKING:
    from . import schemas
    from src.gitlab import models as gl_models


async def get_or_create_user(session: Session, user: 'schemas.User') -> models.User:
    result = await session.scalars(select(models.User).where(models.User.id == user.id_).options(
        selectinload(models.User.gitlab_user)
    ))
    user_obj = result.first()
    if not user_obj:
        user_obj = models.User(**user.model_dump(mode='json', by_alias=True))
        session.add(user_obj)
        await session.commit()  # noqa
        await session.refresh(user_obj)  # noqa
    return user_obj


async def get_or_create_channel(
        session: Session, channel: 'schemas.Channel', gl_projects: list['gl_models.Project'] | None = None
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


async def add_gl_project_to_channel(
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


async def delete_gl_project_from_channel(
        session: Session, channel: models.Channel, gl_project: 'gl_models.Project'
) -> models.Channel:
    channel.gitlab_projects.remove(gl_project)
    session.add(channel)
    await session.commit()  # noqa
    await session.refresh(channel)  # noqa
    return channel


async def get_last_bot(session: Session) -> models.Bot:
    result = await session.scalars(select(models.Bot))
    bot_obj = result.last()
    if not bot_obj:
        raise ValueError('Бот не создан')
    return bot_obj


async def get_or_create_bot(session: Session, bot: 'schemas.CommandRequestContext') -> tuple[models.Bot, bool]:
    result = await session.scalars(select(models.Bot).where(models.Bot.iid == bot.bot_user_id))
    bot_obj = result.first()
    created = False
    if not bot_obj:
        bot_obj = models.Bot(
            **bot.model_dump(mode='json', include={'bot_user_id', 'bot_access_token'}, by_alias=True)
        )
        session.add(bot_obj)
        await session.commit()  # noqa
        await session.refresh(bot_obj)  # noqa
        created = True
    return bot_obj, created


async def update_bot(session: Session, bot: models.Bot, data: 'schemas.CommandRequestContext') -> models.Bot:
    for key, value in data.model_dump(mode='json', include={'bot_user_id', 'bot_access_token'}, by_alias=True).items():
        setattr(bot, key, value)
    session.add(bot)
    await session.commit()  # noqa
    await session.refresh(bot)  # noqa
    return bot
