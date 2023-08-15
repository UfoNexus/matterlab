from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.mattermost import models as mm_models

from . import models, schemas


async def get_or_create_project(session: Session, project_data: schemas.ProjectAttrs) -> models.Project:
    result = await session.scalars(select(models.Project).where(models.Project.id == project_data.id_).options(
        selectinload(models.Project.mattermost_channels)))
    project = result.first()
    if not project:
        project = models.Project(**project_data.model_dump(mode='json', by_alias=True))
        session.add(project)
        await session.commit()  # noqa
        await session.refresh(project)  # noqa
    return project


async def get_project_by_id(session: Session, project_id: int) -> models.Project:
    result = await session.scalars(select(models.Project).where(models.Project.id == project_id).options(
        selectinload(models.Project.mattermost_channels)))
    project = result.first()
    if not project:
        raise ValueError('Проект не найден')
    return project


async def get_or_create_gl_user_by_mm_user(session: Session, mm_user: mm_models.User, data: dict) -> models.GitlabUser:
    gl_user = mm_user.gitlab_user
    if gl_user:
        gl_user: models.GitlabUser
        return gl_user
    gl_user = models.GitlabUser(access_token=data['access_token'], mattermost_user=mm_user)
    session.add(gl_user)
    await session.commit()  # noqa
    await session.refresh(gl_user)  # noqa
    return gl_user


async def update_gl_user(session: Session, user: models.GitlabUser, data: dict) -> models.GitlabUser:
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()  # noqa
    await session.refresh(user)  # noqa
    return user


async def update_gl_user_from_schema(
        session: Session, user: models.GitlabUser, schema: schemas.GitlabUser
) -> models.GitlabUser:
    is_changed = False
    if user.iid != schema.id_:
        user.iid = schema.id_
        is_changed = True
    if user.name != schema.name:
        user.name = schema.name
        is_changed = True
    if user.username != schema.username:
        user.username = schema.username
        is_changed = True
    if not is_changed:
        return user
    session.add(user)
    await session.commit()  # noqa
    await session.refresh(user)  # noqa
    return user
