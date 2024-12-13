from typing import AsyncGenerator

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# from tests.test_config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER # для тестов
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from .models import Base

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# декоратор только для pytest
# @asynccontextmanager  
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session