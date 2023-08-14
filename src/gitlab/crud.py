from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from src.mattermost.models import User as MMUser

from .models import GitlabUser, Project
from .schemas import GitlabUser as GitlabUserSchema, ProjectAttrs as ProjectSchema


async def get_or_create_project(session: Session, project_data: ProjectSchema) -> Project:
    result = await session.scalars(select(Project).where(Project.id == project_data.id).options(
        selectinload(Project.mattermost_channels)))
    project = result.first()
    if not project:
        project = Project(**project_data.model_dump(mode='json'))
        session.add(project)
        await session.commit()  # noqa
        await session.refresh(project)  # noqa
    return project


async def get_or_create_gl_user_by_mm_user(session: Session, mm_user: MMUser, data: dict) -> GitlabUser:
    gl_user = mm_user.gitlab_user
    if gl_user:
        gl_user: GitlabUser
        return gl_user
    gl_user = GitlabUser(access_token=data['access_token'], mattermost_user=mm_user)
    session.add(gl_user)
    await session.commit()  # noqa
    await session.refresh(gl_user)  # noqa
    return gl_user


async def update_gl_user(session: Session, user: GitlabUser, data: dict) -> GitlabUser:
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()  # noqa
    await session.refresh(user)  # noqa
    return user


async def update_gl_user_from_schema(session: Session, user: GitlabUser, schema: GitlabUserSchema) -> GitlabUser:
    is_changed = False
    if user.iid != schema.id:
        user.iid = schema.id
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
