from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_engine(settings.db_url, echo=settings.debug)
SyncSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(settings.db_async_url, echo=settings.debug)
AsyncSession = async_sessionmaker(async_engine, expire_on_commit=False)


class Model(AsyncAttrs, DeclarativeBase):
    pass


async def get_db_session():
    session = AsyncSession()
    try:
        yield session
    finally:
        await session.close()
