from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import AsyncSession

from .models import Project


async def get_project_by_id(session: AsyncSession, project_id: int) -> Project:
    result = await session.scalars(select(Project).where(Project.id == project_id).options(
        selectinload(Project.mattermost_channels)))
    project = result.first()
    if not project:
        raise ValueError('Проект с указанным ID не найден')
    return project
